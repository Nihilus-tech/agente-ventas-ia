from flask import Flask, render_template, request, jsonify
import os
import logging
import warnings
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from langchain.memory import ConversationBufferWindowMemory
from collections import defaultdict

# Memoria por sesión
memorias = defaultdict(lambda: ConversationBufferWindowMemory(
    k=5,
    return_messages=True,
    memory_key="chat_history"
))

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()
os.environ["HF_TOKEN"] = "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"

app = Flask(__name__)


from flask_login import LoginManager, login_required
from database import db, Usuario
from auth import auth

app.config['SECRET_KEY'] = 'clave_secreta_segura_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agente_ventas.db'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.register_blueprint(auth)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(correo='admin@go4more.com').first():
        admin = Usuario(
            nombre='Admin',
            correo='admin@go4more.com',
            numero_whatsapp=None,
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuario admin creado")


print("Cargando base de conocimiento...")
# 1. Cargamos el modelo de embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

# 2. Optimizamos la carga para que no se te congele por la CPU
if os.path.exists("vectorstore"):
    print("-> Base de datos vectorial existente encontrada. Cargando en memoria...")
    vectordb = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
else:
    print("-> No se encontró vectorstore. Generando base de datos por bloques...")
    import time
    loader = DirectoryLoader("Transcripciones", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    fragmentos = splitter.split_documents(docs)
    
    db = None
    for i in range(0, len(fragmentos), 50):
        lote = fragmentos[i:i+50]
        if db is None:
            vectordb = Chroma.from_documents(lote, embeddings, persist_directory="vectorstore")
        else:
            vectordb.add_documents(lote)
        print(f"   Procesados {min(i+50, len(fragmentos))}/{len(fragmentos)} fragmentos...")
        time.sleep(1) # Un respiro para que no se ahogue tu procesador


llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
prompt = ChatPromptTemplate.from_template("""
Eres un asistente experto en ventas de cursos de inglés de GO4MORE.
Tu objetivo es ayudar a los ejecutivos de ventas a redactar mensajes 
efectivos para sus prospectos.

Usa el siguiente contexto de los talleres y plantillas de GO4MORE:
{context}

Con base en eso, ayuda al ejecutivo a:
- Redactar mensajes personalizados para sus prospectos
- Aplicar técnicas de venta de GO4MORE
- Conseguir el número del interesado
- Concretar citas o videollamadas
- Rescatar ventas perdidas

Si el contexto no tiene información suficiente, usa tu conocimiento 
general de ventas para sugerir un mensaje efectivo, pero siempre 
manteniendo el tono y estilo de GO4MORE.

Situación del ejecutivo: {input}
""")
chain = create_stuff_documents_chain(llm, prompt)
retriever = vectordb.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.3,
        "k": 3
    }
)
agente = create_retrieval_chain(retriever, chain)

def clasificar_prospecto(texto):
    texto = texto.lower()
    if any(p in texto for p in ['comentó', 'comento', 'publicación', 'publicacion', 'grupo']):
        return 'comentó_publicación'
    elif any(p in texto for p in ['busca', 'buscando', 'quiere', 'interesado', 'su publicación']):
        return 'publicación_propia'
    elif any(p in texto for p in ['agregado', 'contacto', 'agregué', 'agregue']):
        return 'contacto_agregado'
    elif any(p in texto for p in ['rescatar', 'perdido', 'no contestó', 'frío', 'frio']):
        return 'rescate'
    else:
        return 'general'

@app.route('/consultar', methods=['POST'])
@login_required
def consultar():
    import time
    from flask_login import current_user
    from database import Consulta

    datos = request.json
    consulta_texto = datos.get('consulta', '')
    session_id = datos.get('session_id', 'default')

    inicio = time.time()

    memoria = memorias[session_id]
    historial = memoria.load_memory_variables({})

    respuesta = agente.invoke({
        "input": consulta_texto,
        "chat_history": historial.get("chat_history", [])
    })



    memoria.save_context(
        {"input": consulta_texto},
        {"output": respuesta['answer']}
    )

    tiempo = round((time.time() - inicio) * 1000)

    nueva_consulta = Consulta(
        usuario_id=current_user.id,
        consulta=consulta_texto,
        respuesta=respuesta['answer'],
        tiempo_ms=tiempo,
        canal='web',
        tipo_prospecto=clasificar_prospecto(consulta_texto)
    )
    db.session.add(nueva_consulta)
    db.session.commit()

    return jsonify({
        "respuesta": respuesta['answer'],
        "tiempo_ms": tiempo
    })


@app.route('/historial')
@login_required
def historial():
    from database import Consulta
    from flask_login import current_user
    consultas = Consulta.query.filter_by(usuario_id=current_user.id).order_by(Consulta.fecha.desc()).limit(50).all()
    return render_template('historial.html', usuario=current_user, consultas=consultas)

@app.route('/')
@login_required
def index():
    from database import Consulta
    from flask_login import current_user
    from datetime import datetime, date
    
    hoy = date.today()
    consultas_hoy = Consulta.query.filter(
        Consulta.usuario_id == current_user.id,
        db.func.date(Consulta.fecha) == hoy
    ).count()
    
    tiempo_promedio = db.session.query(
        db.func.avg(Consulta.tiempo_ms)
    ).filter(
        Consulta.usuario_id == current_user.id
    ).scalar()
    
    ultimas_consultas = Consulta.query.filter_by(
        usuario_id=current_user.id
    ).order_by(Consulta.fecha.desc()).limit(5).all()
    
    return render_template('dashboard.html',
        consultas_hoy=consultas_hoy,
        tiempo_promedio=round(tiempo_promedio or 0),
        ultimas_consultas=ultimas_consultas,
        usuario=current_user
    )

@app.route('/agente')
@login_required
def agente_page():
    # Usamos directamente la sesión activa de Flask-Login pasando 'usuario'
    from flask_login import current_user
    return render_template('index.html', usuario=current_user)


@app.route('/metricas')
@login_required
def metricas():
    from database import Consulta, Usuario
    from flask_login import current_user
    from datetime import datetime, timedelta
    
    es_admin = current_user.correo == 'admin@go4more.com'
    
    # Consultas por día últimos 7 días
    hoy = datetime.utcnow().date()
    consultas_por_dia = []
    labels_dias = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        if es_admin:
            count = Consulta.query.filter(
                db.func.date(Consulta.fecha) == dia
            ).count()
        else:
            count = Consulta.query.filter(
                Consulta.usuario_id == current_user.id,
                db.func.date(Consulta.fecha) == dia
            ).count()
        consultas_por_dia.append(count)
        labels_dias.append(dia.strftime('%d/%m'))
    
    # Tipos de prospecto
    if es_admin:
        tipos = db.session.query(
            Consulta.tipo_prospecto,
            db.func.count(Consulta.id)
        ).group_by(Consulta.tipo_prospecto).all()
        
        consultas_por_ejecutivo = db.session.query(
            Usuario.nombre,
            db.func.count(Consulta.id)
        ).join(Consulta, Usuario.id == Consulta.usuario_id)\
         .group_by(Usuario.nombre).all()
    else:
        tipos = db.session.query(
            Consulta.tipo_prospecto,
            db.func.count(Consulta.id)
        ).filter(
            Consulta.usuario_id == current_user.id
        ).group_by(Consulta.tipo_prospecto).all()
        consultas_por_ejecutivo = []
    
    # Horas pico
    if es_admin:
        horas = db.session.query(
            db.func.strftime('%H', Consulta.fecha),
            db.func.count(Consulta.id)
        ).group_by(db.func.strftime('%H', Consulta.fecha)).all()
    else:
        horas = db.session.query(
            db.func.strftime('%H', Consulta.fecha),
            db.func.count(Consulta.id)
        ).filter(
            Consulta.usuario_id == current_user.id
        ).group_by(db.func.strftime('%H', Consulta.fecha)).all()
    
    return render_template('metricas.html',
        consultas_por_dia=consultas_por_dia,
        labels_dias=labels_dias,
        tipos=tipos,
        consultas_por_ejecutivo=consultas_por_ejecutivo,
        es_admin=es_admin,
        usuario=current_user
    )



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
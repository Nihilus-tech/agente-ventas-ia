from flask import Flask, render_template, request, jsonify
import os
import logging
import warnings
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"] = "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"

app = Flask(__name__)

print("Cargando base de conocimiento...")
loader = DirectoryLoader("Transcripciones", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
fragmentos = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

if os.path.exists("vectorstore"):
    db = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
else:
    db = Chroma.from_documents(fragmentos, embeddings, persist_directory="vectorstore")

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
prompt = ChatPromptTemplate.from_template("""
Eres un agente experto en ventas de cursos de ingles.
Usa el siguiente contexto para responder:
{context}
Pregunta: {input}
""")
chain = create_stuff_documents_chain(llm, prompt)
agente = create_retrieval_chain(db.as_retriever(), chain)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar', methods=['POST'])
def consultar():
    datos = request.json
    consulta = datos.get('consulta', '')
    respuesta = agente.invoke({"input": consulta})
    return jsonify({"respuesta": respuesta['answer']})

if __name__ == '__main__':
    app.run(debug=True)
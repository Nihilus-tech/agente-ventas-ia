import os
import logging
import warnings
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

os.environ["GROQ_API_KEY"] = "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"

print("Cargando base de conocimiento...")
loader = DirectoryLoader("Transcripciones", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
fragmentos = splitter.split_documents(docs)

from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"})
import time
import os

if os.path.exists("vectorstore"):
    print("Cargando base existente...")
    db = Chroma(persist_directory="vectorstore", embedding_function=embeddings)
else:
    print("Creando base nueva...")
    db = None
    for i in range(0, len(fragmentos), 50):
        lote = fragmentos[i:i+50]
        if db is None:
            db = Chroma.from_documents(lote, embeddings, persist_directory="vectorstore")
        else:
            db.add_documents(lote)
        print(f"Procesados {min(i+50, len(fragmentos))}/{len(fragmentos)} fragmentos...")
        time.sleep(2)

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7)
prompt = ChatPromptTemplate.from_template("""
Eres un agente experto en ventas de cursos de ingles.
Usa el siguiente contexto para responder:
{context}
Pregunta: {input}
""")
chain = create_stuff_documents_chain(llm, prompt)
agente = create_retrieval_chain(db.as_retriever(), chain)

print("Agente listo. Escribe tu consulta:")
print("(escribe salir para terminar)\n")

while True:
    consulta = input("Tu: ")
    if consulta.lower() == "salir":
        break
    respuesta = agente.invoke({"input": consulta})
    print(f"\nAgente: {respuesta['answer']}\n")
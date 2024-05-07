import os
from dotenv import load_dotenv, find_dotenv
from pinecone import Pinecone, PodSpec, ServerlessSpec
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import datetime
import glob

""" Modelo de ChatBot que responde a preguntas sobre documentos de texto."""

# Find .env
load_dotenv(find_dotenv(), override=True)

class ChatBot:
    def __init__(self, files= ["data/ATM-PRC-DS-01 Procedimiento Planificación de Proyectos.docx", "data/ATM-PRC-DS-02 Procedimiento Gestión y Seguimiento de Proyectos.docx", "data/ATM-PRC-DS-03 Procedimiento de Gestión de Riesgos y Oportunidades.docx"]):
        # Modificar el bucle principal para permitir al usuario especificar múltiples archivos como entrada
        archivos = files
        documentos = self._cargar_documentos(archivos)
        self.fragmentos = self._fragmentar(documentos)
        print(f"El Número de fragmentos es de: {len(self.fragmentos)} fragmentos")
        self._borrar_indices("todos")
        index_name = 'cupcake'
        self.vectores = self._creando_vectores(index_name, self.fragmentos)
        self.mode = "w"
        self.nuevo_chat()
        
    # Borrar los índices de Pinecone
    def _borrar_indices(self, index_name='todos'):

        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'), environment='eu-west1-gcp')
        
        if index_name == 'todos':
            indexes = pc.list_indexes()
            print('Borrando todos los índices ... ')
            for index in indexes:
                pc.delete_index(index.name)
            print('Listo!')
        else:
            print(f'Borrando el índice: {index_name} ...', end='')
            pc.delete_index(index_name)
            print('Listo')

    # Modificar la función cargar_documento para cargar múltiples archivos
    def _cargar_documentos(self, archivos):
        documentos = []
        for archivo in archivos:
            nombre, extension = os.path.splitext(archivo)
            if extension == '.pdf':
                print(f'Cargando {archivo}...')
                loader = PyPDFLoader(archivo)
            elif extension == '.docx':
                print(f'Cargando {archivo}...')
                loader = Docx2txtLoader(archivo)
            else:
                print(f'El formato del documento {archivo} no está soportado!')
                continue

            data = loader.load()
            documentos.append(data)
        return documentos

    # Modificar la función fragmentar para fragmentar los datos de todos los documentos
    def _fragmentar(self, documentos, chunk_size=150):
        fragmentos_totales = []
        for data in documentos:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
            fragmentos = text_splitter.split_documents(data)
            fragmentos_totales.extend(fragmentos)
        return fragmentos_totales

    # Modificar la función creando_vectores para crear vectores y subirlos a Pinecone con los fragmentos de todos los documentos
    def _creando_vectores(self, index_name, fragmentos):
        embeddings = OpenAIEmbeddings()

        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'), environment='us-east-1')

        if index_name in pc.list_indexes():
            print(f'El índice {index_name} ya existe. Cargando los embeddings ... ', end='')
            vectores = Pinecone.from_existing_index(index_name, embeddings)
            print('Ok')
        else:
            print(f'Creando el índice {index_name} y los embeddings ...', end='')
            pc.create_index(index_name, dimension=1536, metric='cosine', spec= ServerlessSpec(cloud="aws", region="us-east-1")) #PodSpec(environment="gcp-starter"))
            vectores = PineconeVectorStore.from_documents(fragmentos, embeddings, index_name=index_name)
            print('Ok')

        return vectores

    # Responder a una pregunta del usuario
    def _consulta(self, vectores, pregunta, recordar=True):
        llm = ChatOpenAI(temperature=0.7)
        retriever = vectores.as_retriever(search_type='similarity', search_kwargs={'k': 3})
        
        crc = ConversationalRetrievalChain.from_llm(llm, retriever)
        respuesta = crc({'question': pregunta, 'chat_history': self.memoria})
        if recordar:
            self.memoria.append((pregunta, respuesta['answer']))
        self._guardar_chat(respuesta)
        
        return respuesta
    
    # Crear un nuevo chat
    def _crear_nuevo_chat(self):
        # Get today's date
        today = datetime.date.today()

        # Create the new file
        new_file_name = self.get_new_chat_filename(today)
            
        return new_file_name
    
    # Guardar un par (pregunta, respuesta) en un archivo
    def _guardar_chat(self, interaccion):
        with open(self.current_chat, self.mode, encoding="utf-8") as file:
                interaccion_json = f'\n{{"question": "{interaccion["question"]}","answer": "{interaccion["answer"]}"}}' if self.mode == "a" else f'{{"question": "{interaccion["question"]}","answer": "{interaccion["answer"]}"}}'
                file.write(interaccion_json)
        self.mode = "a"
    
    # Devuelve el nombre de archivo que le correspondería a un nuevo chat
    def get_new_chat_filename(self, date):
        # Check if there is already a file with today's date
        existing_files = glob.glob(f"history/{date}*.txt")

        if existing_files:
            # Get the last index
            last_index = max([int(file.split("-")[-1].split(".")[0]) for file in existing_files])
            new_index = last_index + 1
        else:
            new_index = 1
        return f"history/{date}-{new_index}.txt"
    
    # Función pública para responder a una pregunta
    def responder(self, pregunta):
        respuesta = self._consulta(vectores=self.vectores, pregunta=pregunta)
        return respuesta['answer']
    
    # Crear un nuevo chat
    def nuevo_chat(self):
        self.mode = "w"
        self.memoria = []
        self.current_chat = self._crear_nuevo_chat()
    
    # Cargar un chat antiguo para responder preguntas sobre ese chat
    def cargar_chat(self, filename, chats):
        self.mode = "a"
        self.memoria = chats
        self.current_chat = filename
        
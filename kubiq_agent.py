import streamlit as st
import os

from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="KUBIQ - Asistente Interno",
    page_icon="🤖",
    layout="wide"
)

# Inicializamos variables en el session_state para mantener los datos durante la recarga de Streamlit
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

# --- UI: Barra lateral ---
st.sidebar.title("🏢 KUBIQ Configuración")

st.sidebar.markdown("El documento base ya está integrado en el sistema.")

# Obtenemos la API Key oculta desde las variables de entorno
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    st.sidebar.error("⚠️ Faltan credenciales: No se encontró COHERE_API_KEY en el archivo .env")

## Definimos la ruta local de tu archivo PDF (Asegúrate de que este archivo exista en tu carpeta)
PDF_PATH = "politicas_kubiq.pdf"
st.sidebar.info(f"📄 Documento fuente: **{PDF_PATH}**")

def process_pdf(file_path, api_key):
    """Procesa el PDF local, lo divide en fragmentos y crea la base de datos vectorial (FAISS)"""
    try:
        # Validar si el archivo existe localmente
        if not os.path.exists(file_path):
            st.error(f"⚠️ No se encontró el archivo '{file_path}'. Asegúrate de colocarlo en la misma carpeta que el script.")
            return None

        # 1. Cargar el documento directamente desde la ruta local
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 2. Dividir el documento en fragmentos (Chunks)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)

        # 3. Crear Embeddings y almacenarlos en FAISS
        embeddings = CohereEmbeddings(cohere_api_key=api_key, model="embed-multilingual-v3.0")
        
        # Generar y almacenar vectores
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        return vector_store
        
    except Exception as e:
        st.error(f"Error al procesar el documento: {str(e)}")
        return None

# Carga automática del documento sin requerir interacción del usuario
if not st.session_state.pdf_processed and cohere_api_key:
    with st.sidebar:
        with st.spinner(f"Analizando y vectorizando {PDF_PATH} en segundo plano..."):
            vector_store = process_pdf(PDF_PATH, cohere_api_key)
            if vector_store:
                st.session_state.vector_store = vector_store
                st.session_state.pdf_processed = True

# Indicador visual de estado en el sidebar
if st.session_state.pdf_processed:
    st.sidebar.success("✅ Base de conocimiento activa y lista")

# --- UI: Área principal ---
st.title("🤖 Asistente KUBIQ para Empleados")
st.markdown("Pregunta sobre las políticas de privacidad, devoluciones, envíos y normativas internas.")

# Mensaje mientras el agente carga o si falta la API Key
if not st.session_state.pdf_processed:
    st.warning("⏳ Inicializando el cerebro del agente... por favor espera.")

# Mostrar el historial de chat iterando sobre la sesión
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario (solo habilitada si el PDF ya fue procesado)
if prompt := st.chat_input("Escribe tu pregunta sobre las políticas de KUBIQ...", disabled=not st.session_state.pdf_processed):
    
    # 1. Agregar pregunta del usuario al historial y mostrarla
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Buscando en los archivos de KUBIQ..."):
            try:
                # Configurar el LLM de Cohere: ¡Actualizado a su modelo más reciente para RAG!
                llm = ChatCohere(cohere_api_key=cohere_api_key, model="command-a-03-2025")
                
                # Configurar el Retriever (Buscador vectorial)
                retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 4})
                
                # Configurar el Prompt (Instrucción al sistema)
                system_prompt = (
                    "Eres el asistente interno de Recursos Humanos y Operaciones de KUBIQ. "
                    "Tu tarea es responder a las preguntas de los empleados basándote ÚNICAMENTE en el siguiente contexto extraído del manual de la empresa. "
                    "Si la respuesta no está en el contexto, di amablemente que no tienes esa información y sugiere contactar a RRHH. "
                    "Responde de manera profesional, clara y concisa.\n\n"
                    "Contexto:\n{context}"
                )
                
                qa_prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", "{input}"),
                ])
                
                # Crear la cadena RAG con la nueva sintaxis de LangChain (LCEL)
                question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
                rag_chain = create_retrieval_chain(retriever, question_answer_chain)
                
                # Ejecutar la consulta
                response = rag_chain.invoke({"input": prompt})
                answer = response["answer"]
                
                # Mostrar y guardar respuesta
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                # (Opcional) Mostrar las fuentes consultadas
                with st.expander("Ver fragmentos consultados del documento"):
                    for i, doc in enumerate(response["context"]):
                        st.write(f"**Fragmento {i+1}:**")
                        st.caption(doc.page_content)
                        
            except Exception as e:
                st.error(f"Hubo un error al generar la respuesta: {str(e)}")
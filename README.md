🤖 Agente KUBIQ: Asistente Interno con IA (RAG)

Este proyecto es el desafío final del programa Alura Agente. Consiste en el desarrollo de un asistente virtual inteligente corporativo para la tienda online 'KUBIQ', diseñado para optimizar el acceso a la información interna de la empresa.

📖 Descripción General del Proyecto

KUBIQ maneja grandes volúmenes de documentos internos, como manuales de políticas de privacidad, procesos de devoluciones y normativas de envíos. Tradicionalmente, los empleados invertían mucho tiempo buscando información específica en estos extensos PDFs.

El Agente KUBIQ soluciona este problema implementando un sistema de Inteligencia Artificial que "lee" y comprende estos documentos, permitiendo a los empleados realizar consultas en lenguaje natural y obtener respuestas precisas, inmediatas y estrictamente basadas en la documentación oficial de la empresa.

🏗️ Arquitectura de la Solución (RAG)

La solución está construida sobre la arquitectura Retrieval-Augmented Generation (RAG), garantizando que el modelo no invente información (cero alucinaciones). El flujo de datos es el siguiente:

Ingesta de Datos: El sistema carga automáticamente el documento local (politicas_kubiq.pdf) utilizando PyPDFLoader.

Procesamiento y División: El texto se divide en fragmentos semánticos manejables (Chunks) utilizando RecursiveCharacterTextSplitter para no exceder los límites de memoria del modelo.

Generación de Embeddings: Los fragmentos de texto se convierten en representaciones vectoriales matemáticas utilizando el modelo multilingüe de Cohere (embed-multilingual-v3.0).

Almacenamiento Vectorial: Estos vectores se guardan en la base de datos vectorial FAISS (ejecutada localmente en memoria) para búsquedas de alta velocidad.

Recuperación y Generación (Query):

Cuando un usuario hace una pregunta en la interfaz, su consulta se vectoriza.

FAISS busca los fragmentos del documento más similares a la pregunta.

Se envía un Prompt estructurado al modelo de lenguaje (LLM) de Cohere (command-a-03-2025), incluyedo la pregunta original y los fragmentos de texto encontrados como contexto estricto.

El LLM redacta una respuesta natural y profesional basada únicamente en ese contexto.

🛠️ Tecnologías y Herramientas Utilizadas

Lenguaje de Programación: Python 3.10+

Framework de Interfaz Gráfica (UI): Streamlit (Despliegue web interactivo).

Orquestador de IA: LangChain (LCEL - Cadenas de recuperación y documentos).

Modelo de Lenguaje (LLM): Cohere (command-a-03-2025 optimizado para tareas RAG corporativas).

Modelo de Embeddings: Cohere (embed-multilingual-v3.0).

Base de Datos Vectorial: FAISS (Facebook AI Similarity Search).

Procesamiento de Documentos: pypdf para lectura de archivos.

Seguridad: python-dotenv para la gestión segura de API Keys.

🚀 Instrucciones para ejecutar el proyecto localmente

Sigue estos pasos para clonar e iniciar el Agente KUBIQ en tu máquina:

1. Requisitos Previos

Python 3.10 o superior instalado.

Una cuenta en Cohere para obtener una API Key gratuita.

2. Clonar el Repositorio

git clone https://github.com/Jhonatanlez/Agente-KUBIQ-RAG.git
cd Agente-KUBIQ-RAG


3. Configurar Credenciales

Crea un archivo llamado .env en la raíz del proyecto y añade tu clave de la API de Cohere:

COHERE_API_KEY=tu_clave_secreta_aqui


4. Instalar Dependencias

Instala las librerías necesarias ejecutando:

pip install -r requirements.txt


5. Preparar el Documento

Asegúrate de que el documento de origen se llame politicas_kubiq.pdf y esté en la misma carpeta que el archivo principal kubiq_agent.py.

6. Ejecutar la Aplicación

Inicia el servidor local de Streamlit con el siguiente comando:

streamlit run kubiq_agent.py


Se abrirá automáticamente una pestaña en tu navegador web. El sistema vectorizará el documento en segundo plano y estará listo para responder consultas.

❓ Ejemplos de Preguntas que el Agente puede responder

Los empleados pueden formular preguntas en lenguaje natural como las siguientes:

"¿Cuál es el plazo máximo que tiene un cliente para solicitar la devolución de un producto electrónico?"

"¿Qué paquetería utilizamos para los envíos internacionales y cuánto tiempo tardan?"

"Si un producto llega dañado a la casa del cliente, ¿quién asume el costo del envío de retorno?"

"¿Cuáles son los pasos que debe seguir un cliente para hacer válida la garantía de fábrica?"

"¿Cómo tratamos los datos personales de los clientes según nuestra política de privacidad?"

💬 Ejemplos de Respuestas generadas por el Agente

Ejemplo de Consulta 1:

Usuario: "¿Cuánto tiempo tiene un cliente para devolver ropa deportiva?"

Agente KUBIQ: "Según las políticas de devoluciones de la empresa, los clientes tienen un plazo de 30 días naturales a partir de la fecha de entrega para solicitar la devolución de prendas de ropa deportiva. El producto debe conservar sus etiquetas originales y no mostrar señales de uso."

Ejemplo de Consulta 2 (Caso donde la información no existe):

Usuario: "¿A qué hora es la fiesta de fin de año de la empresa?"

Agente KUBIQ: "No dispongo de esa información en los manuales de políticas y operaciones actuales. Te sugiero contactar directamente al departamento de Recursos Humanos para obtener detalles sobre los eventos corporativos."

Ejemplo de Consulta 3:

Usuario: "¿Hacemos envíos los fines de semana?"

Agente KUBIQ: "No, el manual de operaciones logísticas indica que los envíos estándar solo se procesan y despachan en días hábiles (de lunes a viernes, excluyendo días festivos oficiales). Las compras realizadas los sábados o domingos comenzarán a procesarse el lunes siguiente."

Desarrollado por [Tu Nombre/Jhonatanlez] para el desafío Alura.
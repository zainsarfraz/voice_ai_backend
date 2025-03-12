import tempfile

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb


chroma_client = chromadb.PersistentClient()
PERSIST_DIRECTORY_PATH = "./chroma"


async def add_doc_to_vector_store(document, collection_name):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
        temp_file.write(document.file.read())
        temp_file.flush()

        loader = PyPDFLoader(temp_file.name)
        loaded_docs = await loader.aload()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=100
        )
        chunks = text_splitter.split_documents(loaded_docs)

        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(),
            persist_directory=PERSIST_DIRECTORY_PATH,
        )

        vectorstore.add_documents(chunks)


def search_vector_store(collection_name: str, query: str):
    vector_strore = Chroma(
        collection_name=collection_name,
        embedding_function=OpenAIEmbeddings(),
        persist_directory=PERSIST_DIRECTORY_PATH,
        create_collection_if_not_exists=False,
    )
    results = vector_strore.similarity_search_with_relevance_scores(query=query, k=5)
    formatted_results = []
    for doc in results:
        formatted_results.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
        )
    return str(formatted_results)


def files_in_collection(collection_name: str):
    try:
        vector_strore = Chroma(
            collection_name=collection_name,
            embedding_function=OpenAIEmbeddings(),
            persist_directory=PERSIST_DIRECTORY_PATH,
            create_collection_if_not_exists=False,
        )
        data = vector_strore.get(include=['metadatas'])
        unique_titles = list({item['title'] for item in data['metadatas']})
        return unique_titles
    except Exception:
        return []
    
    
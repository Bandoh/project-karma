# app/vector_db.py
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

_vector_store = None  # Private module variable


def get_vector_store():
    """Get or initialize the vector store (singleton pattern)"""
    global _vector_store
    if _vector_store is None:
        print("🔧 Creating NEW vector store...")  # Only prints once
        _vector_store = _initialize_vector_store()
    else:
        print("✅ Reusing EXISTING vector store")  # Prints on subsequent calls
    return _vector_store


def _initialize_vector_store():
    """Private function to set up the vector store"""
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    vector_store = InMemoryVectorStore(embeddings)

    # Load and split documents
    loader = TextLoader("./app/data/memory.txt")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100, add_start_index=True
    )
    splits = text_splitter.split_documents(docs)

    # Add documents to store
    vector_store.add_documents(documents=splits)
    return vector_store

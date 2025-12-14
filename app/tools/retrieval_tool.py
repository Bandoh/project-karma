from langchain.tools import tool
import logging
from app.vector_db import get_vector_store


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Search through stored documents and knowledge base to find relevant information.

    Use this tool when you need to:
    - Find specific information from uploaded documents
    - Search through the knowledge base
    - Retrieve context about topics not in your training data
    - Look up details about people, projects, or events in the system

    Args:
        query: The search query to find relevant documents

    Returns:
        Relevant document excerpts with their sources
    """
    logging.info("We are in retrieval tool.....")
    print("In tool")
    vector_store = get_vector_store()
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

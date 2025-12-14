from langchain.tools import tool
import datetime
from langchain_core.documents import Document
from app.vector_db import get_vector_store


@tool(response_format="content")
def update_memory(information: str) -> str:
    """Permanently store important information in the knowledge base.

    Use this when the user:
    - Tells you something about themselves to remember
    - Asks you to "remember this" or "store this"
    - Shares preferences, facts, or context you should retain

    Args:
        information: Clear, complete information to store (e.g., "Kelvin Quansah is the creator and main user")

    Returns:
        Confirmation that information was stored
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a document
    doc = Document(
        page_content=information,
        metadata={"source": "user_memory", "timestamp": timestamp, "type": "memory"},
    )

    # Add to vector store
    vector_store = get_vector_store()
    vector_store.add_documents([doc])

    # Also append to txt file as backup
    with open("app/data/memory.txt", "a") as f:
        f.write(f"[{timestamp}] {information}\n")

    return f"✓ Remembered: {information}"

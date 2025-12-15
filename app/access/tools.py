from langchain.tools import tool
import logging
from app.vector_db import get_vector_store
from langchain_core.documents import Document
import subprocess
import datetime


@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Search through stored documents and knowledge base for information.

    **ONLY use this tool for searching stored documents and knowledge base content.**

    DO NOT use this tool for:
    - System commands (use terminal_access instead)
    - File operations (use terminal_access instead)

    Use this tool when you need to:
    - Find information from previously uploaded documents
    - Search the knowledge base for stored facts
    - Retrieve context about people, projects, or events that were saved
    - Look up remembered information

    Args:
        query: Natural language search query to find relevant documents

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


@tool(response_format="content")
def terminal_access(command: str):  # Changed from cmd: list to command: str
    """Execute terminal/shell commands on the operating system.

    **Use this tool for ANY system command, shell operation, or file system interaction.**

    Common commands that MUST use this tool:
    - ls, dir, pwd (directory operations)
    - cat, head, tail, grep (file reading)
    - mkdir, rm, cp, mv (file operations)
    - python, node, bash (running scripts)
    - Any command you would type in a terminal

    Args:
        command: The command as a string (e.g., "ls -la" or "cat file.txt")

    Returns:
        Command output. Returns stderr if errors occur, otherwise stdout.

    Examples:
        - "ls -la" - List directory contents
        - "cat file.txt" - Read file contents
        - "python --version" - Check Python version
        - "pwd" - Print working directory
    """
    print("In tool, this is the command:", command)

    # Split the command string into a list for subprocess
    cmd_list = command.split()

    result = subprocess.run(cmd_list, capture_output=True, text=True, shell=True)
    if result.stderr:
        return result.stderr
    else:
        return result.stdout


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

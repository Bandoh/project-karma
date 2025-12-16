from langchain.tools import tool
import logging
from app.utils.vector_db import get_vector_store
from langchain_core.documents import Document
import subprocess
import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.utils import get_stop_words
from bs4 import BeautifulSoup


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

    result = subprocess.run(command, capture_output=True, text=True, shell=True)
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


@tool(
    response_format="content",
    description="Fetches the complete HTML source code of a web page using a headless Chrome browser. Use this tool when you need to scrape web content, extract information from websites, or analyze page structure. The tool handles JavaScript-rendered content and returns the fully loaded DOM.",
)
def browser(url: str) -> str:
    """
    Fetches and summarizes web page content using headless Chrome browser.

    This tool scrapes a web page, extracts its textual content, and generates
    a concise summary using LexRank extractive summarization. It handles
    JavaScript-rendered content by using Selenium WebDriver with a headless
    Chrome browser to obtain the fully loaded DOM.

    Args:
        url (str): The complete URL of the web page to fetch and summarize.
                    Must include the protocol (e.g., 'https://example.com').

    Returns:
        str: A summarized version of the page content, consisting of most relevant sentences as determined by the LexRank algorithm.
                Returns an empty string if the page cannot be accessed or contains
                no extractable text.

    Example:
        >>> summary = browser("https://example.com/article")
        >>> print(summary)
        'This is the first key sentence. This is another important point...'

    Raises:
        WebDriverException: If Chrome browser or ChromeDriver is not properly
                            configured or if the URL cannot be accessed.
    """
    # Initialize the summarizer with language settings
    LANGUAGE = "english"
    SENTENCES_COUNT = 8

    summarizer_lex = LexRankSummarizer(Stemmer(LANGUAGE))
    summarizer_lex.stop_words = get_stop_words(LANGUAGE)

    summarized = ""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url=url)
        page_content = driver.page_source

        # Parse HTML and extract text using BeautifulSoup
        soup = BeautifulSoup(page_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)

        # Parse text into a Document object using PlaintextParser
        parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
        document = parser.document

        # Generate summary
        summary = summarizer_lex(document, SENTENCES_COUNT)

        for sentence in summary:
            summarized += str(sentence) + " "

    finally:
        driver.quit()

    return summarized.strip()


# can you browse this page and tell me what in there https://en.wikipedia.org/wiki/Albert_Bandura

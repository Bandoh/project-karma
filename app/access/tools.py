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
import requests


# @tool(response_format="content_and_artifact")
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
    vector_store = get_vector_store()
    all_docs = ""
    retrieved_docs_with_scores = vector_store.similarity_search_with_score(query, k=5)
    for doc, score in retrieved_docs_with_scores:
        # print(score) 
        if score > 0.25: 
            all_docs+= " {}".format(doc.page_content)
    return all_docs



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
    print("terminal_access tool, command:", command)

    # Split the command string into a list for subprocess

    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    if result.stderr:
        return result.stderr
    else:
        return result.stdout



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



def search_anime(query: str, search_type: str) -> str:
    """
    Search for anime information using the Jikan API (MyAnimeList unofficial API).

    Args:
        query (str): The search query. For 'get_anime' and 'search_character',
                     this should be the name to search for. For 'anime_recommendations',
                     this should be the anime ID. For 'top_anime', this parameter is ignored.
        search_type (str): The type of search to perform. Must be one of:
                          - 'anime_recommendations': Get anime recommendations (query = anime name)
                          - 'top_anime': Get top-ranked anime (query ignored)
                          - 'get_anime': Search for anime by name, use this to find any information about a particular anime
                          - 'search_character': Search for characters by name


    Returns:
        str: JSON response from the Jikan API as a string, containing anime/character
             information including titles, scores, images, synopses, and other metadata.

    Example:
        >>> search_anime("naruto", "search_character")
        >>> search_anime("naruto", "anime_recommendations")
        >>> search_anime("", "top_anime")
        >>> search_anime("bleach", "get_anime")
    """
    needed_info = [
        "mal_id",
        "title",
        "score",
        "favorites",
        "popularity",
        "synopsis",
        "rank",
        "year",
        "genres",
        "themes",
        "episodes",
    ]

    urls = {
        "top_anime": "https://api.jikan.moe/v4/top/anime",
        "get_anime": "https://api.jikan.moe/v4/anime?q={}",
        "search_character": "https://api.jikan.moe/v4/characters?q={}",
        "anime_recommendations": "https://api.jikan.moe/v4/anime/{}/recommendations",
    }

    # Get recommendations (special case)
    if search_type == "anime_recommendations":
        # Find anime ID
        url = urls["get_anime"].format(query)
        anime = requests.get(url).json()["data"][0]
        anime_id = anime["mal_id"]

        # Get recommendations
        url = urls["anime_recommendations"].format(anime_id)
        recs = requests.get(url).json()["data"]

        # Format and sort by votes
        results = [{"title": r["entry"]["title"], "votes": r["votes"]} for r in recs]
        results.sort(key=lambda x: x["votes"], reverse=True)

        return str(results[:5])

    # All other search types
    url = (
        urls[search_type]
        if search_type == "top_anime"
        else urls[search_type].format(query)
    )
    resp = requests.get(url).json()["data"]
    json_resp = []
    for anime in resp:
        json_resp.append({key: anime.get(key) for key in needed_info})
    if search_type in ("get_anime", "search_character"):
        return str(json_resp[0])
    else:
        return str(json_resp[:5])



# can you browse this page and tell me what in there https://en.wikipedia.org/wiki/Albert_Bandura
# give me anime recommendations based on erased

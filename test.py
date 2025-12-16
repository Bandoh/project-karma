import subprocess
import requests
import json
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.utils import get_stop_words
import nltk
from bs4 import BeautifulSoup


nltk.download("punkt_tab")


def anime_stuff():
    url = "https://api.jikan.moe/v4"
    path = "/anime"
    params = {"rating": "Rx", "q": "", "limit": 4, "genres": 4}

    resp = requests.get(url=url + path, params=params)
    print(resp.json())

    with open("anime.json", "w+") as inp:
        json.dump(resp.json(), inp)
        inp.close()


def browser(url: str) -> str:
    # Initialize the summarizer with language settings
    LANGUAGE = "english"
    SENTENCES_COUNT = 10

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


# Test
print(browser("https://en.wikipedia.org/wiki/Albert_Bandura"))

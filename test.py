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
import torch

print(torch.xpu.is_available())
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


def search_engine_anime(query: str, search_type: str):
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
        "get_anime_id": "https://api.jikan.moe/v4/anime?q={}",
        "search_character": "https://api.jikan.moe/v4/characters?q={}",
        "anime_recommendations": "https://api.jikan.moe/v4/anime/{}/recommendations",
    }

    # Get recommendations (special case)
    if search_type == "anime_recommendations":
        # Find anime ID
        url = urls["get_anime_id"].format(query)
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
    return str(json_resp)


def save_to_json(data):
    with open("output.json", "w+") as inp:
        json.dump(data, inp)


search_engine_anime("erased", "top_anime")

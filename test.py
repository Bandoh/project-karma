import subprocess
import requests
import json

url = "https://api.jikan.moe/v4"
path = "/anime"
params = {"rating": "Rx", "q": "", "limit": 4, "genres": 4}

resp = requests.get(url=url + path, params=params)
print(resp.json())

with open("anime.json", "w+") as inp:
    json.dump(resp.json(), inp)
    inp.close()

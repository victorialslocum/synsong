import requests
from bs4 import BeautifulSoup
import re
import json


def get_quote_list(url, cat):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all('div', class_="quoteText")

    dataset = []

    cats_list = {"love": 0, "life": 0,
                 "happiness": 0, "music": 0, "inspirational": 0}
    cats_list[cat] = 1

    for element in results:
        data = {}
        data['cats'] = cats_list
        split = re.split("“|”", element.text)
        data['text'] = split[1].replace("’", "'")
        dataset.append(data)

    return dataset


data = []

love_url = "https://www.goodreads.com/quotes/tag/love"
love_quotes = get_quote_list(love_url, "love")
data += love_quotes

life_url = "https://www.goodreads.com/quotes/tag/life"
life_quotes = get_quote_list(life_url, "life")
data += life_quotes

happiness_url = "https://www.goodreads.com/quotes/tag/happiness"
happiness_quotes = get_quote_list(happiness_url, "happiness")
data += happiness_quotes

music_url = "https://www.goodreads.com/quotes/tag/music"
music_quotes = get_quote_list(music_url, "music")
data += music_quotes

inspirational_url = "https://www.goodreads.com/quotes/tag/inspirational"
inspirational_quotes = get_quote_list(inspirational_url, "inspirational")
data += inspirational_quotes

with open('poetry_class/data.json', 'w') as f:
    json.dump(data, f)

import requests
from bs4 import BeautifulSoup
import re
import json


def get_data(url, cats, train):

    data = []
    pages = ['', '?page=2'] if train else ["?page=3"]

    for cat in cats:
        cats_list = {cat: 0 for cat in cats}
        cats_list[cat] = 1

        results = []
        for page in pages:

            cat_url = url + cat + page
            page = requests.get(cat_url)

            soup = BeautifulSoup(page.content, "html.parser")

            results += soup.find_all('div', class_="quoteText")

        cat_data = []

        for element in results:
            quote_data = {}
            quote_data['cats'] = cats_list
            split = re.split("“|”", element.text)
            quote_data['text'] = split[1].replace("’", "'")
            cat_data.append(quote_data)

        data += cat_data

    return data


url = 'https://www.goodreads.com/quotes/tag/'
cats = ['love', 'life', 'music', 'depression']
data = get_data(url, cats, True)
print(data)

with open('poetry_class/data/data.json', 'w') as f:
    json.dump(data, f)

data_test = get_data(url, cats, False)

with open('poetry_class/data/test_data.json', 'w') as f:
    json.dump(data_test, f)

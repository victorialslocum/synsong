import requests
import spotipy
import json
import nltk
import re
import pprint
import string
import itertools
import random
import spacy
from spotipy.oauth2 import SpotifyOAuth
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from itertools import chain

nlp = spacy.load('en_core_web_sm')
prompt = "Sing like no one’s listening, love like you’ve never been hurt, dance like nobody’s watching, and live like it’s heaven on earth."


def create_title(prompt):
    text = nlp(prompt)
    title_list = []

    for token in text:
        if token.pos_ in ['NOUN', 'ADJ', 'PROPN']:
            print(token.text, token.dep_)
            if token.dep_ in ['nsubj', 'pobj'] or token.head.lemma_ == 'be':
                tokens = [t.text for t in token.subtree]
                title_list.append(tokens)

    print(title_list)

    chosen = random.sample(title_list, 1)[0]
    print(chosen)
    title = ' '.join(chosen)

    return title


title = create_title(prompt)
print(title)
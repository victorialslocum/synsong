import spacy
from sense2vec import Sense2VecComponent
import requests 
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
import json

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)



nlp = spacy.load("en_core_web_sm")
s2v = nlp.add_pipe("sense2vec")
s2v.from_disk("./s2v_old")

doc = nlp("I like sunshine and clouds")

content_words = []

for token in doc: 
    if token.is_stop == False:
        content_words.append(token.text)

content_chunks = []
def find_chunks(text):
    for chunk in text.noun_chunks:
        root_word = chunk.root.text
        if root_word in content_words:
            content_chunks.append(chunk)
    return content_chunks

words = find_chunks(doc)
print(words)

parameters = {
    'apikey': 'cf15cff658d467a39bf34a000c89e8bc',
    'page_size': 10,
    'f_has_lyrics': 1,
    's_track_rating': 'desc'
}

word_list = ""

for word in words:
    word_list += str(word) + ","

parameters['q_lyrics'] = word_list[:-1]

print(parameters)

response = requests.get("https://api.musixmatch.com/ws/1.1/track.search?", params=parameters)
track_list = response.json()['message']['body']['track_list']

song_list = {}

for item in track_list:
    value = item['track']
    artist = value['artist_name']
    song_name = value['track_name']
    song_list[song_name] = artist

print(song_list)
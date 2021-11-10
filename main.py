from os import POSIX_FADV_SEQUENTIAL
import requests 
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
import json
import nltk, re, pprint
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

prompt = """I like the yellow sunshine and clouds...."""

def preprocess_text(text): 
    text = text.lower()
    prompt_p = "".join([char for char in prompt if char not in string.punctuation])

    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(prompt_p)

    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]

    lemmed = [WordNetLemmatizer().lemmatize(w) for w in filtered_sentence]
    print(lemmed)

    pos_sent = pos_tag(lemmed)
    print(pos_sent)

    return pos_sent

def get_constituents(pos_sent):
    grammar = """
    NP: {<DT>?<JJ>*<NN>}
    {<NNP>+} 
    """
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(pos_sent)
    print(tree)

    constituent_list = []

    for subtree in tree.subtrees():
        print(subtree)
        if subtree.label() == 'NP': 
            np = str(subtree)
            pattern = r"\w+:?(?=\/)"
            clauses = [re.findall(pattern, np)]
            ouput = [" ".join(cl) for cl in clauses]
            constituent_list.append(ouput[0]) 

    return constituent_list

pre_text = preprocess_text(prompt)
print(pre_text)
words = get_constituents(pre_text)
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
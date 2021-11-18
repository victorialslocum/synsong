import requests, spotipy, json, nltk, re, pprint, string, itertools, random, spacy
from spotipy.oauth2 import SpotifyOAuth
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from itertools import chain

import keys
MUSIXMATCH_API_KEY = keys.MUSIXMATCH_API_KEY
SPOTIPY_CLIENT_ID = keys.SPOTIPY_CLIENT_ID
SPOTIPY_CLIENT_SECRET = keys.SPOTIPY_CLIENT_SECRET

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

prompt = "When virtue and modesty enlighten her charms, the lustre of a beautiful woman is brighter than the stars of heaven, and the influence of her power it is in vain to resist."

nlp = spacy.load('en_core_web_sm')


def create_title(prompt):
    text = nlp(prompt)
    title_list = []

    for token in text:
        if token.pos_ in ['NOUN', 'ADJ']:
            if token.dep_ == 'nsubj' or token.head.lemma_ == 'be':
                tokens = [t.text for t in token.subtree]
                title_list.append(tokens)

    print(title_list)

    chosen = random.sample(title_list, 1)[0]
    print(chosen)          
    title = ' '.join(chosen)
    
    return title

title = create_title(prompt)
print(title)

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
    grammar = "NP: {<DET>?<JJ>*<NN>}"
    cp = nltk.RegexpParser(grammar)
    tree = cp.parse(pos_sent)
    print(tree)

    constituent_list = [word for word,pos in pos_sent if pos == 'NNP' or pos == 'NNS']

    for subtree in tree.subtrees():
        if subtree.label() == 'NP': 
            np = str(subtree)
            pattern = r"\w+:?(?=\/)"
            clauses = [re.findall(pattern, np)]
            ouput = [" ".join(cl) for cl in clauses]
            constituent_list.append(ouput[0]) 

    return constituent_list

pre_text = preprocess_text(prompt)
words = get_constituents(pre_text)
words = random.sample(words, 5)
print(words)

def word_list_combo(word_list):
    p = [[]]
    fnl = [word_list]

    for i in range(len(word_list)):
        for j in range(i+1,len(word_list)):
            p[-1].append([i,j])

    for i in range(len(word_list)-3):
        p.append([])
        for m in p[-2]:
            p[-1].append(m+[m[-1]+1])

    for i in p:
        for j in i:
            n = []
            for m in j:
                if m < len(word_list):
                    n.append(word_list[m])
            if n not in fnl:
                fnl.append(n)

    for i in word_list:
        if [i] not in fnl:
            fnl.append([i])

    list = fnl[10:]
    print(list)
    return list

word_list = word_list_combo(words)

def parameters(word_list, page_size, s_track_rating):
    parameters = {
        'apikey': MUSIXMATCH_API_KEY,
        'page_size': page_size
    }

    if s_track_rating != 'none':
        parameters['s_track_rating'] = s_track_rating

    words = ""

    for word in word_list:
        words += str(word) + ","

    parameters['q'] = words[:-1]

    return parameters

def process_name(name):
    name = re.sub(r"\([^()]*\)", "", name)
    name = name.split("-")[0]
    name = name.split("feat.")[0]

    return name


def get_song_list(parameters):
    response = requests.get("https://api.musixmatch.com/ws/1.1/track.search?", params=parameters)
    track_list = response.json()['message']['body']['track_list']

    song_list = {}

    for item in track_list:
        value = item['track']
        artist = value['artist_name']
        artist = process_name(artist)
        song_name = value['track_name']
        song_name = process_name(song_name)
        if song_name not in song_list:
            song_list[song_name] = artist

    return song_list


song_dicts = []

for list in word_list:
    parameter1 = parameters(list, len(list)*2, 'none')
    parameter2 = parameters(list, len(list)*2, 'desc')

    song_dicts.append(get_song_list(parameter1))
    song_dicts.append(get_song_list(parameter2))

song_list = dict(chain.from_iterable(d.items() for d in song_dicts))

print(song_list)

scope = "playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri='http://localhost:8000/'))

track_id_list = []

for key in song_list:
    artist = song_list[key]
    track = key
    response = sp.search(q='artist:' + artist + ' track:' + track, type='track', limit=1)
    if response['tracks']['items']:
        track_id = response['tracks']['items'][0]['id']
        track_id_list.append(track_id)


playlist = sp.user_playlist_create('victoriaslo235', title, public=False, collaborative=False, description=prompt)

playlist_id = playlist['id']
sp.user_playlist_add_tracks('a0f90529781c4f6a', playlist_id, track_id_list, position=None)

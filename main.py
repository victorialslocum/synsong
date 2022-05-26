# to run this (lol)
# FLASK_APP=main.py FLASK_ENV=development flask run

import requests
import spotipy
import re
import random
import spacy
import time
import json
from spotipy.oauth2 import SpotifyOAuth
from itertools import chain
from flask import Flask, render_template, redirect, request, session, url_for, make_response
from flask_oauthlib.client import OAuth, OAuthException
from decouple import config

MUSIXMATCH_API_KEY = config('MUSIXMATCH_API_KEY')
SPOTIPY_CLIENT_ID = config('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = config('SPOTIPY_CLIENT_SECRET')
SECRET_KEY = config('SECRET_KEY')
GANALYTICS = config('GANALYTICS')

REDIRECT_URI = config('REDIRECT_URI')
API_BASE = 'https://accounts.spotify.com'
SCOPE = 'playlist-modify-public user-read-private'

app = Flask(__name__)
app.secret_key = SECRET_KEY
oauth = OAuth(app)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route("/")
def home():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    if "token_info" in session:
        return render_template("home.html", login_url="/logout", login_text="Log out", app_url="/generator", app_text="Go to app", ganalytics=GANALYTICS)
    else:
        return render_template("home.html", login_url=auth_url, login_text="Log in", app_url=auth_url, app_text="Get started", ganalytics=GANALYTICS)


@app.route("/generator", methods=['GET', 'POST'])
def generator():
    if request.method == 'POST':
        quote = request.form['quote']
        genre_list = request.form.get('hidden')
        vis = request.form.get("hiddenvis")
        pop = request.form.get("hiddenpop")
        print(genre_list)
        return redirect(url_for('make_playlist', quote=quote, genre_list=genre_list, vis=vis, pop=pop))
    else:
        return render_template("generator.html", login_url="/logout", login_text='Log out', app_url="/generator", app_text="Go to app", ganalytics=GANALYTICS)


@app.route("/community")
def community():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    if "token_info" in session:
        return render_template("community.html", login_url="/logout", login_text="Log out", app_url="/generator", app_text="Go to app", ganalytics=GANALYTICS)
    else:
        return render_template("community.html", login_url=auth_url, login_text="Log in", app_url=auth_url, app_text="Get started", ganalytics=GANALYTICS)


@app.route("/features")
def features():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    if "token_info" in session:
        return render_template("features.html", login_url="/logout", login_text="Log out", app_url="/generator", app_text="Go to app", ganalytics=GANALYTICS)
    else:
        return render_template("features.html", login_url=auth_url, login_text="Log in", app_url=auth_url, app_text="Get started", ganalytics=GANALYTICS)


@app.route("/about")
def about():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url = sp_oauth.get_authorize_url()
    if "token_info" in session:
        return render_template("about.html", login_url="/logout", login_text="Log out", app_url="/generator", app_text="Go to app", ganalytics=GANALYTICS)
    else:
        return render_template("about.html", login_url=auth_url, login_text="Log in", app_url=auth_url, app_text="Get started", ganalytics=GANALYTICS)


@app.route("/callback")
def callback():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(
        code, as_dict=True, check_cache=False)
    # Saving the access token along with all other token related info
    session["token_info"] = token_info
    return redirect("generator")


@app.route("/test_shit", methods=['GET', 'POST'])
def test_shit():
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    user = sp.me()
    print(session["token_info"]["access_token"])
    print(user)
    return user["id"]


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect("/")


@app.route("/success/<quote>/<playlist_id>/<genres>/<pop>")
def success(quote, playlist_id, genres, pop):

    return render_template("success.html", success=True, playlist_id=playlist_id, genres=genres, quote=quote, pop=pop, login_url="/logout", login_text='Log out', ganalytics=GANALYTICS)


@app.route("/make_playlist/<quote>/<genre_list>/<vis>/<pop>", methods=['GET', 'POST'])
def make_playlist(quote, genre_list, vis, pop):
    session['token_info'], authorized = get_token(session)
    session.modified = True

    if not authorized:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
        auth_url = sp_oauth.get_authorize_url()
        return redirect('/')

    nlp = spacy.load('en_core_web_sm')

    # create title of playlist from quote
    def create_title(quote):
        # spaCy splits quote into tokens
        doc = nlp(quote)

        # breaks the doc into multi-word segments, matching whether the head has complement or adverbial clause
        # dependency relationship
        title_list_v = [[child.text for child in tok.subtree]
                        for tok in doc if tok.dep_ in ['pcomp', 'xcomp', 'ccomp', 'advcl']]

        # breaks the doc into multi-word segements, matching whether its a subject or object of a prep
        title_list_n = [[child.text for child in tok.subtree]
                        for tok in doc if tok.dep_ in ['nsubj', 'pobj']]

        # combining the lists if the segments have 4-7 words
        title_list = [item for item in
                      title_list_v + title_list_n if 3 < len(item) < 8]
        print(title_list)
        title = ''
        # if list has items, take a random one, else, make noun chunks and take one, else quote
        if title_list:
            title = ' '.join(random.sample(title_list, 1)[0])
            title = re.sub(r"\s+(?=')", '', title)
        else:
            title_list_new = [chunk.text for chunk in doc.noun_chunks]

            title = max(title_list_new, key=len) if title_list_new else quote
            title = re.sub(r"\s+(?=')", '', title)

        # return chosen title
        return title

    title = create_title(quote)
    print("title: ")
    print(title)

    def get_constituents(quote):
        text = nlp(quote)

        chunks = [chunk.text for chunk in text.noun_chunks]
        filt_chunks = []

        for const in chunks:
            words = nlp(const)
            filt_chunks.append(
                [token.lemma_ for token in words if not token.is_stop])

        const_list = []
        for chunk in filt_chunks:
            const_list.append(' '.join(chunk))

        while("" in const_list):
            const_list.remove("")

        print("constituents: ")
        print(const_list)
        return const_list

    def get_more_constituents(quote):
        text = nlp(quote)
        filt_chunks = []
        for token in text:
            if not token.is_stop:
                filt_chunks.append([token.lemma_])

        print("more constituents: ")
        print(filt_chunks)
        return filt_chunks

    words = get_constituents(quote)
    if len(words) > 5:
        words = random.sample(words, 5)
    print("words: ")
    print(words)

    def word_list_combo(word_list):
        p = [[]]
        fnl = [word_list]

        for i in range(len(word_list)):
            for j in range(i+1, len(word_list)):
                p[-1].append([i, j])

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

        length = len(word_list)*2
        if len(word_list) > 3:
            list = fnl[:1] + fnl[-length:]
        else:
            list = fnl

        print("list: ")
        print(list)
        return list

    word_list = word_list_combo(words)
    genre_ids = {'all': 34, 'blues': 2, 'comedy': 3, 'children': 4, 'classical': 5, 'country': 6,
                 'electronic': 7, 'holiday': 8, 'opera': 9, 'folk': 10, 'jazz': 11,
                 'latin': 12, 'new age': 13, 'pop': 14,  'randb': 15, 'soundtrack': 16,
                 'dance': 17, 'rap': 18, 'world': 19, 'alternative': 20, 'rock': 21,
                 'christian': 22, 'vocal': 23, 'reggae': 24, 'k-pop': 51}

    def parameters(word_list, genre, page_size, s_track_rating):
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
        parameters['f_music_genre_id'] = genre

        return parameters

    def process_name(name):
        name = re.sub(r"\([^()]*\)", "", name)
        name = name.split("-")[0]
        name = name.split("feat.")[0]
        name = name.split(" [")[0]
        name = name.strip()
        name = name.lower()
        return name

    def get_song_list(parameters):
        response = requests.get(
            "https://api.musixmatch.com/ws/1.1/track.search?", params=parameters)
        track_list = response.json()['message']['body']['track_list']

        song_list = {}

        for item in track_list:
            value = item['track']
            artist = value['artist_name']
            artist = process_name(artist)
            song_name = value['track_name']
            song_name = process_name(song_name)
            song_list[song_name] = artist

        return song_list

    song_dicts = []
    genre_list = genre_list.split(",")

    genres = []
    [genres.append(x) for x in genre_list if x not in genres]

    pop = int(pop)
    print(pop)

    for list in word_list:
        if pop == 0:
            lenlist = [len(list)*4, 0]
        if pop == 100:
            lenlist = [0, len(list)*4]
        elif pop < 40:
            lenlist = [len(list)*3, len(list)]
        elif 40 <= pop <= 70:
            lenlist = [len(list)*2, len(list)*2]
        elif pop > 70:
            lenlist = [len(list), len(list)*3]

        for genre in genres:
            parameter1 = parameters(
                list, genre_ids[genre], lenlist[0], 'none')
            parameter2 = parameters(
                list, genre_ids[genre], lenlist[1], 'desc')

            song_dicts.append(get_song_list(parameter1))
            song_dicts.append(get_song_list(parameter2))

    song_list = dict(chain.from_iterable(d.items() for d in song_dicts))

    songs = {}

    for song, artist in song_list.items():
        if song not in songs.keys():
            songs[song] = artist

    print("songs: ")
    print(songs)

    if len(songs) < 10:
        more_words = get_more_constituents(quote)
        print("more words: ")
        print(more_words)
        for word in more_words:
            for genre in genres:
                parameter1 = parameters(
                    word, genre_ids[genre], len(list)*2, 'none')
                parameter2 = parameters(
                    word, genre_ids[genre], len(list)*3, 'desc')

                song_dicts.append(get_song_list(parameter1))
                song_dicts.append(get_song_list(parameter2))
        song_list = dict(chain.from_iterable(d.items() for d in song_dicts))
        for song, artist in song_list.items():
            if song not in songs.keys():
                songs[song] = artist

        print("new songs: ")
        print(songs)

    if len(songs) > 25:
        songs = {S: A for (S, A) in [x for x in songs.items()][:30]}

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))

    user = sp.me()
    print(user)

    track_id_list = []

    for key, artist in songs.items():
        artist = artist
        track = key
        response = sp.search(q='artist:' + artist +
                             ' track:' + track, type='track', limit=1)
        if response['tracks']['items']:
            track_id = response['tracks']['items'][0]['id']
            track_id_list.append(track_id)

    description = quote + " ❤ synsong.app"
    playlist = sp.user_playlist_create(
        user['id'], title, public=True, collaborative=False, description=description)

    playlist_id = playlist['id']
    sp.user_playlist_add_tracks(
        user['id'], playlist_id, track_id_list, position=None)

    return redirect(url_for('success', success=vis, quote=quote, genres=genre_list, pop=pop, playlist_id=playlist_id, login_url="/logout", login_text='Log out'))


def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = spotipy.oauth2.SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
        token_info = sp_oauth.refresh_access_token(
            session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


if __name__ == "__main__":
    app.run(debug=True)

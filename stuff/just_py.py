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

REDIRECT_URI = config('REDIRECT_URI')
API_BASE = 'https://accounts.spotify.com'
SCOPE = 'playlist-modify-public user-read-private'


prompt = "When i've worn a hole In my last pair of shoes I'll have a yellow sunshine kind of day"

genre_list = ['blues', "children"]

def make_playlist(prompt, genre_list):
        
    nlp = spacy.load('en_core_web_sm')

    def create_title(prompt):
        text = nlp(prompt)
        title_list = []

        for token in text:
            if token.pos_ in ['NOUN', 'ADJ']:
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

    def get_constituents(prompt):
        text = nlp(prompt)

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

        print(const_list)
        return const_list

    words = get_constituents(prompt)
    if len(words) > 5:
        words = random.sample(words, 5)
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

        if len(word_list) > 5:
            list = fnl[12:]
        else:
            list = fnl

        print(list)
        return list

    word_list = word_list_combo(words)

    def parameters(word_list, genre_list, page_size, s_track_rating):
        parameters = {
            'apikey': MUSIXMATCH_API_KEY,
            'page_size': page_size
        }

        if s_track_rating != 'none':
            parameters['s_track_rating'] = s_track_rating

        words = ""
        genres = ""
        for word in word_list:
            words += str(word) + ","

        for genre in genre_list:
            genres += str(genre)

        parameters['q'] = words[:-1]
        parameters['f_music_genre_id'] = genres[:-1]
        
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

    for list in word_list:
        parameter1 = parameters(list, genre_list, len(list), 'none')
        parameter2 = parameters(list, genre_list, len(list), 'desc')

        song_dicts.append(get_song_list(parameter1))
        song_dicts.append(get_song_list(parameter2))

    songs = {}

    song_list = dict(chain.from_iterable(d.items() for d in song_dicts))

    for song, artist in song_list.items():
        if song not in songs.keys():
            songs[song] = artist

    print(songs)

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    # sp = spotipy.Spotify(auth=token_info['access_token'])

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


    description = prompt + " ❤ synsong.app"
    playlist = sp.user_playlist_create(
        user['id'], title, public=True, collaborative=False, description=description)

    playlist_id = playlist['id']
    sp.user_playlist_add_tracks(
        user['id'], playlist_id, track_id_list, position=None)

    return

make_playlist(prompt, genre_list)
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


quote = "The greatest glory in living lies not in never falling, but in rising every time we fall."

genre_list = "blues,pop"
vis = True
pop = 50


def make_playlist(quote, genre_list, vis, pop):

    # initialize spaCy tokenization
    nlp = spacy.load('en_core_web_sm')
    # intialize spaCy quote categorization model
    textcat = spacy.load(
        '/home/victoriaslocum/synsong/poetry_class/output/model-best')

    # create title of playlist from quote

    def create_title(quote):
        # spaCy splits quote into tokens
        doc = nlp(quote)

        # breaks the doc into multi-word segements, matching whether its a subject or object
        # of a prep and has 4-7 words
        title_list = [[child.text for child in tok.subtree]
                      for tok in doc if 3 < len(list(tok.subtree)) < 8
                      and tok.dep_ in ['nsubj', 'pobj', 'pcomp', 'xcomp', 'ccomp', 'advcl']]

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
        print("title: ")
        print(title)
        return title

    # get quote category (in progress)

    def get_cats(quote):
        # use textcat spaCy model
        doc = textcat(quote)
        # get predicted cats
        predictions = doc.cats
        print("cats:")
        print(predictions)
        # get predicted cat
        cat = max(predictions, key=predictions.get)
        print(cat)
        # list of words to search based on cat (in progress)
        cat_word_list = [str(cat)]

        return predictions, cat_word_list

    # get list of important words for search params

    def get_constituents(quote):
        # spaCy tokenization
        doc = nlp(quote)

        # get noun chunks (lemma)
        n_chunks = [[word.lemma_ for word in chunk if not word.is_stop]
                    for chunk in doc.noun_chunks]

        # get important verbs (lemma)
        v_chunks = [[tok.lemma_] for tok in doc if tok.dep_ in [
            'pcomp', 'xcomp', 'ccomp', 'advcl']]

        # make total list
        const_list = [' '.join(item) for item in n_chunks + v_chunks if item]

        print("constituents: ")
        print(const_list)
        return const_list

    # prepare words for params (need to redo)

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

    # create title
    title = create_title(quote)
    # get categories and category words
    cats, cat_words = get_cats(quote)
    # get words (max 4)
    words = get_constituents(quote)
    if len(words) > 4:
        words = random.sample(words, 4)
    words += cat_words
    print("words: ")
    print(words)
    # get list of words
    word_list = word_list_combo(words)

    # list of Musixmatch genre id's
    genre_ids = {'all': 34, 'blues': 2, 'comedy': 3, 'children': 4, 'classical': 5, 'country': 6,
                 'electronic': 7, 'holiday': 8, 'opera': 9, 'folk': 10, 'jazz': 11,
                 'latin': 12, 'new age': 13, 'pop': 14,  'randb': 15, 'soundtrack': 16,
                 'dance': 17, 'rap': 18, 'world': 19, 'alternative': 20, 'rock': 21,
                 'christian': 22, 'vocal': 23, 'reggae': 24, 'k-pop': 51}

    # get parameters for Musixmatch query
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

    for word in word_list:
        if pop == 0:
            lenlist = [len(word)*4, 0]
        if pop == 100:
            lenlist = [0, len(word)*4]
        elif pop < 40:
            lenlist = [len(word)*3, len(word)]
        elif 40 <= pop <= 70:
            lenlist = [len(word)*2, len(word)*2]
        elif pop > 70:
            lenlist = [len(word), len(word)*3]

        for genre in genres:
            parameter1 = parameters(
                word, genre_ids[genre], lenlist[0], 'none')
            parameter2 = parameters(
                word, genre_ids[genre], lenlist[1], 'desc')

            song_dicts.append(get_song_list(parameter1))
            song_dicts.append(get_song_list(parameter2))

    song_list = dict(chain.from_iterable(d.items() for d in song_dicts))

    songs = {}

    for song, artist in song_list.items():
        if song not in songs.keys():
            songs[song] = artist

    print("songs: ")
    print(songs)

    # if len(songs) < 10:
    #     more_words = get_more_constituents(quote)
    #     print("more words: ")
    #     print(more_words)
    #     for word in more_words:
    #         for genre in genres:
    #             parameter1 = parameters(
    #                 word, genre_ids[genre], len(list)*2, 'none')
    #             parameter2 = parameters(
    #                 word, genre_ids[genre], len(list)*3, 'desc')

    #             song_dicts.append(get_song_list(parameter1))
    #             song_dicts.append(get_song_list(parameter2))
    #     song_list = dict(chain.from_iterable(d.items() for d in song_dicts))
    #     for song, artist in song_list.items():
    #         if song not in songs.keys():
    #             songs[song] = artist

    #     print("new songs: ")
    #     print(songs)

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
        user['id'], title, public=vis, collaborative=False, description=description)

    playlist_id = playlist['id']
    sp.user_playlist_add_tracks(
        user['id'], playlist_id, track_id_list, position=None)

    return


make_playlist(quote, genre_list, vis, pop)

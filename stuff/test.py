import spacy
import random
import re
import classy_classification
import json


textcat = spacy.load(
    '/home/victoriaslocum/synsong/poetry_class/output/model-best')
nlp = spacy.load('en_core_web_sm')

quote = "The greatest glory in living lies not in never falling, but in rising every time we fall."

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

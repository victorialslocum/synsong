import spacy
import random
import re
import classy_classification
import json


nlp = spacy.load('/home/victoriaslocum/synsong/poetry_class/output/model-best')

# textcat = nlp.add_pipe("textcat_multilabel")
# textcat.from_disk(
#     "/home/victoriaslocum/synsong/poetry_class/output/model-best")
quote = "They say a person needs just three things to be truly happy in this world: Someone to love, something to do, and something to hope for."

# quote themes: love, life, happiness, sadness, music, inspirational


def get_cats(quote):
    doc = nlp(quote)
    predictions = doc.cats
    print(predictions)
    return predictions


words = get_cats(quote)

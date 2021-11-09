import spacy
from sense2vec import Sense2VecComponent

nlp = spacy.load("en_core_web_sm")
s2v = nlp.add_pipe("sense2vec")
s2v.from_disk("./s2v_old")


# def most_similar(word):
#     queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
#     by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
#     return by_similarity[:10]

# print(nlp.vocab[u'dog'].cluster)

doc = nlp("food")
most_similar = doc[0]._.s2v_most_similar(3)
other_senses = doc[0]._.s2v_other_senses(3)
print(most_similar)
print(other_senses)
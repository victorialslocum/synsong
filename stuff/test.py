import spacy
import random
import re
# import crosslingual_coreference

nlp = spacy.load('en_core_web_sm')
# nlp.add_pipe(
#     "xx_coref", config={})

quote = "The way to get started is to quit talking and begin doing."

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
print(title)

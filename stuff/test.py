import spacy
import random
# import crosslingual_coreference

nlp = spacy.load('en_core_web_sm')
# nlp.add_pipe(
#     "xx_coref", config={})

prompt = "Rainbows are full of colorful water that splashes when you're wet"


def create_title(prompt):
    doc = nlp(prompt)

    title_list_v = [[child.text for child in tok.subtree if child.dep_ not in ['aux', 'neg']]
                    for tok in doc if tok.pos_ in ['VERB', 'AUX'] and tok.dep_ in ['pcomp', 'xcomp', 'advcl', 'ccomp']]

    title_list_n = [[child.text for child in tok.subtree] for tok in doc if tok.pos_ in
                    ['NOUN', 'ADJ'] and tok.dep_ in ['nsubj', 'pobj']]

    title_list = [item for item in
                  title_list_v + title_list_n if 3 < len(item) < 8]

    title = ''
    if title_list:
        title = ' '.join(random.sample(title_list, 1)[0])
    else:
        title_list_new = [chunk.text for chunk in doc.noun_chunks]

        title = max(title_list_new, key=len) if title_list_new else prompt

    return title


title = create_title(prompt)
print(title)

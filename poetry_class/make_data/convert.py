import spacy
import json
from spacy.tokens import DocBin
from pathlib import Path


f = open('poetry_class/data/data.json')
data = json.load(f)

t_f = open('poetry_class/data/test_data.json')
test_data = json.load(t_f)

nlp = spacy.load("en_core_web_sm")


def convert(data, output_path: Path):

    db = DocBin()
    for line in data:
        doc = nlp.make_doc(line["text"])
        doc.cats = line["cats"]
        db.add(doc)
    db.to_disk(output_path)


convert(data, "poetry_class/spacy_db/train.spacy")

convert(test_data, "poetry_class/spacy_db/dev.spacy")

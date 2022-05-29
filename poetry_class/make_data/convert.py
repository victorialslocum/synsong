import spacy
import json
from spacy.tokens import DocBin
from pathlib import Path

# Opening JSON file
f = open('poetry_class/test_data.json')

# returns JSON object as
# a dictionary
data = json.load(f)

nlp = spacy.load("en_core_web_sm")


def convert(data, output_path: Path):

    db = DocBin()
    for line in data:
        doc = nlp.make_doc(line["text"])
        doc.cats = line["cats"]
        db.add(doc)
    db.to_disk(output_path)


convert(data, "poetry_class/dev.spacy")

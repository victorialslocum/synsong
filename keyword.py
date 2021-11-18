import spacy
nlp = spacy.load("en_core_web_sm")

prompt = "Beans are only cold when its below a cold temperature in Nebraska"

doc = nlp(prompt)

print(doc.ents)
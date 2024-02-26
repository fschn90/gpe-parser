import json
import spacy

data = []
with open('test_articles.json') as articles:
    opened = json.load(articles)
    for i in opened:
        data.append(i['story'])

# nlp = spacy.load("de_core_news_sm")
nlp = spacy.load("de_core_news_lg")

for i in data:
    doc = nlp(i)
    for ent in doc.ents:
        if ent.label_ == "LOC":
            print(ent.text, ent.label_)


# nlp = spacy.load("de_core_news_lg")
# doc = nlp(data[1])
# for ent in doc.ents:
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)
#

# for i in data:
#     doc = nlp(i)
#     for token in doc:
#         if token.ent_type_ == "LOC":
#             print(token.text, token.ent_type_)

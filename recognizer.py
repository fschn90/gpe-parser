import json
import spacy

## get data, sql call for articles not recognised yet 

data = []
with open('test_articles.json') as articles:
    opened = json.load(articles)
    for i in opened:
        data.append(i['story'])


## recognise gpes
nlp = spacy.load("de_core_news_lg")
for i in data:
    doc = nlp(i)
    for ent in doc.ents:
        if ent.label_ == "LOC":
            print(ent.text, ent.label_)


## dump gpes into database per url

## dump gpes into database per gpe

## count ukraine

## enrich gpe data 

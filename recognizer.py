import json
import spacy

with open('test_articles.json') as articles:
    opened = json.load(articles)
    for i in opened:
        print(i['story'])

#nlp = spacy.load("de_core_news_sm")



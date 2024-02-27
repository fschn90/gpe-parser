import spacy
import pymysql
from dotenv import load_dotenv
import os

# loading database credentials 

#load_dotenv("../SETUP/.env")
load_dotenv("./.env")

dbconnection = pymysql.connect(
            host=os.environ.get("NMprod_db_domain"),
            user=os.environ.get("dbuser"),
            password=os.environ.get("dbpass"),
            db=os.environ.get("dbnamePrs"),
            charset=os.environ.get("dbCharst"),
            cursorclass=pymysql.cursors.DictCursor,
        )
cursor = dbconnection.cursor()

# loading data to be parsed from database TO-DO: (accounting for data already parsed)
sqlQuery = f"""SELECT *, 'derstandard' as paper from {os.environ.get("derstandardPrs")} ORDER BY ID DESC LIMIT 2
            ;"""
cursor.execute(sqlQuery)
results = cursor.fetchall()
#print(results)

# closing connection to db                                                                                                                                
dbconnection.close()

# parsing gpe from articles
parsed_data = []
nlp = spacy.load("de_core_news_lg")
for result in results:
    data =[]
    Doc = nlp("; ".join([result['story'], result['headline'], result['subtext']]))
    for ent in Doc.ents:
        if ent.label_ == "LOC":
            data.append(ent.text)
    parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'gpe': data})
print(parsed_data)


## dump gpes into database per url

## dump gpes into database per gpe

## count ukraine

## enrich gpe data 

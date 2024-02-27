import json
import spacy
import pymysql
from dotenv import load_dotenv
import os

# loading database credentials 

#load_dotenv("../SETUP/.env")
load_dotenv("./.env")
host = os.environ.get("NMprod_db_domain")
user = os.environ.get("dbuser")
password = os.environ.get("dbpass")
dbPrs = os.environ.get("dbnamePrs")
dbAna = os.environ.get("dbnameAna")
charset = os.environ.get("dbCharst")
tableArsDe = os.environ.get("derstandardPrs")
# tableArsKr = os.environ.get("kroneArs")
# tableArsOr = os.environ.get("orfArs")
# tableArsOe = os.environ.get("oe24Ars")
# tableMonthly = os.environ.get("monthlyArs")


dbconnection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=dbPrs,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor,
        )
cursor = dbconnection.cursor()

# loading data to be parsed from database (accounting for data already parsed)
sqlQuery = f"""SELECT * from {tableArsDe} ORDER BY ID DESC LIMIT 1
            ;"""
cursor.execute(sqlQuery)
resultsDerstandard = cursor.fetchall()

# closing connection to db                                                                                                                                
dbconnection.close()







## get data, sql call for articles not recognised yet 

# data = []
# with open('test_articles.json') as articles:
#     opened = json.load(articles)
#     for i in opened:
#         data.append(i['story'])


# ## recognise gpes
# nlp = spacy.load("de_core_news_lg")
# for i in data:
#     doc = nlp(i)
#     for ent in doc.ents:
#         if ent.label_ == "LOC":
#             print(ent.text, ent.label_)


## dump gpes into database per url

## dump gpes into database per gpe

## count ukraine

## enrich gpe data 

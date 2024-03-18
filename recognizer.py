import spacy
from collections import Counter
import json
import pymysql
from dotenv import load_dotenv
import os

load_dotenv(".env")

results = []
tables = ['orfPrs', 'kronePrs', 'derstandardPrs', 'oe24Prs']
for table in tables:
    #### loading data to be parsed from database
    dbconnection = pymysql.connect(
                host=os.environ.get("NMprod_db_domain"),
                user=os.environ.get("dbuser"),
                password=os.environ.get("dbpass"),
                charset=os.environ.get("dbCharst"),
                cursorclass=pymysql.cursors.DictCursor,
            )
    cursor = dbconnection.cursor()
    sqlQuery = f"""SELECT *, '{os.environ.get(table)}' as paper from {os.environ.get('dbnamePrs')}.{os.environ.get(table)} 
                    WHERE link NOT IN (SELECT link FROM {os.environ.get('dbnameAna')}.gpeArticles WHERE paper = '{os.environ.get(table)}');""" 
    cursor.execute(sqlQuery)
    outputs = cursor.fetchall()
    for output in outputs:
        results.append(output)
    dbconnection.close()


#### parsing gpe from articles
parsed_data = []
nlp = spacy.load("de_core_news_lg")
for result in results:
    data =[]
    Doc = nlp("; ".join([result['story'], result['headline'], result['subtext']]))
    for ent in Doc.ents:
        if ent.label_ == "LOC":
            data.append(ent.text)
    countedGpes = Counter(data)
    jsonGpes = json.dumps(countedGpes, sort_keys=True, default=str, ensure_ascii=False)
    parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result['author'], 'gpe':jsonGpes, 'scrapeDate':result['scrapeDate']})


#### dump gpes into database per url
dbconnection = pymysql.connect(
            host=os.environ.get("NMprod_db_domain"),
            user=os.environ.get("dbuser"),
            password=os.environ.get("dbpass"),
            db=os.environ.get("dbnameAna"),
            charset=os.environ.get("dbCharst"),
            cursorclass=pymysql.cursors.DictCursor,
        )
cursor = dbconnection.cursor()

for article in parsed_data:
    cursor.execute(f'''
        INSERT INTO gpeArticles
        (link,
        paper,
        author, 
        gpes,
        scrapeDate,
        parseDate) 
        VALUES 
        (%s, %s, %s, %s, %s, NOW())''', 
    [article['link'], article['paper'], article['author'], article['gpe'], article['scrapeDate']])
    dbconnection.commit()  
dbconnection.close()
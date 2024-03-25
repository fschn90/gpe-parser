import spacy
from collections import Counter
import json
import pymysql
from dotenv import load_dotenv
import os
import datetime
import pprint

# start of logging
logStats = {}
logStats['start_time'] = datetime.datetime.now()
logStats['job'] = 'gpeCounter'
logStats['articlesAnalysed/orf'] = 0
logStats['articlesAnalysed/derstandard'] = 0
logStats['articlesAnalysed/oe24'] = 0
logStats['articlesAnalysed/krone'] = 0
logStats['articlesAnalysed/vol'] = 0
logStats['gpesCounted/orf'] = 0
logStats['gpesCounted/derstandard'] = 0
logStats['gpesCounted/oe24'] = 0
logStats['gpesCounted/krone'] = 0
logStats['gpesCounted/vol'] = 0

load_dotenv("../SETUP/.env")

results = []
tables = ['orfPrs', 'kronePrs', 'derstandardPrs', 'oe24Prs', 'volPrs']
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
                    WHERE link NOT IN (SELECT link FROM {os.environ.get('dbnameAna')}.{os.environ.get('gpeCou')} WHERE paper = '{os.environ.get(table)}') LIMIT 500;""" 
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
    logStats[f'articlesAnalysed/{result["paper"]}'] += 1
    filtered = {k: v for k, v in result.items() if v is not None}
    result.clear()
    result.update(filtered)
    Doc = nlp("; ".join([result.get('story', " "), result.get('headline'," "), result.get('subtext'," ")]))
    for ent in Doc.ents:
        if ent.label_ == "LOC":
            data.append(ent.text)
    countedGpes = Counter(data)
    logStats[f'gpesCounted/{result["paper"]}'] += sum(countedGpes.values())
    jsonGpes = json.dumps(countedGpes, sort_keys=True, default=str, ensure_ascii=False)
    parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result.get('author', None), 'gpe':jsonGpes, 'scrapeDate':result.get('scrapeDate', None)})


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

# some more logging
logStats['finish_time'] = datetime.datetime.now()
logStats['elapsed_time'] = logStats['finish_time'] - logStats['start_time']

# converting stats dict into json 
logStats = {key:val for key, val in logStats.items() if val != 0}
stt = json.dumps(logStats, sort_keys=True, default=str)
try:
    # pushing stats as json to db 
    cursor.execute(f"INSERT INTO {os.environ.get('dbnameAna')}.{os.environ.get('mainLogAna')} (logStats, finishTime) VALUES (%s, %s)", [stt, logStats['finish_time']])
    dbconnection.commit() 
except pymysql.Error as e:
    print(e)         
# closing connection to db
dbconnection.close()

pprint.pprint(logStats)

import spacy
from collections import Counter
import json
import pymysql
from dotenv import load_dotenv
import os
import datetime
from loggi import logger

# load_dotenv("../SETUP/.env")
# load_dotenv("SETUP/.env")
load_dotenv("./.env")


 

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
    # logStats[f'articlesAnalysed/{result["paper"]}'] += 1
    logger.logStats[f'articlesAnalysed/{result["paper"]}'] += 1
    filtered = {k: v for k, v in result.items() if v is not None}
    result.clear()
    result.update(filtered)
    Doc = nlp("; ".join([result.get('story', " "), result.get('headline'," "), result.get('subtext'," ")]))
    for ent in Doc.ents:
        if ent.label_ == "LOC":
            data.append(ent.text)
    countedGpes = Counter(data)
    # logStats[f'gpesCounted/{result["paper"]}'] += sum(countedGpes.values())
    logger.logStats[f'gpesCounted/{result["paper"]}'] += sum(countedGpes.values())
    jsonGpes = json.dumps(countedGpes, sort_keys=True, default=str, ensure_ascii=False)
    parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result.get('author', None), 'gpe':jsonGpes, 'scrapeDate':result.get('scrapeDate', None)})

#### dump gpes into database per url
try:
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
except Exception as e:
    logger.logStats['error'] = e
    logger.logStats['last_items_before_error'] = json.dumps(article, sort_keys=True, default=str)
    logger.transformingDump()
finally:
    dbconnection.close()

logger.transformingDump()
import spacy
import pymysql
from dotenv import load_dotenv
import os

#load_dotenv("../SETUP/.env")
load_dotenv("./.env")

#### passing articles where gpes already parsed to sql call to avoid double parsing 
dbconnection = pymysql.connect(
            host=os.environ.get("NMprod_db_domain"),
            user=os.environ.get("dbuser"),
            password=os.environ.get("dbpass"),
            db=os.environ.get("dbnameAna"),
            charset=os.environ.get("dbCharst"),
            cursorclass=pymysql.cursors.DictCursor,
        )
cursor = dbconnection.cursor()

sqlQuery = f"""SELECT link FROM gpeArticles;"""
cursor.execute(sqlQuery)
resulted = cursor.fetchall()
resulted_list = [i['link'] for i in resulted]

# closing connection to db                                                                                                                                
dbconnection.close()


#### loading data to be parsed from database
dbconnection = pymysql.connect(
            host=os.environ.get("NMprod_db_domain"),
            user=os.environ.get("dbuser"),
            password=os.environ.get("dbpass"),
            db=os.environ.get("dbnamePrs"),
            charset=os.environ.get("dbCharst"),
            cursorclass=pymysql.cursors.DictCursor,
        )
cursor = dbconnection.cursor()

in_params = ','.join(['%s'] * len(resulted_list))
sqlQuery = f"""SELECT *, 'derstandard' as paper from {os.environ.get("derstandardPrs")} 
                WHERE link NOT IN (%s)
            ;""" % in_params
cursor.execute(sqlQuery, resulted_list)
results = cursor.fetchall()

# closing connection to db                                                                                                                                
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
    #### draft, to do check data first, check output of countedGpes and then drop tables and insert tables and data newly
    from collections import Counter
    import json
    countedGpes = Counter(data)
    jsonGpes = json.dumps(countedGpes, sort_keys=True, default=str, ensure_ascii=False)
    parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result['author'], 'gpe':jsonGpes, 'scrapeDate':result['scrapeDate']})
    # parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result['author'], 'gpe':data, 'scrapeDate':result['scrapeDate']})



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
    # [article['link'], article['paper'], article['author'], "; ".join(article['gpe']), article['scrapeDate']])
    dbconnection.commit()  

# closing connection to db                                                                                                                                
dbconnection.close()

## merge recogniser and counter into one, converting gpes dict into json and insert json directly into sql

## enrich gpe data, later TO-DO

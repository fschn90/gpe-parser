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

#### get previously recognised gpes  
sqlQuery = f"""SELECT * FROM gpeArticles LIMIT 3;"""
cursor.execute(sqlQuery)
resulted = cursor.fetchall()
resulted_list = [i['gpe'] for i in resulted]

#### first add unique gpes as columns to table, then second count gpes in article 
for result in resulted:
    # check gpes already in columns
    sqlQuery = f"""select column_name from information_schema.columns where table_schema = 'austrian_news_analysing' and table_name = 'gpeCounted'"""
    cursor.execute(sqlQuery)
    columns_result = cursor.fetchall()
    alreadyCounted = [column['column_name'] for column in resulted]
    # add gpes not yet in columns
    if result['gpes'] is not None:
            for gpe in result['gpes'].split('; '):
                    if gpe not in alreadyCounted:
                        alreadyCounted.append(gpe)
                        sqlQuery = f"""ALTER TABLE gpeCounted ADD {gpe} INT;"""
                        cursor.execute(sqlQuery)


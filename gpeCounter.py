import spacy
import pymysql
from dotenv import load_dotenv
import os
from collections import Counter

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
sqlQuery = f"""SELECT * FROM gpeArticles WHERE link NOT IN (SELECT link FROM gpeCounted) order by id desc LIMIT 10;"""
cursor.execute(sqlQuery)
resulted = cursor.fetchall()
# resulted_list = [i['gpes'].split('; ') for i in resulted]
# print(resulted_list)

#### first add unique gpes as columns to table, then second count gpes in article 
for result in resulted:


    ### TO-DO: move check of gpes already in columsn out of loop, only needs to be done once and then simple list.append() in loop for added gpes
    # check gpes already in columns
    sqlQuery = f"""select column_name from information_schema.columns where table_schema = 'austrian_news_analysing' and table_name = 'gpeCounted';"""
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
                        dbconnection.commit()

    #### TO-DO: fix error here:  cursor.execute(query.format(columns, placeholders), values) -> TypeError: not enough arguments for format string

    # counting gpes 
    countedGpes = Counter(result)
    ### https://stackoverflow.com/questions/22920842/using-pythons-dictionarys-to-create-a-generic-mysql-insert-string
    query = 'INSRET INTO gpeCounted ({0}) VALUES ({1})'
    columns = ','.join(countedGpes.keys())
    placeholders = ','.join(['%s'] * len(countedGpes))
    values = countedGpes.values()
    cursor.execute(query.format(columns, placeholders), values)
    dbconnection.commit()


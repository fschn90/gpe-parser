import spacy
from collections import Counter
import json
import pymysql
from dotenv import load_dotenv
import os
import datetime



class classyLogStats():
    """Custom logging and dumping logs into database."""

    def __init__(self):
        self.logStats = {}
        self.logStats['start_time'] = datetime.datetime.now()
        self.logStats['job'] = 'gpeCounter'

    def incLog(self, key, value=1):
        if key not in self.logStats:
            self.logStats[key] = value
        else:
            self.logStats[key] += value
    
    def transformingLogDump(self, dbCredentials):
        self.logStats['finish_time'] = datetime.datetime.now()
        self.logStats['elapsed_time'] = self.logStats['finish_time'] - self.logStats['start_time']
        self.logStats = {key:val for key, val in self.logStats.items() if val != 0}
        self.stt = json.dumps(self.logStats, sort_keys=True, default=str)
        try:
            dbconnection = pymysql.connect(
                        host=os.environ.get(dbCredentials['host']),
                        user=os.environ.get(dbCredentials['user']),
                        password=os.environ.get(dbCredentials['password']),
                        charset=os.environ.get(dbCredentials['charset']),
                        cursorclass=pymysql.cursors.DictCursor,
                    )
            cursor = dbconnection.cursor()
            cursor.execute(f"INSERT INTO {os.environ.get('dbnameAna')}.{os.environ.get('mainLogAna')} (logStats, finishTime) VALUES (%s, %s)", [self.stt, self.logStats['finish_time']])
            dbconnection.commit()
        except pymysql.Error as e:
            print(e)         
        finally:
            dbconnection.close()
            print(self.logStats)



class gpeRecognizer(classyLogStats):
    """Getting articles out of database, the using spacy to parse geopolitical entities and then dumping the results back into database."""

    def __init__(self, envPath=".env"):
        classyLogStats.__init__(self)
        load_dotenv(envPath)
 
    def getArticles(self, dbCredentials, tables):
        self.results = []
        try:
            dbconnection = pymysql.connect(
                        host=os.environ.get(dbCredentials['host']),
                        user=os.environ.get(dbCredentials['user']),
                        password=os.environ.get(dbCredentials['password']),
                        charset=os.environ.get(dbCredentials['charset']),
                        cursorclass=pymysql.cursors.DictCursor,
                    )
            for table in tables:
                cursor = dbconnection.cursor()
                sqlQuery = f"""SELECT *, '{os.environ.get(table)}' as paper from {os.environ.get('dbnamePrs')}.{os.environ.get(table)} 
                                WHERE link NOT IN (SELECT link FROM {os.environ.get('dbnameAna')}.{os.environ.get('gpeCou')} WHERE paper = '{os.environ.get(table)}') LIMIT 500;""" 
                cursor.execute(sqlQuery)
                outputs = cursor.fetchall()
                for output in outputs:
                    self.results.append(output)
        except pymysql.Error as e:
            print(e)         
        finally:
            dbconnection.close()

    def parsing(self):
        self.parsed_data = []
        nlp = spacy.load("de_core_news_lg")
        for result in self.results:
            data =[]
            self.incLog('articlesAnalysed')
            self.incLog(f'articlesAnalysed/{result["paper"]}')
            filtered = {k: v for k, v in result.items() if v is not None}
            result.clear()
            result.update(filtered)
            Doc = nlp("; ".join([result.get('story', " "), result.get('headline'," "), result.get('subtext'," ")]))
            for ent in Doc.ents:
                if ent.label_ == "LOC":
                    data.append(ent.text)
            countedGpes = Counter(data)
            self.incLog('gpesCounted', sum(countedGpes.values()))
            self.incLog(f'gpesCounted/{result["paper"]}', sum(countedGpes.values()))
            jsonGpes = json.dumps(countedGpes, sort_keys=True, default=str, ensure_ascii=False)
            self.parsed_data.append({'link':f"{result['link']}", 'paper':result['paper'], 'author':result.get('author', None), 'gpe':jsonGpes, 'scrapeDate':result.get('scrapeDate', None)})

    def dumping(self, dbCredentials):
        try:
            dbconnection = pymysql.connect(
                        host=os.environ.get(dbCredentials['host']),
                        user=os.environ.get(dbCredentials['user']),
                        password=os.environ.get(dbCredentials['password']),
                        charset=os.environ.get(dbCredentials['charset']),
                        cursorclass=pymysql.cursors.DictCursor,
                        )        
            cursor = dbconnection.cursor()
            for article in self.parsed_data:
                cursor.execute(f'''
                    INSERT INTO {os.environ.get('dbnameAna')}.{os.environ.get('gpeCou')}
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
            self.logStats['error'] = e
            self.logStats['last_items_before_error'] = json.dumps(article, sort_keys=True, default=str)
            self.transformingLogDump(dbCredentials)
        finally:
            dbconnection.close()
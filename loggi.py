import json
from dotenv import load_dotenv
import os
import datetime
import pymysql

class classyLogStats():

    def __init__(self):
        load_dotenv('.env')
        self.logStats = {}
        self.logStats['start_time'] = datetime.datetime.now()
        self.logStats['job'] = 'gpeCounter'
        self.logStats['articlesAnalysed/orf'] = 0
        self.logStats['articlesAnalysed/derstandard'] = 0
        self.logStats['articlesAnalysed/oe24'] = 0
        self.logStats['articlesAnalysed/krone'] = 0
        self.logStats['articlesAnalysed/vol'] = 0
        self.logStats['gpesCounted/orf'] = 0
        self.logStats['gpesCounted/derstandard'] = 0
        self.logStats['gpesCounted/oe24'] = 0
        self.logStats['gpesCounted/krone'] = 0
        self.logStats['gpesCounted/vol'] = 0 

    def transformingDump(self):
        self.logStats['finish_time'] = datetime.datetime.now()
        self.logStats['elapsed_time'] = self.logStats['finish_time'] - self.logStats['start_time']
        self.logStats = {key:val for key, val in self.logStats.items() if val != 0}
        self.stt = json.dumps(self.logStats, sort_keys=True, default=str)
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
            cursor.execute(f"INSERT INTO {os.environ.get('dbnameAna')}.{os.environ.get('mainLogAna')} (logStats, finishTime) VALUES (%s, %s)", [self.stt, self.logStats['finish_time']])
            dbconnection.commit()
        except pymysql.Error as e:
            print(e)         
        # closing connection to db
        finally:
            dbconnection.close()
            print(self.logStats)


logger = classyLogStats() 
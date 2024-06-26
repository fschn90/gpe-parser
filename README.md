# GPE parser

identifying and parsing Geopolitical Entities based on spacy in news paper articles, which are retrieved from a mysql database.

Setup:

- one .env file with MySQL credentials
- two databases, one for articles and one as destination for parsed GPEs

## Installing requirements

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Example .env file

```env
# .env
db_host=localhost
db_user=user
db_pass=password
db_charset=utf8mb

db_name_articles=news_articles      # database as source of articles
nyt=new_york_times
zeit=zeit
scmp=south_china_morning_post

db_name_gpes=news_gpes      # database as destionation of parsed gpes
gpes=gpes_count
log=mainLogStat
```

## Running the GPE parser

Notes regarding the dictionaries provieded when initializing the gpeParser object:

- keys need to keep the same name as blow
- values need to be in line with the .env file

```python
# main.py
from gpeParser import gpeParser

# initializing the gpeParser object with the relevant db credentials, db names, and db table names
razer = gpeParser(
    dbCredentials={'host':'db_host','user':'db_user','password':'db_pass','charset':'db_charset'},
    dbNames={'dbNameGpes': 'db_name_gpes', 'dbNameArticles':'db_name_articles'},
    dbTables={'dbTableLogging':'log', 'dbTableGpes': 'gpes'}
    )

# retriving the articles, note: each news paper has its own db table and its very important to probide the paperTables exactly as specified in .env file
razer.gettingArticles(paperTables=['nyt', 'zeit', 'scmp'])

# parsing gpes from articles
razer.parsing()

# dumping parsed gpes into destination database
razer.dumping()

# dumping Log
razer.logging()

```

## Structure of mysql databases

```sql
use news_gpes;
CREATE TABLE gpeArticles (
    id SERIAL,
    link VARCHAR(256),
    paper VARCHAR(256),
    author VARCHAR(256),
    gpes JSON,
    scrapeDate DATETIME,
    parseDate DATETIME
);
CREATE TABLE mainLogStats (
    id SERIAL,
    logStats JSON,
    finishTime DATETIME
);

use news_articles;
CREATE TABLE new_york_times (
    id SERIAL,
    link VARCHAR(256);
    story TEXT;
    author TEXT;
    headline TEXT;
    subtext TEXT;
    scrapeDate DATETIME,
    parseDate DATETIME
);

-- same structure for tables of zeit and south_china_morning_post as new_york_times just above

```

## Example log

```bash
{
    'start_time': datetime.datetime(2024, 4, 27, 19, 3, 59, 972022),
    'job': 'gpeParser',
    'articlesAnalysed': 28,
    'articlesAnalysed/nyt': 7,
    'gpesCounted': 274,
    'gpesCounted/nyt': 84,
    'articlesAnalysed/zeit': 9,
    'gpesCounted/zeit': 117,
    'articlesAnalysed/scmp': 1,
    'gpesCounted/scmp': 11,
    'finish_time': datetime.datetime(2024, 4, 27, 19, 4, 20, 149128),
    'elapsed_time': datetime.timedelta(seconds=20, microseconds=177106)
}
```

-- creating tables

use austrian_news_analysing;
CREATE TABLE gpeArticles (
    id SERIAL, 
    link varchar(256),
    paper varchar(256),
    author TEXT,
    gpes TEXT,
    scrapeDate DATETIME,
    parseDate DATETIME
);
INSERT INTO gpeArticles (link, paper)
VALUES ('test.com', 'testPaper');


use austrian_news_analysing;
CREATE TABLE gpeCounted (
    id SERIAL, 
    link varchar(256),
    paper varchar(256),
    author TEXT,
    scrapeDate DATETIME,
    parseDate DATETIME
);
INSERT INTO gpeArticles (link, paper)
VALUES ('test.com', 'testPaper');


-- use austrian_news_analysing;
-- CREATE TABLE gpeDictionary (
--     gpes TEXT,
--     parseDATE DATETIME
-- );

-- use austrian_news_analysing;
-- CREATE TABLE gpe_dictionary (
--     gpes TEXT,
--     parseDATE DATETIME
-- );


-- droping tables

use austrian_news_analysing;
DROP TABLE gpeArticles;


-- deleteing test dummy
DELETE FROM gpeArticles WHERE link='test.com' AND paper="testPaper";
DELETE FROM gpeCounted WHERE link='test.com' AND paper="testPaper";
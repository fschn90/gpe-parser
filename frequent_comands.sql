-- creating tables
use austrian_news_analysing;
CREATE TABLE gpeArticles (
    id SERIAL, 
    link varchar(256),
    paper varchar(256),
    author varchar(256),
    gpes JSON,
    scrapeDate DATETIME,
    parseDate DATETIME
);
INSERT INTO gpeArticles (link, paper)
VALUES ('test.com', 'testPaper');


-- droping tables
use austrian_news_analysing;
DROP TABLE gpeArticles;


-- deleteing test dummy
DELETE FROM gpeArticles WHERE link='test.com' AND paper="testPaper";


-- ukraine counter DRAFT
SELECT 
  scrapeDate as "time",
  cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) as "word count Ukraine  
FROM austrian_news_analysing.gpeArticles
where cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) is not NULL
ORDER BY ID DESC;

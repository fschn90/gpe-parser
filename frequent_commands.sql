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
(CASE WHEN (paper = "orf") THEN cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) END) as "orf",
(CASE WHEN (paper = "derstandard") THEN cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) END) as "derstandard",
(CASE WHEN (paper = "krone") THEN cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) END) as "krone",
(CASE WHEN (paper = "oe24") THEN cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) END) as "oe24",
(CASE WHEN (paper = "vol") THEN cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) END) as "vol"
FROM austrian_news_analysing.gpeArticles
where cast(JSON_EXTRACT(gpes, "$.Ukraine") as decimal) is not NULL
ORDER BY ID DESC
-- LIMIT 500;

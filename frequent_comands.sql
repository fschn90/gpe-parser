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
-- TEMPLATE
-- SELECT 
--   CAST(JSON_UNQUOTE(JSON_EXTRACT(logStats, "$.finish_time")) AS DATETIME) as "time",
--   (case when JSON_UNQUOTE(JSON_EXTRACT(logStats, "$.spider_name")) = "links" then cast(JSON_EXTRACT(logStats, "$.item_scraped_count/orf/new_item") as decimal) else NULL end) as Links,
--   (case when JSON_UNQUOTE(JSON_EXTRACT(logStats, "$.spider_name")) = "landingpage" then cast(JSON_EXTRACT(logStats, "$.item_scraped_count/orf/landingpage_changed") as decimal) else NULL end) as Landingpage,
--   (case when JSON_UNQUOTE(JSON_EXTRACT(logStats, "$.spider_name")) = "articles" then cast(JSON_EXTRACT(logStats, "$.item_scraped_count/orf/new_article") as decimal) else NULL end) as Articles
-- FROM mainLogStats
-- where cast(JSON_EXTRACT(logStats, "$.item_scraped_count") as decimal) is not NULL
-- ORDER BY ID DESC
-- LIMIT 3000;
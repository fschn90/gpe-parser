-- creating tables

use austrian_news_analysing;
CREATE TABLE gpeArticles (
    id SERIAL, 
    link varchar(256),
    paper varchar(256),
    author TEXT,
    gpes TEXT,
    parseDATE DATETIME
);

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
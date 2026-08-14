

-- Dimension table: one row per ad campaign (describes each campaign)
CREATE TABLE campaigns (
    campaign_id   INT PRIMARY KEY,          -- unique id, no duplicates
    channel       TEXT NOT NULL,            -- Meta / Google / TikTok / LinkedIn
    campaign_name TEXT NOT NULL,
    objective     TEXT NOT NULL,            -- Awareness / Traffic / Conversions
    start_date    DATE NOT NULL,
    end_date      DATE NOT NULL,
    daily_budget  NUMERIC(10,2) NOT NULL    -- money -> NUMERIC, never FLOAT
);

-- Fact table: one row per campaign per day (the numbers we analyse)
CREATE TABLE daily_performance (
    date         DATE NOT NULL,
    campaign_id  INT NOT NULL REFERENCES campaigns(campaign_id),  -- foreign key
    impressions  INT NOT NULL,
    clicks       INT NOT NULL,
    spend        NUMERIC(10,2) NOT NULL,
    conversions  INT NOT NULL,
    revenue      NUMERIC(10,2) NOT NULL
);

-- Customer reviews (feeds the AI layer in Phase 4)
CREATE TABLE reviews (
    review_id    INT PRIMARY KEY,
    date         DATE NOT NULL,
    product      TEXT NOT NULL,
    rating       INT NOT NULL,               -- 1..5 stars
    review_text  TEXT NOT NULL
);

-- AI-derived layer: one label per review, kept SEPARATE from raw reviews
-- (so we can re-run the AI without touching original data)
CREATE TABLE review_labels (
    review_id INT PRIMARY KEY REFERENCES reviews(review_id),  -- FK: 1 label / 1 review
    sentiment TEXT NOT NULL,   -- positive / negative
    topic     TEXT NOT NULL    -- shipping / quality / price / support / other
);

-- Q5: What do unhappy customers complain about? (topics labelled by AI)
SELECT
    topic,
    COUNT(*) FILTER (WHERE sentiment = 'negative') AS complaints,  -- đếm có điều kiện (Postgres)
    COUNT(*) FILTER (WHERE sentiment = 'positive') AS praise,
    COUNT(*)                                       AS mentions
FROM review_labels
GROUP BY topic
ORDER BY complaints DESC;

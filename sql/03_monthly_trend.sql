-- Q3: Monthly trend — is overall performance improving over time?
SELECT
    DATE_TRUNC('month', d.date)::date         AS month,        -- gom về đầu tháng
    ROUND(SUM(d.spend))                       AS spend,
    ROUND(SUM(d.revenue))                     AS revenue,
    ROUND(SUM(d.revenue) / SUM(d.spend), 2)   AS roas,
    COUNT(DISTINCT d.campaign_id)             AS active_campaigns  -- số campaign chạy trong tháng
FROM daily_performance d
GROUP BY 1     -- = gom theo cột 1 (tháng)
ORDER BY 1;    -- theo thứ tự thời gian

-- Q2: Funnel efficiency by channel — explains WHY a channel wins or loses
SELECT
    c.channel,
    ROUND(100.0 * SUM(d.clicks)      / SUM(d.impressions), 2) AS ctr_pct,  -- 100.0 tránh bẫy integer
    ROUND(100.0 * SUM(d.conversions) / SUM(d.clicks),      2) AS cvr_pct,
    ROUND(SUM(d.spend) / SUM(d.clicks),      2)              AS cpc,
    ROUND(SUM(d.spend) / SUM(d.conversions), 2)              AS cac
FROM daily_performance d
JOIN campaigns c ON c.campaign_id = d.campaign_id
GROUP BY c.channel
ORDER BY cac ASC;   -- kênh có chi phí/khách RẺ nhất lên đầu

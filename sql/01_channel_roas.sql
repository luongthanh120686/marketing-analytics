-- Q1: Which channel is profitable? (ROAS = revenue per $1 spent)
SELECT
    c.channel,
    SUM(d.spend)                              AS total_spend,
    SUM(d.revenue)                            AS total_revenue,
    ROUND(SUM(d.revenue) / SUM(d.spend), 2)   AS roas
FROM daily_performance d
JOIN campaigns c ON c.campaign_id = d.campaign_id   -- ghép fact + dimension
GROUP BY c.channel                                   -- gom theo kênh
ORDER BY roas DESC;                                  -- kênh lời nhất lên đầu

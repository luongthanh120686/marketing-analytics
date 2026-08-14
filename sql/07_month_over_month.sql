-- Q6: Month-over-month ROAS change using a WINDOW function (LAG) + CTE
WITH monthly AS (                                    -- CTE: bảng tạm tính ROAS mỗi tháng
    SELECT DATE_TRUNC('month', date)::date AS month,
           ROUND(SUM(revenue) / SUM(spend), 2) AS roas
    FROM daily_performance
    GROUP BY 1
)
SELECT
    month,
    roas,
    LAG(roas) OVER (ORDER BY month)                  AS prev_roas,  -- ROAS tháng TRƯỚC
    ROUND(roas - LAG(roas) OVER (ORDER BY month), 2) AS change      -- tăng/giảm so tháng trước
FROM monthly
ORDER BY month;

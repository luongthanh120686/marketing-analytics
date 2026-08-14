-- Q4: Product satisfaction from reviews — numbers only (no reason WHY yet)
SELECT
    product,
    COUNT(*)                                        AS reviews,
    ROUND(AVG(rating), 2)                           AS avg_rating,
    SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END)    AS negative,      -- đếm có điều kiện
    ROUND(100.0 * SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END)
                / COUNT(*), 1)                      AS negative_pct
FROM reviews
GROUP BY product
ORDER BY avg_rating ASC;   -- sản phẩm điểm thấp lên đầu

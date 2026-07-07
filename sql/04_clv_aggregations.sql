-- 04_clv_aggregations.sql
-- Revenue per cohort member by month offset -> cumulative cohort CLV.
WITH first_order AS (
    SELECT c.customer_unique_id,
           DATE_TRUNC('month', MIN(o.order_purchase_timestamp)) AS cohort_month
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' GROUP BY 1
),
monthly_rev AS (
    SELECT c.customer_unique_id,
           DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
           SUM(oi.price + oi.freight_value) AS revenue
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered' GROUP BY 1, 2
)
SELECT f.cohort_month,
       DATE_DIFF('month', f.cohort_month, m.order_month) AS month_offset,
       SUM(m.revenue) AS revenue
FROM first_order f
JOIN monthly_rev m ON f.customer_unique_id = m.customer_unique_id
GROUP BY 1, 2 ORDER BY 1, 2;

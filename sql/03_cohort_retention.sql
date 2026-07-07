-- 03_cohort_retention.sql
-- Monthly acquisition cohorts vs active months -> triangular retention.
WITH first_order AS (
    SELECT c.customer_unique_id,
           DATE_TRUNC('month', MIN(o.order_purchase_timestamp)) AS cohort_month
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' GROUP BY 1
),
activity AS (
    SELECT c.customer_unique_id,
           DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month
    FROM orders o JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered' GROUP BY 1, 2
)
SELECT f.cohort_month,
       DATE_DIFF('month', f.cohort_month, a.order_month) AS month_offset,
       COUNT(DISTINCT a.customer_unique_id) AS active_customers
FROM first_order f
JOIN activity a ON f.customer_unique_id = a.customer_unique_id
GROUP BY 1, 2 ORDER BY 1, 2;

-- 02_rfm_metrics.sql
-- Recency / Frequency / Monetary at customer_unique_id grain.
-- Recency measured from snapshot date 2018-08-29 (dataset max order date).
WITH delivered AS (
    SELECT
        c.customer_unique_id,
        o.order_id,
        o.order_purchase_timestamp,
        SUM(oi.price + oi.freight_value) AS order_value
    FROM orders o
    JOIN customers c         ON o.customer_id = c.customer_id
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2, 3
)
SELECT
    customer_unique_id,
    DATE_DIFF('day', MAX(order_purchase_timestamp), DATE '2018-08-29') AS recency_days,
    COUNT(DISTINCT order_id)                                           AS frequency,
    SUM(order_value)                                                  AS monetary,
    AVG(order_value)                                                  AS avg_order_value
FROM delivered
GROUP BY customer_unique_id;

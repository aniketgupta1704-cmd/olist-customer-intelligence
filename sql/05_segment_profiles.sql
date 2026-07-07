-- 05_segment_profiles.sql
-- Per-customer geographic state + dominant product category (English).
-- Uses ROW_NUMBER() window function to pick each customer's top category.
WITH cust_state AS (
    SELECT DISTINCT
        c.customer_unique_id,
        FIRST_VALUE(c.customer_state) OVER (
            PARTITION BY c.customer_unique_id ORDER BY c.customer_id
        ) AS customer_state
    FROM customers c
),
cust_category AS (
    SELECT customer_unique_id, category_en FROM (
        SELECT
            c.customer_unique_id,
            COALESCE(t.product_category_name_english,
                     p.product_category_name, 'unknown') AS category_en,
            COUNT(*) AS n,
            ROW_NUMBER() OVER (
                PARTITION BY c.customer_unique_id ORDER BY COUNT(*) DESC
            ) AS rn
        FROM orders o
        JOIN customers c    ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p     ON oi.product_id = p.product_id
        LEFT JOIN category_translation t
               ON p.product_category_name = t.product_category_name
        WHERE o.order_status = 'delivered'
        GROUP BY 1, 2
    ) WHERE rn = 1
)
SELECT s.customer_unique_id, s.customer_state, c.category_en
FROM cust_state s
LEFT JOIN cust_category c ON s.customer_unique_id = c.customer_unique_id;

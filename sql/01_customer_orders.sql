-- 01_customer_orders.sql
-- Order-grain spine: one row per delivered order with customer, value, timing.
-- Joins: orders -> customers (customer_unique_id), orders -> order_items.
SELECT
    c.customer_unique_id,
    o.order_id,
    o.order_purchase_timestamp,
    o.order_status,
    COUNT(oi.order_item_id)              AS n_items,
    SUM(oi.price)                        AS items_value,
    SUM(oi.freight_value)                AS freight_value,
    SUM(oi.price + oi.freight_value)     AS order_value
FROM orders o
JOIN customers c         ON o.customer_id = c.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1, 2, 3, 4;

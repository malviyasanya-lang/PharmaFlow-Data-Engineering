{{ config(materialized='table', schema='GOLD') }}

SELECT
    product_id,
    warehouse_id,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN transaction_type = 'INBOUND' THEN quantity ELSE 0 END) AS inbound_quantity,
    SUM(CASE WHEN transaction_type = 'OUTBOUND' THEN quantity ELSE 0 END) AS outbound_quantity,
    SUM(CASE WHEN transaction_type = 'INBOUND' THEN quantity ELSE -quantity END) AS net_stock_movement,
    SUM(transaction_amount) AS total_transaction_value,
    COUNT_IF(expiry_date BETWEEN CURRENT_DATE() AND DATEADD(day, 30, CURRENT_DATE())) AS expiring_30d_transactions
FROM {{ ref('stg_inventory_transactions') }}
GROUP BY product_id, warehouse_id

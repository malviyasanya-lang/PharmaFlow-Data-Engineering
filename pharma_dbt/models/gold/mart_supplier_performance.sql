{{ config(materialized='table', schema='GOLD') }}

SELECT
    supplier_id,
    COUNT(DISTINCT product_id) AS products_supplied,
    COUNT(*) AS inbound_transactions,
    SUM(quantity) AS total_units_received,
    SUM(transaction_amount) AS total_purchase_value,
    ROUND(AVG(unit_price), 2) AS average_unit_price
FROM {{ ref('fct_inventory_transactions') }}
WHERE transaction_type = 'INBOUND'
GROUP BY supplier_id

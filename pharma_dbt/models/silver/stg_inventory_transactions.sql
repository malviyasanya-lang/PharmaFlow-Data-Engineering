{{ config(materialized='table', schema='SILVER') }}

SELECT
    transaction_id,
    product_id,
    warehouse_id,
    supplier_id,
    quantity,
    unit_price,
    quantity * unit_price AS transaction_amount,
    transaction_type,
    transaction_date,
    expiry_date,
    loaded_at
FROM {{ source('bronze', 'RAW_INVENTORY_TRANSACTIONS') }}
WHERE quantity > 0
  AND unit_price >= 0

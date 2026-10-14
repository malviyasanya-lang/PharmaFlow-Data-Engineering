{{ config(materialized='view', schema='SILVER') }}
select order_id, product_id, warehouse_id, quantity,
unit_price, quantity * unit_price as order_amount,
order_date, upper(trim(order_status)) as order_status
from {{ source('bronze', 'raw_sales_orders') }}
where order_id is not null and quantity > 0 and unit_price >= 0

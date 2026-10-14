{{ config(materialized='table', schema='GOLD') }}
select s.order_id, s.product_id, p.product_name,
p.category, s.warehouse_id, w.city as warehouse_city,
s.quantity, s.unit_price, s.order_amount,
s.order_date, s.order_status
from {{ ref('stg_sales_orders') }} s
left join {{ ref('dim_products') }} p
on s.product_id = p.product_id
left join {{ ref('dim_warehouses') }} w
on s.warehouse_id = w.warehouse_id

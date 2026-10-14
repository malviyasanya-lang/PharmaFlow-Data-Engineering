{{ config(materialized='table', schema='GOLD') }}
select date_trunc('month', order_date)::date as sales_month,
warehouse_city, category, count(*) as total_orders,
sum(quantity) as units_sold,
sum(order_amount) as total_sales_amount
from {{ ref('fct_sales') }}
where order_status = 'COMPLETED'
group by 1, 2, 3

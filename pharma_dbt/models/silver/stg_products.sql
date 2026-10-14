{{ config(materialized='view', schema='SILVER') }}
select product_id, trim(product_name) as product_name,
trim(category) as category, unit_price, reorder_level
from {{ source('bronze', 'raw_products') }}
where product_id is not null

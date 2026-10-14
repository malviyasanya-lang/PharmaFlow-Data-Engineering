{{ config(materialized='table', schema='GOLD') }}
select product_id, product_name, category,
unit_price, reorder_level
from {{ ref('stg_products') }}

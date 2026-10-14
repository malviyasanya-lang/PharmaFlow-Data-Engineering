{{ config(materialized='table', schema='GOLD') }}
select warehouse_id, warehouse_name, city, capacity
from {{ ref('stg_warehouses') }}

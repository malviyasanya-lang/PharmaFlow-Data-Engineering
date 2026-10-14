{{ config(materialized='view', schema='SILVER') }}
select warehouse_id, trim(warehouse_name) as warehouse_name,
trim(city) as city, capacity
from {{ source('bronze', 'raw_warehouses') }}
where warehouse_id is not null

{{ config(materialized='view', schema='SILVER') }}
select supplier_id, trim(supplier_name) as supplier_name,
trim(supplier_city) as supplier_city, supplier_rating
from {{ source('bronze', 'raw_suppliers') }}
where supplier_id is not null

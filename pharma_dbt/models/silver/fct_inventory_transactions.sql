{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='transaction_id',
        schema='SILVER',
        on_schema_change='sync_all_columns'
    )
}}

SELECT
    transaction_id,
    product_id,
    warehouse_id,
    supplier_id,
    quantity,
    unit_price,
    transaction_amount,
    transaction_type,
    transaction_date,
    expiry_date,
    loaded_at
FROM {{ ref('stg_inventory_transactions') }}

{% if is_incremental() %}
WHERE loaded_at >= (
    SELECT COALESCE(MAX(loaded_at), '1900-01-01'::TIMESTAMP_LTZ)
    FROM {{ this }}
)
{% endif %}

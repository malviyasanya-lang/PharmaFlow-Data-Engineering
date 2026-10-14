# PharmaFlow — Pharmaceutical Supply Chain Analytics

## Overview
A portfolio data engineering project for pharmaceutical inventory and supplier analytics.

## Technology Stack
- Snowflake: Cloud data warehouse
- dbt Core: SQL transformations, testing, documentation
- SQL: Data modeling and analytics
- Python and PostgreSQL: Local inventory data preparation

## Architecture

Synthetic transaction generation
        |
        v
Snowflake BRONZE
RAW_INVENTORY_TRANSACTIONS (100K rows)
        |
        v
dbt SILVER
stg_inventory_transactions
        |
        +--------------------------+
        |                          |
        v                          v
dbt GOLD                  dbt SILVER
mart_inventory_health     fct_inventory_transactions
                                   |
                                   v
                              dbt GOLD
                         mart_supplier_performance

## Implemented Features
- 100,000 synthetic pharmaceutical inventory transactions
- Bronze, Silver and Gold data modeling
- dbt SQL transformations
- Incremental fact model with MERGE
- Inventory movement analytics
- Supplier purchase analytics
- Data quality tests for uniqueness, nulls and accepted values
- dbt documentation and lineage generation

## Run

cd pharma_dbt
dbt debug
dbt build
dbt docs generate

## Business Use Cases
- Analyze inbound and outbound inventory movements
- Identify products associated with upcoming expiry dates
- Compare supplier purchase volume and value
- Track transaction activity across warehouses

## Current Scope
The 100K transaction dataset is generated directly in Snowflake.
The local PostgreSQL inventory ingestion is separate and is not yet
integrated into the Snowflake transaction pipeline.

## Future Enhancements
- PostgreSQL-to-Snowflake ingestion
- Airflow scheduling
- Late-arriving data handling
- Dashboard integration

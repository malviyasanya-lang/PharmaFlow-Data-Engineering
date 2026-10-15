
import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

CSV_PATH = ROOT / "data" / "products.csv"
STAGE_NAME = "PHARMAFLOW.BRONZE.PHARMA_CSV_STAGE"
TARGET_TABLE = "PHARMAFLOW.BRONZE.RAW_PRODUCTS_INGEST_TEST"

required = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_WAREHOUSE",
]
missing = [key for key in required if not os.getenv(key)]
if missing:
    raise RuntimeError(f"Missing environment variables: {missing}")

if not CSV_PATH.exists():
    raise FileNotFoundError(CSV_PATH)

connection_args = {
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
    "database": "PHARMAFLOW",
    "schema": "BRONZE",
}
if os.getenv("SNOWFLAKE_ROLE"):
    connection_args["role"] = os.environ["SNOWFLAKE_ROLE"]

with snowflake.connector.connect(**connection_args) as conn:
    with conn.cursor() as cur:
        # Separate test table: no changes to existing RAW_PRODUCTS
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TARGET_TABLE}
            LIKE PHARMAFLOW.BRONZE.RAW_PRODUCTS
        """)

        cur.execute(f"""
            CREATE STAGE IF NOT EXISTS {STAGE_NAME}
            FILE_FORMAT = (
                TYPE = CSV
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            )
        """)

        # Upload local CSV to Snowflake internal stage
        cur.execute(
            f"PUT 'file://{CSV_PATH.as_posix()}' "
            f"@{STAGE_NAME} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        )

        # Load into the test table using COPY INTO
        cur.execute(f"""
            COPY INTO {TARGET_TABLE}
            FROM @{STAGE_NAME}/products.csv.gz
            FILE_FORMAT = (
                TYPE = CSV
                SKIP_HEADER = 1
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            )
            ON_ERROR = 'ABORT_STATEMENT'
        """)

        for row in cur.fetchall():
            print("COPY result:", row)

        cur.execute(f"SELECT COUNT(*) FROM {TARGET_TABLE}")
        print("Test table row count:", cur.fetchone()[0])

print("Ingestion completed.")

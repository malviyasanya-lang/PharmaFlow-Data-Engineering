import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

# Build database connection
db_url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(db_url)

# Locate the input file
project_root = Path(__file__).resolve().parent.parent
csv_path = project_root / "data" / "inventory.csv"

# Extract
df = pd.read_csv(csv_path, dtype={"batch_id": str, "warehouse_id": str})

# Basic validation
if df.empty:
    raise ValueError("Inventory CSV is empty")

# Load into PostgreSQL
with engine.begin() as connection:
    df.to_sql(
        "raw_inventory",
        connection,
        schema="public",
        if_exists="replace",
        index=False,
    )

print(f"Successfully loaded {len(df)} records into public.raw_inventory")
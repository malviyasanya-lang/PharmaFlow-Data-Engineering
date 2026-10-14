import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            database, version = cur.fetchone()

            print("Database connection successful!")
            print(f"Connected database: {database}")
            print(f"PostgreSQL version: {version.split(',')[0]}")

except psycopg.Error as error:
    print(f"Database connection failed: {error}")
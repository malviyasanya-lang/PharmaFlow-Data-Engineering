
from pathlib import Path
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 1. Products: 500 records
categories = [
    "Antibiotics", "Analgesics", "Antidiabetics",
    "Cardiovascular", "Vitamins", "Respiratory"
]

products = []
for product_id in range(101, 601):
    products.append({
        "product_id": product_id,
        "product_name": f"{random.choice(['Medi', 'Pharma', 'Cure', 'Health'])}-{product_id}",
        "category": random.choice(categories),
        "unit_price": round(random.uniform(20, 1500), 2),
        "reorder_level": random.randint(100, 1000)
    })

pd.DataFrame(products).to_csv(DATA_DIR / "products.csv", index=False)

# 2. Suppliers: 20 records
suppliers = []
for i in range(1, 21):
    suppliers.append({
        "supplier_id": f"S{i:03d}",
        "supplier_name": fake.company(),
        "supplier_city": fake.city(),
        "supplier_rating": round(random.uniform(2.5, 5.0), 2)
    })

pd.DataFrame(suppliers).to_csv(DATA_DIR / "suppliers.csv", index=False)

# 3. Warehouses: 5 records
cities = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai"]
warehouses = []

for i, city in enumerate(cities, start=1):
    warehouses.append({
        "warehouse_id": f"W{i:02d}",
        "warehouse_name": f"{city} Distribution Center",
        "city": city,
        "capacity": random.randint(100000, 500000)
    })

pd.DataFrame(warehouses).to_csv(DATA_DIR / "warehouses.csv", index=False)

# 4. Sales Orders: 50,000 records
# Existing inventory transactions reference product IDs 101-108.
# Use that range so the new sales data can be joined to existing inventory.
sales = []
start_date = datetime(2025, 1, 1)
max_days = (datetime(2026, 10, 14) - start_date).days

for order_id in range(1, 50001):
    product_id = random.randint(101, 108)
    quantity = random.randint(1, 100)
    unit_price = next(
        p["unit_price"] for p in products
        if p["product_id"] == product_id
    )

    sales.append({
        "order_id": order_id,
        "product_id": product_id,
        "warehouse_id": f"W{random.randint(1, 5):02d}",
        "quantity": quantity,
        "unit_price": unit_price,
        "order_date": (
            start_date + timedelta(days=random.randint(0, max_days))
        ).strftime("%Y-%m-%d"),
        "order_status": random.choice(
            ["COMPLETED", "COMPLETED", "COMPLETED", "CANCELLED", "PENDING"]
        )
    })

pd.DataFrame(sales).to_csv(DATA_DIR / "sales_orders.csv", index=False)

print("Generated 4 datasets successfully!")
print("Products: 500")
print("Suppliers: 20")
print("Warehouses: 5")
print("Sales Orders: 50000")

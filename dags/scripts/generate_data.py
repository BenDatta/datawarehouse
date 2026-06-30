import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

NUM_CUSTOMERS = 2000
NUM_PRODUCTS = 200
NUM_SALES = 100_000

DATE_START = date(2025, 1, 1)
DATE_END = date(2025, 12, 31)

PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
    "Toys",
]

# Directory where Airflow expects the CSV files
DATA_DIR = Path("/opt/airflow/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ── 1. Dim Customer ──────────────────────────────────────────────────────
def generate_dim_customer(n):
    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                "customer_id": i,
                "customer_name": fake.name(),
                "email": fake.email(),
                "city": fake.city(),
                "country": fake.country(),
                "signup_date": fake.date_between(
                    start_date=DATE_START,
                    end_date=DATE_END,
                ),
            }
        )
    return pd.DataFrame(rows)


# ── 2. Dim Product ────────────────────────────────────────────────────────
def generate_dim_product(n):
    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                "product_id": i,
                "product_name": fake.word().capitalize()
                + " "
                + fake.word().capitalize(),
                "category": random.choice(PRODUCT_CATEGORIES),
                "unit_price": round(random.uniform(5, 500), 2),
            }
        )
    return pd.DataFrame(rows)


# ── 3. Dim Date ───────────────────────────────────────────────────────────
def generate_dim_date(start, end):
    rows = []
    current = start

    while current <= end:
        rows.append(
            {
                "date_id": int(current.strftime("%Y%m%d")),
                "full_date": current,
                "day": current.day,
                "month": current.month,
                "month_name": current.strftime("%B"),
                "quarter": (current.month - 1) // 3 + 1,
                "year": current.year,
                "day_of_week": current.strftime("%A"),
                "is_weekend": current.weekday() >= 5,
            }
        )
        current += timedelta(days=1)

    return pd.DataFrame(rows)


# ── 4. Fact Sales ─────────────────────────────────────────────────────────
def generate_fact_sales(n, dim_customer, dim_product, dim_date):
    customer_ids = dim_customer["customer_id"].tolist()
    product_ids = dim_product["product_id"].tolist()
    date_ids = dim_date["date_id"].tolist()

    price_lookup = dict(
        zip(
            dim_product["product_id"],
            dim_product["unit_price"],
        )
    )

    rows = []

    for i in range(1, n + 1):
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 10)
        unit_price = price_lookup[product_id]

        rows.append(
            {
                "sale_id": i,
                "customer_id": random.choice(customer_ids),
                "product_id": product_id,
                "date_id": random.choice(date_ids),
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": round(quantity * unit_price, 2),
            }
        )

    return pd.DataFrame(rows)


# ── Generate all CSVs ─────────────────────────────────────────────────────
def main():

    print("Generating dimension tables...")

    dim_customer = generate_dim_customer(NUM_CUSTOMERS)
    dim_product = generate_dim_product(NUM_PRODUCTS)
    dim_date = generate_dim_date(DATE_START, DATE_END)

    print("Generating fact table...")

    fact_sales = generate_fact_sales(
        NUM_SALES,
        dim_customer,
        dim_product,
        dim_date,
    )

    print("Saving CSV files...")

    dim_customer.to_csv(DATA_DIR / "dim_customer.csv", index=False)
    dim_product.to_csv(DATA_DIR / "dim_product.csv", index=False)
    dim_date.to_csv(DATA_DIR / "dim_date.csv", index=False)
    fact_sales.to_csv(DATA_DIR / "fact_sales.csv", index=False)

    print("\n✅ CSV files created successfully!\n")


if __name__ == "__main__":
    main()

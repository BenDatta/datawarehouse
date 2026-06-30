import random
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

NUM_CUSTOMERS = 2000
NUM_PRODUCTS = 200
NUM_SALES = 150_000

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

DATA_DIR = Path("/opt/airflow/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────
# DIM CUSTOMER
# ─────────────────────────────
def dim_customer(n):
    return pd.DataFrame(
        [
            {
                "customer_id": i,
                "customer_name": fake.name(),
                "email": f"user{i}@example.com",
                "city": fake.city(),
                "country": fake.country(),
                "signup_date": fake.date_between(START_DATE, END_DATE),
            }
            for i in range(1, n + 1)
        ]
    )


# ─────────────────────────────
# DIM PRODUCT
# ─────────────────────────────
def dim_product(n):
    categories = ["Electronics", "Clothing", "Home", "Sports", "Books", "Toys"]

    return pd.DataFrame(
        [
            {
                "product_id": i,
                "product_name": fake.word().capitalize(),
                "category": random.choice(categories),
                "unit_price": round(random.uniform(5, 500), 2),
            }
            for i in range(1, n + 1)
        ]
    )


# ─────────────────────────────
# DIM DATE
# ─────────────────────────────
def dim_date(start, end):
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


# ─────────────────────────────
# FACT SALES
# ─────────────────────────────
def fact_sales(n, customers, products, dates):
    customer_ids = customers["customer_id"].tolist()
    product_ids = products["product_id"].tolist()
    date_ids = dates["date_id"].tolist()

    price_map = dict(zip(products["product_id"], products["unit_price"]))

    rows = []

    for i in range(1, n + 1):
        product_id = random.choice(product_ids)
        quantity = random.randint(1, 10)
        unit_price = price_map[product_id]

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


# ─────────────────────────────
# RUN
# ─────────────────────────────
def main():
    print("Generating data...")

    customers = dim_customer(NUM_CUSTOMERS)
    products = dim_product(NUM_PRODUCTS)
    dates = dim_date(START_DATE, END_DATE)

    sales = fact_sales(NUM_SALES, customers, products, dates)

    print("Saving CSVs...")

    customers.to_csv(DATA_DIR / "dim_customer.csv", index=False)
    products.to_csv(DATA_DIR / "dim_product.csv", index=False)
    dates.to_csv(DATA_DIR / "dim_date.csv", index=False)
    sales.to_csv(DATA_DIR / "fact_sales.csv", index=False)

    print("✅ Done")


if __name__ == "__main__":
    main()

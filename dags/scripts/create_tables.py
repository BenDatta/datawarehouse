import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.environ["POSTGRES_CONN_HOST"],
        port=os.environ["POSTGRES_CONN_PORT"],
        dbname=os.environ["DATABASE_NAME"],
        user=os.environ["DATABASE_USERNAME"],
        password=os.environ["DATABASE_PASSWORD"],
    )


def run_query(query, message):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
        print(message)
    finally:
        conn.close()


# ─────────────────────────────
# DIM CUSTOMER
# ─────────────────────────────
def create_dim_customer():
    query = """
    CREATE TABLE IF NOT EXISTS dim_customer (
        customer_id   INT PRIMARY KEY,
        customer_name TEXT,
        email         TEXT UNIQUE,
        city          TEXT,
        country       TEXT,
        signup_date   DATE,
        updated_at    TIMESTAMP DEFAULT NOW()
    );
    """
    run_query(query, "dim_customer ready")


# ─────────────────────────────
# DIM PRODUCT
# ─────────────────────────────
def create_dim_product():
    query = """
    CREATE TABLE IF NOT EXISTS dim_product (
        product_id   INT PRIMARY KEY,
        product_name TEXT,
        category     TEXT,
        unit_price   NUMERIC,
        updated_at   TIMESTAMP DEFAULT NOW()
    );
    """
    run_query(query, "dim_product ready")


# ─────────────────────────────
# DIM DATE
# ─────────────────────────────
def create_dim_date():
    query = """
    CREATE TABLE IF NOT EXISTS dim_date (
        date_id     INT PRIMARY KEY,
        full_date   DATE,
        day         INT,
        month       INT,
        month_name  TEXT,
        quarter     INT,
        year        INT,
        day_of_week TEXT,
        is_weekend  BOOLEAN
    );
    """
    run_query(query, "dim_date ready")


# ─────────────────────────────
# FACT SALES
# ─────────────────────────────
def create_fact_sales():
    query = """
    CREATE TABLE IF NOT EXISTS fact_sales (
        sale_id      INT,
        customer_id  INT REFERENCES dim_customer(customer_id),
        product_id   INT REFERENCES dim_product(product_id),
        date_id      INT REFERENCES dim_date(date_id),
        quantity     INT,
        unit_price   NUMERIC,
        total_amount NUMERIC,

        PRIMARY KEY (sale_id, customer_id, product_id, date_id)
    );
    """
    run_query(query, "fact_sales ready")


# ─────────────────────────────
# RUN ALL
# ─────────────────────────────
if __name__ == "__main__":
    create_dim_customer()
    create_dim_product()
    create_dim_date()
    create_fact_sales()

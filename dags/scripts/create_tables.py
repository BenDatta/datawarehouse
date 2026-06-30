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


def run_query(query, success_message):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
        print(success_message)
    finally:
        conn.close()


def create_dim_customer():
    query = """
    CREATE TABLE IF NOT EXISTS dim_customer (
        customer_id   INT PRIMARY KEY,
        customer_name TEXT,
        email         TEXT,
        city          TEXT,
        country       TEXT,
        signup_date   DATE
    );
    """
    run_query(query, "dim_customer Table created")


def create_dim_product():
    query = """
    CREATE TABLE IF NOT EXISTS dim_product (
        product_id   INT PRIMARY KEY,
        product_name TEXT,
        category     TEXT,
        unit_price   NUMERIC
    );
    """
    run_query(query, "dim_product Table created")


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
    run_query(query, "dim_date Table created")


def create_fact_sales():
    query = """
    CREATE TABLE IF NOT EXISTS fact_sales (
        sale_id      INT PRIMARY KEY,
        customer_id  INT REFERENCES dim_customer(customer_id),
        product_id   INT REFERENCES dim_product(product_id),
        date_id      INT REFERENCES dim_date(date_id),
        quantity     INT,
        unit_price   NUMERIC,
        total_amount NUMERIC
    );
    """
    run_query(query, "fact_sales Table created")


if __name__ == "__main__":
    create_dim_customer()
    create_dim_product()
    create_dim_date()
    create_fact_sales()  # must be last — depends on the three dim tables above

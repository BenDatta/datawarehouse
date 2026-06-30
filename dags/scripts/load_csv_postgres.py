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


def load_csv_to_table(csv_path, table_name):
    """
    Uses Postgres' COPY command — by far the fastest way to bulk load
    a CSV (much faster than row-by-row INSERTs, especially for fact_sales
    with 100k rows).
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur, open(csv_path, "r") as f:
            next(f)  # skip header row, since the table columns are already defined
            cur.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV", f)
        conn.commit()
        print(f"Loaded {csv_path} → {table_name}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Order matters: dimensions first, fact table last
    # (fact_sales has foreign keys pointing to the dim tables)
    load_csv_to_table("dim_customer.csv", "dim_customer")
    load_csv_to_table("dim_product.csv", "dim_product")
    load_csv_to_table("dim_date.csv", "dim_date")
    load_csv_to_table("fact_sales.csv", "fact_sales")

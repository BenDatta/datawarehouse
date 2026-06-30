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


# Columns that exist in each CSV file
COPY_COLUMNS = {
    "dim_customer": ("customer_id, customer_name, email, city, country, signup_date"),
    "dim_product": ("product_id, product_name, category, unit_price"),
    "dim_date": (
        "date_id, full_date, day, month, month_name, quarter, "
        "year, day_of_week, is_weekend"
    ),
    "fact_sales": (
        "sale_id, customer_id, product_id, date_id, quantity, unit_price, total_amount"
    ),
}


def load_csv_to_table(csv_path, table_name, truncate_first=False):
    """
    Load a CSV file into a PostgreSQL table.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.
    table_name : str
        Target PostgreSQL table.
    truncate_first : bool
        If True, truncate the table before loading.
    """

    conn = get_connection()

    try:
        with conn.cursor() as cur:
            if truncate_first:
                cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")

            columns = COPY_COLUMNS[table_name]

            with open(csv_path, "r") as f:
                next(f)  # Skip header row

                cur.copy_expert(
                    f"""
                    COPY {table_name} ({columns})
                    FROM STDIN
                    WITH CSV
                    """,
                    f,
                )

        conn.commit()
        print(f"✅ Loaded {csv_path} → {table_name}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Failed to load {table_name}: {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    load_csv_to_table(
        "dim_customer.csv",
        "dim_customer",
        truncate_first=True,
    )

    load_csv_to_table(
        "dim_product.csv",
        "dim_product",
        truncate_first=True,
    )

    load_csv_to_table(
        "dim_date.csv",
        "dim_date",
        truncate_first=True,
    )

    load_csv_to_table(
        "fact_sales.csv",
        "fact_sales",
        truncate_first=True,
    )

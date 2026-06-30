from datetime import datetime

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from scripts.generate_data import main as generate_data
from scripts.create_tables import (
    create_dim_customer,
    create_dim_product,
    create_dim_date,
    create_fact_sales,
)
from scripts.load_csv_postgres import load_csv_to_table

with DAG(
    dag_id="sales_star_schema_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["etl", "postgres", "star-schema"],
) as dag:
    # ==============================================================
    # Generate CSV Files
    # ==============================================================

    generate_data_task = PythonOperator(
        task_id="generate_data",
        python_callable=generate_data,
    )

    # ==============================================================
    # Create Tables
    # ==============================================================

    create_dim_customer_task = PythonOperator(
        task_id="create_dim_customer",
        python_callable=create_dim_customer,
    )

    create_dim_product_task = PythonOperator(
        task_id="create_dim_product",
        python_callable=create_dim_product,
    )

    create_dim_date_task = PythonOperator(
        task_id="create_dim_date",
        python_callable=create_dim_date,
    )

    create_fact_sales_task = PythonOperator(
        task_id="create_fact_sales",
        python_callable=create_fact_sales,
    )

    # ==============================================================
    # Load Dimension Tables
    # ==============================================================

    load_dim_customer_task = PythonOperator(
        task_id="load_dim_customer",
        python_callable=load_csv_to_table,
        op_kwargs={
            "csv_path": "/opt/airflow/data/dim_customer.csv",
            "table_name": "dim_customer",
        },
    )

    load_dim_product_task = PythonOperator(
        task_id="load_dim_product",
        python_callable=load_csv_to_table,
        op_kwargs={
            "csv_path": "/opt/airflow/data/dim_product.csv",
            "table_name": "dim_product",
        },
    )

    load_dim_date_task = PythonOperator(
        task_id="load_dim_date",
        python_callable=load_csv_to_table,
        op_kwargs={
            "csv_path": "/opt/airflow/data/dim_date.csv",
            "table_name": "dim_date",
        },
    )

    # ==============================================================
    # Load Fact Table
    # ==============================================================

    load_fact_sales_task = PythonOperator(
        task_id="load_fact_sales",
        python_callable=load_csv_to_table,
        op_kwargs={
            "csv_path": "/opt/airflow/data/fact_sales.csv",
            "table_name": "fact_sales",
        },
    )

    # ==============================================================
    # Dependencies
    # ==============================================================

    # Step 1 - Generate CSV files
    generate_data_task >> [
        create_dim_customer_task,
        create_dim_product_task,
        create_dim_date_task,
        create_fact_sales_task,
    ]

    # Step 2 - Load dimension tables
    create_dim_customer_task >> load_dim_customer_task
    create_dim_product_task >> load_dim_product_task
    create_dim_date_task >> load_dim_date_task

    # Step 3 - Load fact table
    [
        create_fact_sales_task,
        load_dim_customer_task,
        load_dim_product_task,
        load_dim_date_task,
    ] >> load_fact_sales_task

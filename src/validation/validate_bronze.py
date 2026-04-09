import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def main() -> None:
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print("Validating bronze.telco_customers_raw...")

    # Check total row count
    row_count_query = "SELECT COUNT(*) AS row_count FROM bronze.telco_customers_raw;"
    row_count = pd.read_sql(row_count_query, engine).iloc[0]["row_count"]

    print(f"Row count: {row_count}")

    if row_count == 0:
        raise ValueError("Validation failed: bronze.telco_customers_raw is empty.")

    # Check for null customer IDs
    null_id_query = """
        SELECT COUNT(*) AS null_customer_ids
        FROM bronze.telco_customers_raw
        WHERE customer_id IS NULL;
    """
    null_customer_ids = pd.read_sql(null_id_query, engine).iloc[0]["null_customer_ids"]

    print(f"Null customer_id count: {null_customer_ids}")

    if null_customer_ids > 0:
        raise ValueError("Validation failed: bronze.telco_customers_raw contains null customer_id values.")

    print("Bronze validation passed successfully.")


if __name__ == "__main__":
    main()
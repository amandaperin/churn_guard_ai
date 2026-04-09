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

    print("Validating features.customer_churn_features...")

    # Check total row count
    row_count_query = "SELECT COUNT(*) AS row_count FROM features.customer_churn_features;"
    row_count = pd.read_sql(row_count_query, engine).iloc[0]["row_count"]

    print(f"Row count: {row_count}")

    if row_count == 0:
        raise ValueError("Validation failed: features.customer_churn_features is empty.")

    # Check for nulls in key model columns
    nulls_query = """
        SELECT
            SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS null_customer_id,
            SUM(CASE WHEN tenure IS NULL THEN 1 ELSE 0 END) AS null_tenure,
            SUM(CASE WHEN monthly_charges IS NULL THEN 1 ELSE 0 END) AS null_monthly_charges,
            SUM(CASE WHEN total_charges IS NULL THEN 1 ELSE 0 END) AS null_total_charges,
            SUM(CASE WHEN churn IS NULL THEN 1 ELSE 0 END) AS null_churn
        FROM features.customer_churn_features;
    """
    nulls_df = pd.read_sql(nulls_query, engine)

    print("Null check results:")
    print(nulls_df.to_string(index=False))

    null_values = nulls_df.iloc[0].to_dict()
    if any(value > 0 for value in null_values.values()):
        raise ValueError("Validation failed: features.customer_churn_features contains nulls in key columns.")

    print("Feature validation passed successfully.")


if __name__ == "__main__":
    main()
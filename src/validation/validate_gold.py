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

    print("Validating gold.customer_risk_segments...")

    # Check total row count
    row_count_query = "SELECT COUNT(*) AS row_count FROM gold.customer_risk_segments;"
    row_count = pd.read_sql(row_count_query, engine).iloc[0]["row_count"]

    print(f"Row count: {row_count}")

    if row_count == 0:
        raise ValueError("Validation failed: gold.customer_risk_segments is empty.")

    # Check allowed risk categories
    category_query = """
        SELECT risk_category, COUNT(*) AS count
        FROM gold.customer_risk_segments
        GROUP BY risk_category
        ORDER BY risk_category;
    """
    category_df = pd.read_sql(category_query, engine)

    print("Risk category distribution:")
    print(category_df.to_string(index=False))

    valid_categories = {"High", "Medium", "Low"}
    found_categories = set(category_df["risk_category"].tolist())

    if not found_categories.issubset(valid_categories):
        raise ValueError(
            f"Validation failed: unexpected risk categories found: {found_categories - valid_categories}"
        )

    print("Gold validation passed successfully.")


if __name__ == "__main__":
    main()
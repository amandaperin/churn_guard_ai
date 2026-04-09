from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# Load environment variables from the .env file
load_dotenv()

# Read database connection settings from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Read the raw CSV path from environment variables
CSV_PATH = Path(os.getenv("CSV_PATH", ""))

# Define the target schema and table in PostgreSQL
SCHEMA_NAME = "bronze"
TABLE_NAME = "telco_customers_raw"


def main() -> None:
    try:
        # Validate required environment variables before running
        required_env_vars = {
            "DB_USER": DB_USER,
            "DB_PASSWORD": DB_PASSWORD,
            "DB_HOST": DB_HOST,
            "DB_PORT": DB_PORT,
            "DB_NAME": DB_NAME,
        }

        missing_vars = [key for key, value in required_env_vars.items() if not value]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Check whether the CSV file exists before trying to read it
        if not CSV_PATH.exists():
            raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

        print("Reading CSV file...")
        df = pd.read_csv(CSV_PATH)

        # Standardize column names 
        df.columns = [
            "customer_id",
            "gender",
            "senior_citizen",
            "partner",
            "dependents",
            "tenure",
            "phone_service",
            "multiple_lines",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies",
            "contract",
            "paperless_billing",
            "payment_method",
            "monthly_charges",
            "total_charges",
            "churn",
        ]

        print("Connecting to PostgreSQL...")
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        # Clear the bronze table before reloading the full dataset
        print(f"Truncating table {SCHEMA_NAME}.{TABLE_NAME}...")
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {SCHEMA_NAME}.{TABLE_NAME};"))

        # Load the DataFrame into the bronze table
        print("Loading data into PostgreSQL...")
        df.to_sql(
            name=TABLE_NAME,
            con=engine,
            schema=SCHEMA_NAME,
            if_exists="append",
            index=False,
        )

        print(f"Success: {len(df)} rows loaded into {SCHEMA_NAME}.{TABLE_NAME}")

    except FileNotFoundError as e:
        print(f"File error: {e}")

    except ValueError as e:
        print(f"Configuration error: {e}")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
import json
import os
import pickle
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

MODEL_PATH = Path("models/churn_model.pkl")
METADATA_PATH = Path("models/model_metadata.json")


def main() -> None:
    try:
        # Validate environment variables
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

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

        if not METADATA_PATH.exists():
            raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

        print("Loading saved model and metadata...")

        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)

        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        threshold = metadata["threshold"]
        feature_columns = metadata["feature_columns"]

        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        print("Loading feature table from database...")

        df = pd.read_sql("SELECT * FROM features.customer_churn_features", engine)

        X = df[feature_columns]

        print("Generating predictions using saved model...")

        proba = model.predict_proba(X)[:, 1]

        df_predictions = pd.DataFrame(
            {
                "customer_id": df["customer_id"],
                "churn_probability": proba,
                "churn_prediction": (proba >= threshold).astype(int),
            }
        )

        print("Clearing old predictions from gold.churn_predictions...")

        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE gold.churn_predictions;"))

        print("Saving predictions to PostgreSQL...")

        df_predictions.to_sql(
            name="churn_predictions",
            con=engine,
            schema="gold",
            if_exists="append",
            index=False,
        )

        print(
            f"Success: {len(df_predictions)} predictions saved to gold.churn_predictions "
            f"using saved model and threshold {threshold}"
        )

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
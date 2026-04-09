import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from xgboost import XGBClassifier


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Define the classification threshold used to convert probabilities into classes
THRESHOLD = 0.3


def main() -> None:
    try:
        # Validate required environment variables
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

        # Create PostgreSQL connection
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        print("Loading feature table from database...")

        # Load the model-ready feature table
        df = pd.read_sql(
            "SELECT * FROM features.customer_churn_features",
            engine,
        )

        print(f"Loaded dataset shape: {df.shape}")

        # Separate features and target
        X = df.drop(columns=["customer_id", "churn"])
        y = df["churn"]

        print("Training XGBoost model on full feature table...")

        # Train the final model using the full dataset
        model = XGBClassifier(
            random_state=42,
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
        )
        model.fit(X, y)

        print("Generating predictions...")

        # Generate churn probabilities
        proba = model.predict_proba(X)[:, 1]

        # Apply the custom threshold to generate class predictions
        df_predictions = pd.DataFrame(
            {
                "customer_id": df["customer_id"],
                "churn_probability": proba,
                "churn_prediction": (proba >= THRESHOLD).astype(int),
            }
        )

        print("Clearing old predictions from gold.churn_predictions...")

        # Remove previous predictions before inserting the new ones
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE gold.churn_predictions;"))

        print("Saving predictions to PostgreSQL...")

        # Save the predictions into the gold layer
        df_predictions.to_sql(
            name="churn_predictions",
            con=engine,
            schema="gold",
            if_exists="append",
            index=False,
        )

        print(
            f"Success: {len(df_predictions)} predictions saved to "
            f"gold.churn_predictions using threshold {THRESHOLD}"
        )

    except ValueError as e:
        print(f"Configuration error: {e}")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
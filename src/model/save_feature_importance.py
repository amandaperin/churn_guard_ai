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

        # Create database connection
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        print("Loading feature table from database...")

        # Load model-ready data
        df = pd.read_sql("SELECT * FROM features.customer_churn_features", engine)

        # Separate features and target
        X = df.drop(columns=["customer_id", "churn"])
        y = df["churn"]

        print("Training XGBoost model...")

        # Train the final XGBoost model
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

        print("Extracting feature importances...")

        # Build the feature importance DataFrame
        importance_df = pd.DataFrame(
            {
                "feature": X.columns,
                "importance": model.feature_importances_,
            }
        ).sort_values(by="importance", ascending=False)

        print("Clearing old feature importance values...")

        # Clear previous records
        with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE gold.model_feature_importance;"))

        print("Saving feature importances to PostgreSQL...")

        # Save the results
        importance_df.to_sql(
            name="model_feature_importance",
            con=engine,
            schema="gold",
            if_exists="append",
            index=False,
        )

        print(
            f"Success: {len(importance_df)} feature importance rows saved "
            "to gold.model_feature_importance"
        )

    except ValueError as e:
        print(f"Configuration error: {e}")

    except SQLAlchemyError as e:
        print(f"Database error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
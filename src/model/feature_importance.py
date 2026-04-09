import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from xgboost import XGBClassifier


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def main() -> None:
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

    # Extract feature importance
    importance_df = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": model.feature_importances_,
        }
    ).sort_values(by="importance", ascending=False)

    print("\nTop feature importances:")
    print(importance_df.to_string(index=False))


if __name__ == "__main__":
    main()
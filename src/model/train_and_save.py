import json
import os
import pickle
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "churn_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
THRESHOLD = 0.3


def main() -> None:
    # Create database connection
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print("Loading feature table from database...")

    df = pd.read_sql("SELECT * FROM features.customer_churn_features", engine)

    X = df.drop(columns=["customer_id", "churn"])
    y = df["churn"]

    feature_columns = X.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Training final tuned XGBoost model...")

    model = XGBClassifier(
        random_state=42,
        eval_metric="logloss",
        subsample=0.9,
        n_estimators=100,
        min_child_weight=1,
        max_depth=3,
        learning_rate=0.05,
        gamma=0.3,
        colsample_bytree=0.8,
    )
    model.fit(X_train, y_train)

    print("Evaluating final model...")

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_proba)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "threshold": THRESHOLD,
        "feature_columns": feature_columns,
        "model_name": "XGBoost",
        "best_params": {
            "subsample": 0.9,
            "n_estimators": 100,
            "min_child_weight": 1,
            "max_depth": 3,
            "learning_rate": 0.05,
            "gamma": 0.3,
            "colsample_bytree": 0.8,
        },
    }

    print("Saving model...")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print("Saving metadata...")
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print("Final metrics:")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
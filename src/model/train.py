import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def evaluate_thresholds(model_name: str, y_test, y_proba) -> None:
    """
    Print only the most relevant threshold-based metrics for churn prediction.
    """
    print(f"\n{model_name}")
    print("-" * len(model_name))

    roc_auc = roc_auc_score(y_test, y_proba)
    print(f"ROC AUC: {roc_auc:.4f}")

    for threshold in [0.5, 0.4, 0.3]:
        y_pred = (y_proba >= threshold).astype(int)

        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(
            f"Threshold {threshold:.1f} | "
            f"Precision: {precision:.4f} | "
            f"Recall: {recall:.4f} | "
            f"F1: {f1:.4f}"
        )


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

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Logistic Regression pipeline with scaling
    logistic_model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(random_state=42, max_iter=1000)),
        ]
    )

    # Final XGBoost candidate
    xgboost_model = XGBClassifier(
        random_state=42,
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
    )

    # Train Logistic Regression
    logistic_model.fit(X_train, y_train)
    logistic_proba = logistic_model.predict_proba(X_test)[:, 1]

    # Train XGBoost
    xgboost_model.fit(X_train, y_train)
    xgboost_proba = xgboost_model.predict_proba(X_test)[:, 1]

    print("\nFinal model comparison")
    print("======================")
    evaluate_thresholds("Logistic Regression", y_test, logistic_proba)
    evaluate_thresholds("XGBoost", y_test, xgboost_proba)

    print("\nRecommended final choice:")
    print("XGBoost with threshold = 0.3")


if __name__ == "__main__":
    main()
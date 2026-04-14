import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, train_test_split
from xgboost import XGBClassifier


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

BEST_PARAMS_PATH = OUTPUT_DIR / "best_xgboost_params.json"


def evaluate_thresholds(y_true, y_proba) -> list[dict]:
    """
    Evaluate multiple probability thresholds for classification decisions.
    """
    results = []

    for threshold in [0.5, 0.4, 0.3]:
        y_pred = (y_proba >= threshold).astype(int)

        results.append(
            {
                "threshold": threshold,
                "precision": round(precision_score(y_true, y_pred), 4),
                "recall": round(recall_score(y_true, y_pred), 4),
                "f1_score": round(f1_score(y_true, y_pred), 4),
            }
        )

    return results


def main() -> None:
    # Create PostgreSQL connection
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print("Loading feature table from database...")

    df = pd.read_sql("SELECT * FROM features.customer_churn_features", engine)

    print(f"Dataset shape: {df.shape}")

    X = df.drop(columns=["customer_id", "churn"])
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    print("Preparing RandomizedSearchCV...")

    # Base model
    model = XGBClassifier(
        random_state=42,
        eval_metric="logloss",
    )

    # Parameter search space
    param_distributions = {
        "n_estimators": [100, 150, 200, 250, 300],
        "max_depth": [3, 4, 5, 6],
        "learning_rate": [0.01, 0.03, 0.05, 0.1],
        "subsample": [0.7, 0.8, 0.9, 1.0],
        "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
        "min_child_weight": [1, 3, 5, 7],
        "gamma": [0, 0.1, 0.3, 0.5],
    }

    # Stratified cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    search = RandomizedSearchCV(
        estimator=model,
        param_distributions=param_distributions,
        n_iter=20,
        scoring="roc_auc",
        cv=cv,
        verbose=2,
        random_state=42,
        n_jobs=-1,
    )

    print("Running hyperparameter tuning...")
    search.fit(X_train, y_train)

    best_model = search.best_estimator_

    print("\nBest parameters found:")
    print(search.best_params_)

    print(f"\nBest cross-validated ROC AUC: {search.best_score_:.4f}")

    print("\nEvaluating best model on test set...")

    y_proba = best_model.predict_proba(X_test)[:, 1]
    test_roc_auc = roc_auc_score(y_test, y_proba)

    threshold_results = evaluate_thresholds(y_test, y_proba)

    output = {
        "model_name": "XGBoost",
        "best_params": search.best_params_,
        "best_cv_roc_auc": round(search.best_score_, 4),
        "test_roc_auc": round(test_roc_auc, 4),
        "threshold_results": threshold_results,
        "feature_columns": X.columns.tolist(),
    }

    print("\nFinal tuning summary:")
    print(json.dumps(output, indent=2))

    with open(BEST_PARAMS_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved tuning results to: {BEST_PARAMS_PATH}")


if __name__ == "__main__":
    main()
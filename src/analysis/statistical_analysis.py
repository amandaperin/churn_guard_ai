import json
import math
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from scipy.stats import chi2_contingency, mannwhitneyu
from sqlalchemy import create_engine


# Load environment variables from the .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "statistical_analysis_summary.json"


def cramers_v(confusion_matrix: pd.DataFrame) -> float:
    """
    Compute Cramer's V effect size for a contingency table.
    """
    chi2, _, _, _ = chi2_contingency(confusion_matrix)
    n = confusion_matrix.to_numpy().sum()
    r, k = confusion_matrix.shape

    if n == 0 or min(r - 1, k - 1) == 0:
        return 0.0

    return math.sqrt(chi2 / (n * min(r - 1, k - 1)))


def wilson_confidence_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """
    Compute Wilson score confidence interval for a proportion.
    """
    if total == 0:
        return 0.0, 0.0

    p = successes / total
    denominator = 1 + (z**2 / total)
    center = (p + z**2 / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt((p * (1 - p) / total) + (z**2 / (4 * total**2)))
        / denominator
    )

    return center - margin, center + margin


def run_chi_square_tests(df: pd.DataFrame) -> list[dict]:
    """
    Run chi-square tests for categorical variables against churn.
    """
    categorical_columns = [
        "gender",
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
    ]

    results = []

    for column in categorical_columns:
        contingency = pd.crosstab(df[column], df["churn"])

        chi2, p_value, dof, _ = chi2_contingency(contingency)
        effect_size = cramers_v(contingency)

        results.append(
            {
                "variable": column,
                "test": "chi_square",
                "chi2_statistic": round(float(chi2), 4),
                "p_value": round(float(p_value), 6),
                "degrees_of_freedom": int(dof),
                "cramers_v": round(float(effect_size), 4),
                "significant_at_0_05": bool(p_value < 0.05),
            }
        )

    return results


def run_mann_whitney_tests(df: pd.DataFrame) -> list[dict]:
    """
    Run Mann-Whitney U tests for numeric variables comparing churn vs non-churn.
    """
    numeric_columns = [
        "tenure",
        "monthly_charges",
        "total_charges",
    ]

    results = []

    churn_group = df[df["churn"] == 1]
    non_churn_group = df[df["churn"] == 0]

    for column in numeric_columns:
        group_1 = churn_group[column].dropna()
        group_0 = non_churn_group[column].dropna()

        statistic, p_value = mannwhitneyu(
            group_1,
            group_0,
            alternative="two-sided",
        )

        results.append(
            {
                "variable": column,
                "test": "mann_whitney_u",
                "u_statistic": round(float(statistic), 4),
                "p_value": round(float(p_value), 6),
                "median_churn_1": round(float(group_1.median()), 4),
                "median_churn_0": round(float(group_0.median()), 4),
                "mean_churn_1": round(float(group_1.mean()), 4),
                "mean_churn_0": round(float(group_0.mean()), 4),
                "significant_at_0_05": bool(p_value < 0.05),
            }
        )

    return results


def compute_churn_rate_by_contract(df: pd.DataFrame) -> list[dict]:
    """
    Compute churn rate by contract type with 95% Wilson confidence interval.
    """
    grouped = (
        df.groupby("contract")["churn"]
        .agg(total_customers="count", churn_customers="sum")
        .reset_index()
    )

    results = []

    for _, row in grouped.iterrows():
        total = int(row["total_customers"])
        churn_customers = int(row["churn_customers"])
        churn_rate = churn_customers / total if total > 0 else 0.0
        ci_low, ci_high = wilson_confidence_interval(churn_customers, total)

        results.append(
            {
                "contract": row["contract"],
                "total_customers": total,
                "churn_customers": churn_customers,
                "churn_rate": round(float(churn_rate), 4),
                "ci_95_low": round(float(ci_low), 4),
                "ci_95_high": round(float(ci_high), 4),
            }
        )

    return results


def main() -> None:
    # Create database connection
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print("Loading silver.telco_customers_clean from database...")

    df = pd.read_sql("SELECT * FROM silver.telco_customers_clean", engine)

    print(f"Dataset shape: {df.shape}")

    print("Running chi-square tests...")
    chi_square_results = run_chi_square_tests(df)

    print("Running Mann-Whitney U tests...")
    mann_whitney_results = run_mann_whitney_tests(df)

    print("Computing churn rate by contract with confidence intervals...")
    churn_rate_by_contract = compute_churn_rate_by_contract(df)

    output = {
        "dataset": "silver.telco_customers_clean",
        "row_count": int(len(df)),
        "chi_square_tests": chi_square_results,
        "mann_whitney_tests": mann_whitney_results,
        "churn_rate_by_contract": churn_rate_by_contract,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Statistical analysis saved to: {OUTPUT_PATH}")

    print("\nTop chi-square results (first 5):")
    for result in chi_square_results[:5]:
        print(result)

    print("\nMann-Whitney results:")
    for result in mann_whitney_results:
        print(result)

    print("\nChurn rate by contract:")
    for result in churn_rate_by_contract:
        print(result)


if __name__ == "__main__":
    main()
import pandas as pd
from fastapi import APIRouter, HTTPException

from src.db.connection import get_engine


# Create a router for customer-related endpoints
router = APIRouter()


@router.get("/risk-summary")
def get_risk_summary():
    """
    Return the number of customers in each churn risk category.
    """
    query = """
        SELECT risk_category, COUNT(*) AS customer_count
        FROM gold.customer_risk_segments
        GROUP BY risk_category
        ORDER BY risk_category;
    """

    engine = get_engine()
    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")


@router.get("/high-risk-customers")
def get_high_risk_customers(limit: int = 20):
    """
    Return the top high-risk customers ordered by churn probability.
    """
    query = f"""
        SELECT customer_id, churn_probability, churn_prediction, risk_category
        FROM gold.customer_risk_segments
        WHERE risk_category = 'High'
        ORDER BY churn_probability DESC
        LIMIT {limit};
    """

    engine = get_engine()
    df = pd.read_sql(query, engine)

    return df.to_dict(orient="records")


@router.get("/customer/{customer_id}")
def get_customer_by_id(customer_id: str):
    """
    Return churn risk information for a specific customer.
    """
    query = """
        SELECT customer_id, churn_probability, churn_prediction, risk_category
        FROM gold.customer_risk_segments
        WHERE customer_id = %(customer_id)s;
    """

    engine = get_engine()
    df = pd.read_sql(query, engine, params={"customer_id": customer_id})

    if df.empty:
        raise HTTPException(status_code=404, detail="Customer not found")

    return df.to_dict(orient="records")[0]
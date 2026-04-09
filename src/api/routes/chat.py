import re

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.chatbot.response_generator import generate_llm_response
from src.db.connection import get_engine
from src.retention.strategy_rules import attach_retention_actions


router = APIRouter()


class ChatRequest(BaseModel):
    question: str


def extract_customer_id(question: str) -> str | None:
    """
    Extract a customer ID in the format 1234-ABCDE from the user question.
    """
    match = re.search(r"\b\d{4}-[A-Z0-9]{5}\b", question.upper())
    if match:
        return match.group(0)
    return None


@router.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    AI-powered chatbot endpoint for churn insights.
    """
    original_question = request.question
    question = original_question.lower()
    engine = get_engine()

    try:
        customer_id = extract_customer_id(original_question)

        # Customer-specific analysis
        if customer_id:
            query = """
            SELECT
                r.customer_id,
                r.churn_probability,
                r.churn_prediction,
                r.risk_category,
                CASE
                    WHEN f.gender_encoded = 1 THEN 'Female'
                    ELSE 'Male'
                END AS gender,
                CASE
                    WHEN f.senior_citizen = 1 THEN 'Yes'
                    ELSE 'No'
                END AS senior_citizen,
                CASE
                    WHEN f.has_partner = 1 THEN 'Yes'
                    ELSE 'No'
                END AS has_partner,
                CASE
                    WHEN f.has_dependents = 1 THEN 'Yes'
                    ELSE 'No'
                END AS has_dependents,
                f.tenure,
                f.monthly_charges,
                f.total_charges,
                CASE
                    WHEN f.contract_type = 0 THEN 'Month-to-month'
                    WHEN f.contract_type = 1 THEN 'One year'
                    WHEN f.contract_type = 2 THEN 'Two year'
                    ELSE 'Unknown'
                END AS contract_type,
                CASE
                    WHEN f.paperless_billing_encoded = 1 THEN 'Yes'
                    ELSE 'No'
                END AS paperless_billing
            FROM gold.customer_risk_segments r
            JOIN features.customer_churn_features f
                ON r.customer_id = f.customer_id
            WHERE r.customer_id = %(customer_id)s;
            """
            df = pd.read_sql(query, engine, params={"customer_id": customer_id})

            if df.empty:
                return {
                    "response": {
                        "summary": f"I could not find customer {customer_id} in the database.",
                        "customer_recommendations": [],
                        "priority_actions": "",
                    },
                    "data": [],
                }

            data = df.to_dict(orient="records")
            data = attach_retention_actions(data)
            structured_response = generate_llm_response(
                question=original_question,
                data=data,
            )

            return {
                "response": structured_response,
                "data": data,
            }

        # High-risk customers query with customer-level explanatory fields
        if (
            "high risk" in question
            or "highest risk" in question
            or "at risk" in question
            or ("customers" in question and "risk" in question)
        ):
            query = """
            SELECT
                r.customer_id,
                r.churn_probability,
                r.risk_category,
                f.tenure,
                f.monthly_charges,
                f.total_charges,
                CASE
                    WHEN f.contract_type = 0 THEN 'Month-to-month'
                    WHEN f.contract_type = 1 THEN 'One year'
                    WHEN f.contract_type = 2 THEN 'Two year'
                    ELSE 'Unknown'
                END AS contract_type,
                CASE
                    WHEN f.paperless_billing_encoded = 1 THEN 'Yes'
                    ELSE 'No'
                END AS paperless_billing,
                CASE
                    WHEN f.has_partner = 1 THEN 'Yes'
                    ELSE 'No'
                END AS has_partner,
                CASE
                    WHEN f.has_dependents = 1 THEN 'Yes'
                    ELSE 'No'
                END AS has_dependents
            FROM gold.customer_risk_segments r
            JOIN features.customer_churn_features f
                ON r.customer_id = f.customer_id
            WHERE r.risk_category = 'High'
            ORDER BY r.churn_probability DESC
            LIMIT 5;
            """
            df = pd.read_sql(query, engine)

            data = df.to_dict(orient="records")
            data = attach_retention_actions(data)
            structured_response = generate_llm_response(
                question=original_question,
                data=data,
            )

            return {
                "response": structured_response,
                "data": data,
            }

        # Risk summary query
        elif "summary" in question or "distribution" in question:
            query = """
            SELECT risk_category, COUNT(*) AS customer_count
            FROM gold.customer_risk_segments
            GROUP BY risk_category
            ORDER BY risk_category;
            """
            df = pd.read_sql(query, engine)

            data = df.to_dict(orient="records")
            structured_response = generate_llm_response(
                question=original_question,
                data=data,
            )

            return {
                "response": structured_response,
                "data": data,
            }

        # Churn drivers / feature importance query
        elif (
            "driver" in question
            or "drivers" in question
            or "factor" in question
            or "factors" in question
            or "importance" in question
            or "why do customers churn" in question
            or "main reasons for churn" in question
        ):
            query = """
            SELECT feature, importance
            FROM gold.model_feature_importance
            ORDER BY importance DESC
            LIMIT 5;
            """
            df = pd.read_sql(query, engine)

            data = df.to_dict(orient="records")
            structured_response = generate_llm_response(
                question=original_question,
                data=data,
            )

            return {
                "response": structured_response,
                "data": data,
            }

        # Default fallback
        else:
            return {
                "response": {
                    "summary": (
                        "I can help with churn insights. Try asking about risk summary, "
                        "high-risk customers, churn drivers, or analyze a specific customer ID."
                    ),
                    "customer_recommendations": [],
                    "priority_actions": "",
                },
                "data": [],
            }

    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
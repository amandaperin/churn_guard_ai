import json


def build_chat_prompt(question: str, data: list[dict]) -> str:
        
    """
    Build a prompt that instructs the LLM to answer in structured JSON format.
    """
    formatted_data = json.dumps(data, indent=2)

    prompt = f"""
    You are Churn Advisor, an AI assistant for churn risk analysis.

    Your task is to answer business questions about customer churn using ONLY the provided data.

    Rules:
    - Use only the provided data.
    - Do not invent customers, probabilities, or business facts.
    - If no relevant data is found, return a valid JSON object with empty fields.
    - If rule-based recommended_actions are present, use them as the main basis for recommendations.
    - Keep language business-friendly and concise.
    - Do not use markdown.
    - Return ONLY valid JSON.
    - Do not wrap the JSON in code fences.

    Expected output formats:

    1. If the question is about multiple customers:
    {{
    "summary": "short paragraph",
    "customer_recommendations": [
    {{
    "customer_id": "customer id",
    "reason": "short explanation",
    "recommended_action": "short action"
    }}
    ],
    "priority_actions": "short paragraph"
    }}

    2. If the question is about one customer:
    {{
    "summary": "short paragraph",
    "customer_recommendations": [
    {{
    "customer_id": "customer id",
    "reason": "short explanation",
    "recommended_action": "short action"
    }}
    ],
    "priority_actions": "short paragraph"
    }}

    3. If the question is about churn drivers or summary:
    {{
    "summary": "short paragraph",
    "customer_recommendations": [],
    "priority_actions": "short paragraph"
    }}

    User question:
    {question}

    Structured data:
    {formatted_data}
    """
    return prompt

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from src.chatbot.prompt_builder import build_chat_prompt


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


def generate_llm_response(question: str, data: list[dict]) -> dict:
    """
    Generate a structured JSON response using an LLM.
    """
    provider = os.getenv("LLM_PROVIDER", "openai")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    api_key = os.getenv("OPENAI_API_KEY")

    if provider != "openai":
        raise ValueError("Unsupported LLM provider. Only 'openai' is configured for now.")

    if not api_key:
        raise ValueError(
            f"Missing OPENAI_API_KEY in environment variables. Expected .env at: {ENV_PATH}"
        )

    client = OpenAI(api_key=api_key)

    prompt = build_chat_prompt(question=question, data=data)

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    raw_text = response.output_text.strip()

    try:
        parsed = json.loads(raw_text)
        return parsed
    except json.JSONDecodeError:
        return {
            "summary": raw_text,
            "customer_recommendations": [],
            "priority_actions": "",
        }
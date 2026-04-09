from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_chat_fallback_response() -> None:
    """
    Test whether the chat endpoint returns a fallback response for unsupported questions.
    """
    payload = {"question": "Hello, what can you do?"}
    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert "answer" in response.json()
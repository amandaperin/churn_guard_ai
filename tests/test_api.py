from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    """
    Test whether the health endpoint returns status ok.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
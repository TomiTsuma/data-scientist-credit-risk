from fastapi.testclient import TestClient
from src.deployment.api.app import app


def test_api_root():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

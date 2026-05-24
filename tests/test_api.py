from fastapi.testclient import TestClient

from src.deployment.api.app import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_segment_endpoint():
    response = client.post(
        "/api/segment",
        json={
            "customer_id": "CUST-TEST",
            "age": 40,
            "account_age_days": 500,
            "financed_amount": 200000,
            "outstanding_balance": 40000,
            "repayment_progress": 0.8,
            "is_in_arrears": 0,
            "is_default": 0,
            "is_healthy": 1,
            "country_name": "Kenya",
            "payment_type": "PAYG",
            "product_tier": "New",
        },
    )
    if response.status_code == 503:
        return  # model not trained in CI without data
    assert response.status_code == 200
    body = response.json()
    assert "segment_id" in body
    assert "segment_name" in body

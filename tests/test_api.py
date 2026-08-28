from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_PAYLOAD = {
    "full_name": "علی رضایی",
    "age": 35,
    "score": 82.5,
    "requested_loan": 500000000,
    "salary": 25000000,
    "salary_deduction": 3000000,
    "collateral": 700000000,
    "job": "کارمند",
    "work_years": 8,
}


def test_health_and_valid_loan_request():
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/api/loan-requests", json=VALID_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"] == VALID_PAYLOAD


def test_missing_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    del payload["job"]
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_non_numeric_and_negative_values_are_rejected():
    non_numeric = VALID_PAYLOAD.copy()
    non_numeric["age"] = "سی و پنج"
    assert client.post("/api/loan-requests", json=non_numeric).status_code == 422

    negative = VALID_PAYLOAD.copy()
    negative["salary"] = -1
    assert client.post("/api/loan-requests", json=negative).status_code == 422

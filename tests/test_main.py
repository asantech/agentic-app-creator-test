from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


VALID_PAYLOAD = {
    "full_name": "علی رضایی",
    "age": 35,
    "score": 800,
    "requested_loan": 250000000,
    "salary": 30000000,
    "salary_deduction": 2000000,
    "collateral": 400000000,
    "job": "کارمند",
    "work_years": 8,
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_page_contains_rtl_form_and_all_fields():
    response = client.get("/")
    html = response.text
    assert response.status_code == 200
    assert '<html lang="fa" dir="rtl">' in html
    assert "درخواست وام" in html
    for field in (
        "full_name", "age", "score", "requested_loan", "salary",
        "salary_deduction", "collateral", "job", "work_years",
    ):
        assert f'name="{field}"' in html
    assert 'type="submit"' in html
    assert "event.preventDefault()" in html
    assert "fetch('/api/loan-requests'" in html
    assert "finally" in html


def test_valid_request_is_accepted_without_storage():
    response = client.post("/api/loan-requests", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert "موفقیت" in response.json()["message"]


def test_missing_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    del payload["job"]
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_negative_numeric_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["age"] = -1
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_non_numeric_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["salary"] = "نامشخص"
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_blank_text_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    payload["full_name"] = "   "
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422

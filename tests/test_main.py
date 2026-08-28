from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_REQUEST = {
    "first_name": "علی",
    "last_name": "رضایی",
    "age": 34,
    "score": 780,
    "requested_loan": 250000000,
    "salary": 30000000,
    "salary_deduction": 5000000,
    "collateral_amount": 400000000,
    "job": "کارمند",
    "work_experience": 8,
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_form_contains_persian_rtl_fields_and_submit_script():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'lang="fa"' in html
    assert 'dir="rtl"' in html
    assert "درخواست وام" in html
    for field in ("first_name", "last_name", "age", "score", "requested_loan", "salary", "salary_deduction", "collateral_amount", "job", "work_experience"):
        assert f'name="{field}"' in html
    assert '>تایید</button>' in html
    assert "event.preventDefault()" in html
    assert "fetch('/api/loan-requests'" in html


def test_valid_loan_request_is_accepted():
    response = client.post("/api/loan-requests", json=VALID_REQUEST)
    assert response.status_code == 200
    assert "موفقیت" in response.json()["message"]


def test_incomplete_non_numeric_and_negative_requests_are_rejected():
    incomplete = dict(VALID_REQUEST)
    incomplete.pop("job")
    assert client.post("/api/loan-requests", json=incomplete).status_code == 422

    non_numeric = dict(VALID_REQUEST, age="نامشخص")
    assert client.post("/api/loan-requests", json=non_numeric).status_code == 422

    negative = dict(VALID_REQUEST, salary=-1)
    assert client.post("/api/loan-requests", json=negative).status_code == 422

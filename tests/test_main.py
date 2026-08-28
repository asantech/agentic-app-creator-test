from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_REQUEST = {
    "full_name": "علی رضایی",
    "age": 32,
    "score": 850,
    "requested_loan": 500000000,
    "salary": 25000000,
    "salary_deduction": 3000000,
    "collateral": 700000000,
    "occupation": "کارمند",
    "work_experience": 7,
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_form_page_contains_rtl_fields_and_vanilla_js():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'dir="rtl"' in html
    assert "درخواست وام" in html
    for label in ["نام و نام خانوادگی", "سن", "امتیاز", "میزان وام درخواستی", "حقوق", "کسر از حقوق", "مقدار وثیقه", "شغل", "سنوات کاری"]:
        assert label in html
    assert '>تایید<' in html
    assert "addEventListener('submit'" in html
    assert "event.preventDefault()" in html
    assert "fetch('/api/loan-requests'" in html


def test_valid_loan_request_is_accepted():
    response = client.post("/api/loan-requests", json=VALID_REQUEST)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["full_name"] == "علی رضایی"


def test_missing_field_is_rejected():
    payload = VALID_REQUEST.copy()
    del payload["salary"]
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_negative_numeric_field_is_rejected():
    payload = VALID_REQUEST.copy()
    payload["collateral"] = -1
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_non_numeric_field_is_rejected():
    payload = VALID_REQUEST.copy()
    payload["age"] = "نامعتبر"
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422

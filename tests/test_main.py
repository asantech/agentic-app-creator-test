from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_PAYLOAD = {
    "full_name": "علی رضایی",
    "age": 35,
    "score": 80,
    "requested_loan": 500000000,
    "salary": 30000000,
    "salary_deduction": 5000000,
    "collateral": 700000000,
    "occupation": "مهندس",
    "work_experience": 8,
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_page_contains_rtl_form_and_all_fields():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'dir="rtl"' in html
    assert "درخواست وام" in html
    assert '<form id="loan-form"' in html
    for label in [
        "نام و نام خانوادگی", "سن", "امتیاز", "میزان وام درخواستی",
        "حقوق", "کسر از حقوق", "مقدار وثیقه", "شغل", "سنوات کاری",
    ]:
        assert label in html
    assert '>تأیید<' in html
    assert "fetch('/api/loan-requests'" in html
    assert "addEventListener('submit'" in html


def test_valid_loan_request_is_accepted():
    response = client.post("/api/loan-requests", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert "با موفقیت ثبت شد" in response.json()["message"]


def test_blank_text_is_rejected():
    payload = {**VALID_PAYLOAD, "full_name": "   "}
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422


def test_negative_number_is_rejected():
    payload = {**VALID_PAYLOAD, "requested_loan": -1}
    response = client.post("/api/loan-requests", json=payload)
    assert response.status_code == 422

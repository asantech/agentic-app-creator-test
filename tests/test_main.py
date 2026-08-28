from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def valid_payload() -> dict:
    return {
        "full_name": "علی رضایی",
        "age": 35,
        "score": 85,
        "requested_loan": 500000000,
        "salary": 30000000,
        "salary_deduction": 5000000,
        "collateral": 800000000,
        "occupation": "کارمند",
        "work_years": 8,
    }


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_contains_rtl_form_and_all_fields() -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'lang="fa"' in html
    assert 'dir="rtl"' in html
    assert "درخواست وام" in html
    for label in [
        "نام و نام خانوادگی", "سن", "امتیاز", "میزان وام درخواستی",
        "حقوق", "کسر از حقوق", "مقدار وثیقه", "شغل", "سنوات کاری", "تأیید",
    ]:
        assert label in html
    assert "fetch('/api/loan-applications'" in html


def test_valid_application_is_accepted() -> None:
    response = client.post("/api/loan-applications", json=valid_payload())
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["application"]["full_name"] == "علی رضایی"


def test_negative_numeric_value_is_rejected() -> None:
    payload = valid_payload()
    payload["age"] = -1
    response = client.post("/api/loan-applications", json=payload)
    assert response.status_code == 422


def test_blank_text_value_is_rejected() -> None:
    payload = valid_payload()
    payload["occupation"] = "   "
    response = client.post("/api/loan-applications", json=payload)
    assert response.status_code == 422

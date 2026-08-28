from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


VALID_PAYLOAD = {
    "name": "علی رضایی",
    "email": "ali@example.com",
    "phone": "09121234567",
    "company": "شرکت نمونه",
    "job_title": "مدیر محصول",
    "address": "خیابان ولیعصر، پلاک ۱۰",
    "city": "تهران",
    "postal_code": "1234567890",
    "message": "برای دریافت اطلاعات بیشتر تماس بگیرید.",
}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_form_has_rtl_bootstrap_and_all_fields():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert '<html lang="fa" dir="rtl">' in html
    assert "bootstrap.rtl.min.css" in html
    for field in VALID_PAYLOAD:
        assert f'name="{field}"' in html
        assert f'for="{field}"' in html
    assert 'class="container' in html
    assert 'class="card' in html
    assert 'class="form-control"' in html
    assert 'class="btn btn-primary' in html
    assert 'class="alert' in html


def test_submit_accepts_existing_payload_contract():
    response = client.post("/submit", json=VALID_PAYLOAD)
    assert response.status_code == 200
    assert "موفقیت" in response.json()["message"]


def test_submit_rejects_invalid_payload():
    invalid = dict(VALID_PAYLOAD)
    invalid["email"] = "not-an-email"
    invalid["name"] = ""
    response = client.post("/submit", json=invalid)
    assert response.status_code == 422


def test_form_submission_is_fetch_based_and_restores_button():
    html = client.get("/").text
    assert "event.preventDefault()" in html
    assert "fetch('/submit'" in html
    assert "button.disabled = false" in html
    assert "showStatus(result.message, 'success')" in html

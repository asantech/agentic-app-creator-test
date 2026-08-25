from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_is_available():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_form_has_requested_persian_content_and_rtl_right_layout():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert '<h1 id="form-title">درخواست وام</h1>' in html
    assert '<button type="submit">ارسال</button>' in html
    assert 'lang="fa" dir="rtl"' in html
    assert "direction: rtl" in html
    assert "justify-content: flex-end" in html
    assert "margin-left: auto" in html


def test_removed_fields_and_subtitle_are_not_in_form():
    html = client.get("/").text
    form = html.split('<form id="loan-form">', 1)[1].split("</form>", 1)[0]
    assert "email" not in form.lower()
    assert "message" not in form.lower()
    assert "textarea" not in form.lower()
    assert "زیر عنوان" not in form
    assert form.count('name="') == 4


def test_submit_accepts_only_remaining_form_fields():
    response = client.post(
        "/api/loan-request",
        json={
            "full_name": "علی رضایی",
            "phone": "09121234567",
            "amount": 50000000,
            "employment": "شاغل",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

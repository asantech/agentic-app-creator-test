from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_page_contains_persian_rtl_form():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert '<html lang="fa" dir="rtl">' in html
    assert "<title>درخواست وام</title>" in html
    assert '<h1 id="page-title">درخواست وام</h1>' in html
    for name in (
        "full_name", "age", "score", "requested_loan", "salary",
        "salary_deduction", "collateral", "job", "work_years",
    ):
        assert f'name="{name}"' in html
    assert "تأیید" in html


def test_static_javascript_handles_submission():
    response = client.get("/static/app.js")
    assert response.status_code == 200
    script = response.text
    assert "event.preventDefault()" in script
    assert "fetch('/api/loan-requests'" in script
    assert "response.ok" in script
    assert "finally" in script


def test_styles_include_rtl_and_responsive_layout():
    css = client.get("/static/styles.css").text
    assert "direction: rtl" in css
    assert "@media" in css
    assert "grid-template-columns" in css

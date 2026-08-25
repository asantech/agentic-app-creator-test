from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_form_has_rtl_rating_control_and_limits():
    html = client.get("/").text
    assert 'lang="fa"' in html
    assert 'dir="rtl"' in html
    assert 'for="rating"' in html
    assert 'name="rating"' in html
    assert 'type="number"' in html
    assert 'min="1"' in html
    assert 'max="5"' in html
    assert 'امتیاز (۱ تا ۵)' in html


def test_javascript_validates_and_sends_rating():
    html = client.get("/").text
    assert "Number.isInteger(ratingValue)" in html
    assert "ratingValue < 1 || ratingValue > 5" in html
    assert "rating: ratingValue" in html
    assert "Content-Type': 'application/json'" in html
    assert "fetch('/api/feedback'" in html

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload(rating):
    return {
        "name": "کاربر نمونه",
        "email": "user@example.com",
        "message": "تجربه خوبی بود.",
        "rating": rating,
    }


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_ratings_are_accepted_and_returned():
    for rating in (1, 3, 5):
        response = client.post("/api/feedback", json=payload(rating))
        assert response.status_code == 200
        assert response.json()["data"]["rating"] == rating


def test_out_of_range_ratings_are_rejected():
    for rating in (0, 6):
        response = client.post("/api/feedback", json=payload(rating))
        assert response.status_code == 422


def test_non_integer_ratings_are_rejected():
    for rating in (3.5, "3", "نامعتبر", True):
        response = client.post("/api/feedback", json=payload(rating))
        assert response.status_code == 422

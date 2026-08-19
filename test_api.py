"""
Quick smoke tests for the URL shortener API.

Uses an in-memory SQLite database instead of PostgreSQL purely so the
tests run instantly with zero external setup. The application code
itself (models/crud/routes) is unchanged and works identically against
real PostgreSQL — SQLAlchemy abstracts the database differences.

Run with:  pytest test_api.py -v
"""
import os

# Point the app at a throwaway file-based SQLite DB *before* importing it,
# since app.database builds its engine once at import time. (A ":memory:"
# DB won't work here because each pooled connection would see a fresh,
# empty database.)
TEST_DB_PATH = "./test.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shorten_url_returns_short_code():
    response = client.post("/shorten", json={"original_url": "https://www.example.com/some/long/path"})
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == "https://www.example.com/some/long/path"
    assert data["short_url"].endswith(data["short_code"])


def test_shorten_same_url_returns_same_code():
    r1 = client.post("/shorten", json={"original_url": "https://duplicate-test.com/"})
    r2 = client.post("/shorten", json={"original_url": "https://duplicate-test.com/"})
    assert r1.json()["short_code"] == r2.json()["short_code"]


def test_shorten_rejects_invalid_url():
    response = client.post("/shorten", json={"original_url": "not-a-valid-url"})
    assert response.status_code == 422


def test_redirect_to_original_url():
    create_resp = client.post("/shorten", json={"original_url": "https://redirect-test.com/page"})
    short_code = create_resp.json()["short_code"]

    redirect_resp = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"] == "https://redirect-test.com/page"


def test_redirect_unknown_code_returns_404():
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_stats_endpoint_tracks_clicks():
    create_resp = client.post("/shorten", json={"original_url": "https://stats-test.com/"})
    short_code = create_resp.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)
    client.get(f"/{short_code}", follow_redirects=False)

    stats_resp = client.get(f"/shorten/{short_code}/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["clicks"] == 2

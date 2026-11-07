import pytest

from shortener.app import create_app, is_valid_url
from shortener.storage import MemoryStorage


@pytest.fixture
def client():
    app = create_app(storage=MemoryStorage())
    app.config["TESTING"] = True
    return app.test_client()


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_shorten_and_redirect(client):
    resp = client.post("/shorten", json={"url": "https://example.com/page"})
    assert resp.status_code == 201
    code = resp.get_json()["code"]
    assert len(code) == 7

    redirect_resp = client.get(f"/{code}")
    assert redirect_resp.status_code == 302
    assert redirect_resp.headers["Location"] == "https://example.com/page"


def test_inspect_returns_original_url(client):
    code = client.post("/shorten", json={"url": "https://example.com"}).get_json()["code"]
    resp = client.get(f"/api/urls/{code}")
    assert resp.status_code == 200
    assert resp.get_json()["url"] == "https://example.com"


@pytest.mark.parametrize(
    "payload",
    [{}, {"url": ""}, {"url": "not-a-url"}, {"url": "ftp://example.com"}, {"url": 123}],
)
def test_shorten_rejects_invalid_urls(client, payload):
    resp = client.post("/shorten", json=payload)
    assert resp.status_code == 400


def test_unknown_code_returns_404(client):
    assert client.get("/doesnotexist").status_code == 404


def test_delete(client):
    code = client.post("/shorten", json={"url": "https://example.com"}).get_json()["code"]
    assert client.delete(f"/{code}").status_code == 204
    assert client.get(f"/{code}").status_code == 404
    assert client.delete(f"/{code}").status_code == 404


def test_metrics_endpoint_exposes_counters(client):
    client.get("/health")
    body = client.get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


def test_is_valid_url():
    assert is_valid_url("http://a.com")
    assert not is_valid_url("javascript:alert(1)")
    assert not is_valid_url("https://" + "a" * 3000)
"""MongoStorage tests using mongomock (an in-memory fake of pymongo),
so no real MongoDB is needed to run them."""
import mongomock
import pytest

from shortener.app import create_app
from shortener.storage import MongoStorage


@pytest.fixture
def storage():
    return MongoStorage(client=mongomock.MongoClient())


def test_create_and_get(storage):
    code = storage.create("https://example.com")
    assert len(code) == 7
    assert storage.get(code) == "https://example.com"


def test_get_missing_returns_none(storage):
    assert storage.get("nope") is None


def test_delete(storage):
    code = storage.create("https://example.com")
    assert storage.delete(code) is True
    assert storage.get(code) is None
    assert storage.delete(code) is False


def test_unique_index_exists(storage):
    indexes = storage._urls.index_information()
    assert any(info.get("unique") for info in indexes.values())


def test_ping(storage):
    assert storage.ping() is True


def test_api_works_with_mongo_storage(storage):
    app = create_app(storage=storage)
    client = app.test_client()
    resp = client.post("/shorten", json={"url": "https://example.com/x"})
    assert resp.status_code == 201
    code = resp.get_json()["code"]
    assert client.get(f"/{code}").headers["Location"] == "https://example.com/x"
    assert client.get("/health").status_code == 200
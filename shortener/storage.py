"""Storage backends for the URL shortener.

Two backends share the same small interface:
  - MemoryStorage: used in unit tests and when MONGODB_URI is not set
  - MongoStorage:  used in Docker Compose and real deployments
"""
import secrets
import string
import threading
from datetime import  datetime, timezone

ALPHABET = string.ascii_letters + string.digits


def generate_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


class MemoryStorage:
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def create(self, url: str) -> str:
        with self._lock:
            code = generate_code()
            while code in self._data:
                code = generate_code()
            self._data[code] = url
            return code

    def get(self, code: str):
        return self._data.get(code)

    def delete(self, code: str) -> bool:
        with self._lock:
            return self._data.pop(code, None) is not None

    def ping(self) -> bool:
        return True


class MongoStorage:
    def __init__(self, uri=None, db_name="shortener", client=None):
        # pymongo is imported lazily so unit tests that use MemoryStorage
        # don't need it. A ready-made client can be passed in (tests do this).
        from pymongo import MongoClient, errors

        self._errors = errors
        self._client = client or MongoClient(uri, serverSelectionTimeoutMS=3000)
        self._urls = self._client[db_name]["urls"]
        # A unique index on "code" plays the role of a primary key.
        self._urls.create_index("code", unique=True)

    def create(self, url: str) -> str:
        for _ in range(5):
            code = generate_code()
            try:
                self._urls.insert_one(
                    {"code": code, "url": url, "created_at": datetime.now(timezone.utc)}
                )
                return code
            except self._errors.DuplicateKeyError:
                continue
        raise RuntimeError("could not generate a unique code")

    def get(self, code: str):
        doc = self._urls.find_one({"code": code}, {"_id": 0, "url": 1})
        return doc["url"] if doc else None

    def delete(self, code: str) -> bool:
        return self._urls.delete_one({"code": code}).deleted_count > 0

    def ping(self) -> bool:
        try:
            self._client.admin.command("ping")
            return True
        except self._errors.PyMongoError:
            return False
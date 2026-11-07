"""Tiny URL shortener API. The app is deliberately simple: the DevOps work
around it (containers, CI/CD, IaC, monitoring) is the point of the project."""
import os
import time
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, redirect, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

from shortener.storage import MemoryStorage, MongoStorage

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency in seconds", ["endpoint"]
)


def is_valid_url(value) -> bool:
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parsed = urlparse(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def build_storage():
    uri = os.environ.get("MONGODB_URI")
    if uri:
        return MongoStorage(uri, db_name=os.environ.get("MONGO_DB", "shortener"))
    return MemoryStorage()


def create_app(storage=None):
    app = Flask(__name__)
    app.config["STORAGE"] = storage or build_storage()

    @app.before_request
    def _start_timer():
        request._start = time.perf_counter()

    @app.after_request
    def _record_metrics(response):
        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        start = getattr(request, "_start", None)
        if start is not None:
            REQUEST_LATENCY.labels(endpoint).observe(time.perf_counter() - start)
        REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
        return response

    @app.get("/health")
    def health():
        db_ok = app.config["STORAGE"].ping()
        status = 200 if db_ok else 503
        return jsonify(status="ok" if db_ok else "degraded", database=db_ok), status

    @app.post("/shorten")
    def shorten():
        payload = request.get_json(silent=True) or {}
        url = payload.get("url")
        if not is_valid_url(url):
            return jsonify(error="a valid http(s) 'url' is required"), 400
        code = app.config["STORAGE"].create(url)
        return jsonify(code=code, short_url=request.host_url + code), 201

    @app.get("/<code>")
    def follow(code):
        url = app.config["STORAGE"].get(code)
        if url is None:
            return jsonify(error="not found"), 404
        return redirect(url, code=302)

    @app.get("/api/urls/<code>")
    def inspect(code):
        url = app.config["STORAGE"].get(code)
        if url is None:
            return jsonify(error="not found"), 404
        return jsonify(code=code, url=url)

    @app.delete("/<code>")
    def remove(code):
        if app.config["STORAGE"].delete(code):
            return "", 204
        return jsonify(error="not found"), 404

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return app
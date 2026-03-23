"""Tests for health endpoint, error handlers, and middleware."""

from unittest.mock import patch

from flask import Flask


def test_health_endpoint(client):
    """GET /health returns ok status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"


def test_404_triggers_http_error_handler(client, contractor_headers):
    """Hitting a nonexistent vendor triggers handle_http_error (404)."""
    resp = client.get(
        "/api/vendors/00000000-0000-0000-0000-000000000001",
        headers=contractor_headers,
    )
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_validation_error_handler(client):
    """POST /api/auth/login with invalid body triggers handle_validation_error."""
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_generic_error_handler_debug(app):
    """handle_generic_error returns str(e) in debug mode."""
    from app.middleware.error_handler import register_error_handlers

    test_app = Flask(__name__)
    test_app.debug = True
    register_error_handlers(test_app)

    @test_app.route("/boom")
    def boom_route():
        raise ValueError("boom")

    with test_app.test_client() as c:
        resp = c.get("/boom")
        assert resp.status_code == 500
        data = resp.get_json()
        assert "boom" in data["error"]


def test_generic_error_handler_non_debug(app):
    """handle_generic_error returns generic message in production mode."""
    from app.middleware.error_handler import register_error_handlers

    test_app = Flask(__name__)
    test_app.debug = False
    register_error_handlers(test_app)

    @test_app.route("/boom")
    def boom_route():
        raise ValueError("secret details")

    with test_app.test_client() as c:
        resp = c.get("/boom")
        assert resp.status_code == 500
        data = resp.get_json()
        assert data["error"] == "Internal server error"


def test_jwt_required_rls_middleware(app, client, contractor_headers):
    """jwt_required_rls decorator works on a custom route."""
    from app.middleware.auth import jwt_required_rls

    called = {"value": False}

    @jwt_required_rls
    def wrapped():
        called["value"] = True
        return {"ok": True}

    with (
        patch("app.middleware.auth.verify_jwt_in_request") as mock_verify,
        patch(
            "app.middleware.auth.get_jwt_identity", return_value="contractor-123"
        ) as mock_identity,
        patch("app.middleware.auth.set_current_contractor") as mock_set,
    ):
        result = wrapped()

    mock_verify.assert_called_once()
    mock_identity.assert_called_once()
    mock_set.assert_called_once_with("contractor-123")
    assert called["value"] is True
    assert result == {"ok": True}


def test_create_app_default_config():
    """create_app() without args reads FLASK_ENV and resolves a config."""
    import os

    from app import create_app

    original = os.environ.get("FLASK_ENV")
    os.environ["FLASK_ENV"] = "testing"
    try:
        test_app = create_app()
        assert test_app is not None
        assert test_app.config["TESTING"] is True
    finally:
        if original is None:
            os.environ.pop("FLASK_ENV", None)
        else:
            os.environ["FLASK_ENV"] = original

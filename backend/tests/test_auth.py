import pytest
from app import create_app
from models import db


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_register(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"


def test_register_duplicate_email(client):
    payload = {"username": "user1", "email": "dup@example.com", "password": "pass"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "secret"
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "secret"
    })
    assert response.status_code == 200


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401

from app.services.auth_service import verify_password
from sqlalchemy.exc import IntegrityError
import app.extensions as extensions
from flask_jwt_extended import create_access_token



def test_verify_password_no_hash():
    class Dummy:
        password_hash = None
    dummy = Dummy()
    assert verify_password(dummy, "pw") is False

DUPLICATE_KEY_MSG = (
    "duplicate key value violates unique "
    "constraint 'some_other_field'"
)

def test_register_duplicate_entry_branch(monkeypatch, client):
    """Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""
    def raise_integrity(*args, **kwargs):
        class DummyOrig:
            def __str__(self):
                return DUPLICATE_KEY_MSG
        raise IntegrityError("", None, DummyOrig())
    monkeypatch.setattr(extensions.db.session, "commit", raise_integrity)
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Zed",
            "last_name": "Other",
            "email": "zed@example.com",
            "username": "zedother",
            "password": "password123",
        },
    )
    assert resp.status_code == 409
    assert "Duplicate entry" in resp.get_json()["error"]
from app.services.auth_service import verify_password
from sqlalchemy.exc import IntegrityError
import app.extensions as extensions


def test_verify_password_no_hash():
    class Dummy:
        password_hash = None
    dummy = Dummy()
    assert verify_password(dummy, "pw") is False

DUPLICATE_KEY_MSG = (
    "duplicate key value violates unique "
    "constraint 'some_other_field'"
)


def test_register_duplicate_entry_branch(monkeypatch, client):
    """Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""
    def raise_integrity(*args, **kwargs):
        class DummyOrig:
            def __str__(self):
                return DUPLICATE_KEY_MSG
        raise IntegrityError("", None, DummyOrig())
    monkeypatch.setattr(extensions.db.session, "commit", raise_integrity)
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Zed",
            "last_name": "Other",
            "email": "zed@example.com",
            "username": "zedother",
            "password": "password123",
        },
    )
    assert resp.status_code == 409
    assert "Duplicate entry" in resp.get_json()["error"]

from app.services.auth_service import verify_password
from sqlalchemy.exc import IntegrityError
import app.extensions as extensions

def test_verify_password_no_hash():
    class Dummy:
        password_hash = None
    dummy = Dummy()
    assert verify_password(dummy, "pw") is False

DUPLICATE_KEY_MSG = (
    "duplicate key value violates unique "
    "constraint 'some_other_field'"
)

def test_register_duplicate_entry_branch(monkeypatch, client):
    """Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""
    def raise_integrity(*args, **kwargs):
        class DummyOrig:
            def __str__(self):
                return DUPLICATE_KEY_MSG
        raise IntegrityError("", None, DummyOrig())
    monkeypatch.setattr(extensions.db.session, "commit", raise_integrity)
    resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Zed",
            "last_name": "Other",
            "email": "zed@example.com",
            "username": "zedother",
            "password": "password123",
        },
    )
    assert resp.status_code == 409
    assert "Duplicate entry" in resp.get_json()["error"]

def test_register_duplicate_entry_branch(monkeypatch, client):
    """Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""

def test_register_duplicate_entry_branch(monkeypatch, client):
    """Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""
    def raise_integrity(*args, **kwargs):
        dummy = Dummy()
        assert verify_password(dummy, "pw") is False

    # Move the long string to a variable to avoid E501
    DUPLICATE_KEY_MSG = (
        "duplicate key value violates unique "
        "constraint 'some_" )

    from app.services.auth_service import verify_password
    from sqlalchemy.exc import IntegrityError
    import app.extensions as extensions

    class Dummy:
        password_hash = None
    dummy = Dummy()
    assert verify_password(dummy, "pw") is False


    DUPLICATE_KEY_MSG = (
        "duplicate key value violates unique "
        "constraint 'some_"
        "other_field'"
        )


"""Simulate IntegrityError with a non-username/email message to hit the generic duplicate entry branch."""
def raise_integrity(*args, **kwargs):
        class DummyOrig:
            def __str__(self):
                return DUPLICATE_KEY_MSG
        raise IntegrityError("", None, DummyOrig())
        monkeypatch.setattr(extensions.db.session, "commit", raise_integrity)
        resp = client.post(
        "/api/auth/register",
        json={
            "first_name": "Zed",
            "last_name": "Other",
            "email": "zed@example.com",
            "username": "zedother",
            "password": "password123",
        },
    )
        assert resp.status_code == 409
        assert "Duplicate entry" in resp.get_json()["error"]
def test_me_success(client, contractor_headers, test_contractor):
        resp = client.get("/api/auth/me", headers=contractor_headers)
        assert resp.status_code == 200
data = resp.get_json()
assert data["email"] == test_contractor.email
assert data["username"] == test_contractor.username


def test_me_not_found(client):
    # Use a JWT for a non-existent contractor
        from flask_jwt_extended import create_access_token

fake_id = "00000000-0000-0000-0000-000000000000"
token = create_access_token(identity=fake_id)
headers = {"Authorization": f"Bearer {token}"}
resp = client.get("/api/auth/me", headers=headers)
assert resp.status_code == 404
assert "error" in resp.get_json()


def test_me_unauthorized(client):
        resp = client.get("/api/auth/me")
assert resp.status_code == 401
assert "msg" in resp.get_json() or "error" in resp.get_json()


def test_register_db_unique_constraint(monkeypatch, client):
        """Simulate DB-level unique constraint violation for username."""
        payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "username": "alicesmith",
        "password": "password123",
    }
resp = client.post("/api/auth/register", json=payload)
assert resp.status_code == 201
data = resp.get_json()
assert data["email"] == payload["email"]
assert data["username"] == payload["username"]

def raise_integrity(*args, **kwargs):
        class DummyOrig:
            def __str__(self):
                return "duplicate key value violates unique constraint 'username'"
        raise IntegrityError("", None, DummyOrig())

    monkeypatch.setattr(extensions.db.session, "commit", raise_integrity)
resp = client.post("/api/auth/register", json=payload)
assert resp.status_code == 409
assert "Username already exists" in resp.get_json()["error"]


def test_register_db_generic_error(monkeypatch, client):
    """Simulate generic DB exception during registration."""
    payload = {
        "first_name": "Frank",
        "last_name": "Green",
        "email": "frank@example.com",
        "username": "frankgreen",
        "password": "password123",
    }
    import app.extensions as extensions

    def raise_generic(*args, **kwargs):
        raise Exception("DB is down")

    monkeypatch.setattr(extensions.db.session, "commit", raise_generic)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 500
    assert "DB is down" in resp.get_json()["error"]


    def test_login_inactive_account(client, test_contractor, test_contractor_password, db):
        """Test login returns 403 for inactive account."""
    # Set account_status to something not 'active'
    test_contractor.account_status = "suspended"
    db.session.commit()
    resp = client.post(
        "/api/auth/login",
        json={"email": test_contractor.email, "password": test_contractor_password},
    )
    assert resp.status_code == 403
    data = resp.get_json()
    assert "inactive" in data["error"].lower()
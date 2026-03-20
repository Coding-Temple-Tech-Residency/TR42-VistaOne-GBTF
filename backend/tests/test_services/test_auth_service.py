from app.models.contractors import Contractor
from app.services.auth_service import set_password, verify_password


def test_password_hashing(app):
    """Test that set_password hashes correctly and verify_password works."""
    with app.app_context():
        c = Contractor(
            first_name="Pwd",
            last_name="Test",
            email="pwd@example.com",
        )
        set_password(c, "secret")
        assert c.password_hash is not None
        assert verify_password(c, "secret") is True
        assert verify_password(c, "wrong") is False

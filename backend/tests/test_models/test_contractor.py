import pytest

from app.extensions import db
from app.models.contractors import Contractor
from app.services.auth_service import set_password, verify_password


def test_create_contractor(app):
    """Test creating a contractor and setting password."""
    with app.app_context():
        c = Contractor(
            first_name="Test", last_name="User", email="test2@example.com", username="testuser1"
        )
        set_password(c, "password123")
        db.session.add(c)
        db.session.commit()

        saved = Contractor.query.filter_by(email="test2@example.com").first()
        assert saved is not None
        assert saved.first_name == "Test"
        assert verify_password(saved, "password123") is True


def test_contractor_email_unique_constraint(app):
    """Test that duplicate emails are rejected."""
    with app.app_context():
        c1 = Contractor(
            first_name="One", last_name="User", email="unique@example.com", username="uniqueuser1"
        )
        set_password(c1, "pass")
        db.session.add(c1)
        db.session.commit()

        c2 = Contractor(
            first_name="Two",
            last_name="User",
            email="unique@example.com",
            username="uniqueuser2",
        )
        set_password(c2, "pass")
        db.session.add(c2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

"""Tests for app.utils.rls.set_current_contractor."""

import uuid


def test_set_current_contractor_with_id(app):
    """set_current_contractor executes SET with a valid contractor ID."""
    from app.utils.rls import set_current_contractor

    with app.app_context():
        contractor_id = str(uuid.uuid4())
        # Should not raise
        set_current_contractor(contractor_id)


def test_set_current_contractor_with_none(app):
    """set_current_contractor with None executes SET ... = NULL branch."""
    from app.utils.rls import set_current_contractor

    with app.app_context():
        # Should not raise
        set_current_contractor(None)


def test_set_current_contractor_set_then_clear(app):
    """set_current_contractor can be called multiple times in sequence."""
    from app.utils.rls import set_current_contractor

    with app.app_context():
        contractor_id = str(uuid.uuid4())
        set_current_contractor(contractor_id)
        set_current_contractor(None)

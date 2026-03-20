from sqlalchemy import text

from app.extensions import db


def set_current_contractor(contractor_id):
    """Set the PostgreSQL session variable for RLS."""
    if contractor_id:
        db.session.execute(
            text(f"SET app.current_contractor_id" f" = '{contractor_id}';")
        )
    else:
        db.session.execute(text("SET app.current_contractor_id = NULL;"))

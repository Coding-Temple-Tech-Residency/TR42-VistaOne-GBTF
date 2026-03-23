from sqlalchemy import text

from app.extensions import db


def set_current_contractor(contractor_id):
    """Set the PostgreSQL session variable for RLS."""
    if contractor_id:
        db.session.execute(
            text("SELECT set_config('app.current_contractor_id', :cid, false);"),
            {"cid": str(contractor_id)},
        )
    else:
        db.session.execute(
            text("SELECT set_config('app.current_contractor_id', :cid, false);"),
            {"cid": ""},
        )

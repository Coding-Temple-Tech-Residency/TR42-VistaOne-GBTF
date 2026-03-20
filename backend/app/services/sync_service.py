import uuid
from datetime import datetime, timezone

from app.extensions import db
from app.models import SiteVisit
from app.utils.logger import get_logger

logger = get_logger("services.sync")


def _model_to_dict(instance):
    """Convert SQLAlchemy instance to dict, handling UUID and datetime."""
    d = {}
    for col in instance.__table__.columns:
        value = getattr(instance, col.name)
        if isinstance(value, datetime):
            value = int(value.replace(tzinfo=timezone.utc).timestamp() * 1000)
        elif isinstance(value, uuid.UUID):
            value = str(value)
        d[col.name] = value
    return d


def pull_changes(contractor_id, last_pulled_at):
    """Return all records for this contractor changed after last_pulled_at."""
    if last_pulled_at is None:
        last_pulled_at = 0
    # Convert milliseconds to datetime
    since = datetime.fromtimestamp(last_pulled_at / 1000.0, tz=timezone.utc)

    changes = {
        "site_visits": {"created": [], "updated": [], "deleted": []},
        "progress_updates": {"created": [], "updated": [], "deleted": []},
        "task_executions": {"created": [], "updated": [], "deleted": []},
        "issues": {"created": [], "updated": [], "deleted": []},
        "photos": {"created": [], "updated": [], "deleted": []},
        "job_responses": {"created": [], "updated": [], "deleted": []},
        "job_completions": {"created": [], "updated": [], "deleted": []},
        "submissions": {"created": [], "updated": [], "deleted": []},
    }

    # Example for site_visits
    sv_qs = SiteVisit.query.filter(
        SiteVisit.contractor_id == contractor_id, SiteVisit.updated_at >= since
    ).all()
    for sv in sv_qs:
        key = "created" if sv.created_at >= since else "updated"
        changes["site_visits"][key].append(_model_to_dict(sv))

    # Deleted records would need to be tracked separately.

    # Repeat for other tables...

    new_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return changes, new_timestamp


def push_changes(contractor_id, client_changes):
    """Insert/update/delete records from client."""
    # Example for site_visits
    for record in client_changes.get("site_visits", {}).get("created", []):
        record["contractor_id"] = contractor_id
        sv = SiteVisit(**record)
        db.session.add(sv)

    for record in client_changes.get("site_visits", {}).get("updated", []):
        sv = SiteVisit.query.get(record["visit_id"])
        if sv and str(sv.contractor_id) == str(contractor_id):
            for k, v in record.items():
                setattr(sv, k, v)

    # Deletions: mark as deleted or remove
    for record_id in client_changes.get("site_visits", {}).get("deleted", []):
        sv = SiteVisit.query.get(record_id)
        if sv and str(sv.contractor_id) == str(contractor_id):
            db.session.delete(sv)  # or soft delete

    db.session.commit()

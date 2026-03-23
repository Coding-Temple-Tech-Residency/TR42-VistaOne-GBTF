"""Tests for sync_service pull_changes and push_changes."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import text


def test_pull_changes_empty(app, test_contractor):
    """pull_changes returns empty lists when there are no visits."""
    from app.services.sync_service import pull_changes

    with app.app_context():
        # Use a contractor_id that has no visits
        cid = str(test_contractor.contractor_id)
        changes, ts = pull_changes(cid, None)
        assert "site_visits" in changes
        assert changes["site_visits"]["created"] == []
        assert isinstance(ts, int)


def test_pull_changes_with_last_pulled_at(app, test_contractor):
    """pull_changes with lastPulledAt=1 (epoch ms) returns correct structure."""
    from app.services.sync_service import pull_changes

    with app.app_context():
        cid = str(test_contractor.contractor_id)
        changes, ts = pull_changes(cid, 1)
        assert "site_visits" in changes
        assert isinstance(ts, int)


def test_pull_changes_visit_in_created(app, test_contractor, test_job):
    """When a visit exists and lastPulledAt=0, it appears in 'created'."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import pull_changes

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
        )
        db.session.add(visit)
        db.session.commit()

        cid = str(test_contractor.contractor_id)
        changes, _ = pull_changes(cid, 0)
        created_ids = [v["visit_id"] for v in changes["site_visits"]["created"]]
        assert str(visit.visit_id) in created_ids

        # Cleanup
        db.session.delete(visit)
        db.session.commit()


def test_pull_changes_visit_in_updated(app, test_contractor, test_job):
    """When lastPulledAt is after created_at, the visit appears in 'updated'."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import pull_changes

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
        )
        db.session.add(visit)
        db.session.commit()

        # Move created_at to 2020 so it is before our lastPulledAt (2021)
        db.session.execute(
            text("UPDATE site_visits SET created_at = :ts WHERE visit_id = :id"),
            {
                "ts": datetime(2020, 1, 1, tzinfo=timezone.utc),
                "id": str(visit.visit_id),
            },
        )
        db.session.commit()

        # lastPulledAt = 2021-01-01 in ms
        last_pulled_at = int(datetime(2021, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
        cid = str(test_contractor.contractor_id)
        changes, _ = pull_changes(cid, last_pulled_at)
        updated_ids = [v["visit_id"] for v in changes["site_visits"]["updated"]]
        assert str(visit.visit_id) in updated_ids

        # Cleanup
        db.session.delete(visit)
        db.session.commit()


def test_push_changes_created(app, test_contractor, test_job):
    """push_changes creates a new SiteVisit from client data."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import push_changes

    with app.app_context():
        new_visit_id = str(uuid.uuid4())
        client_changes = {
            "site_visits": {
                "created": [
                    {
                        "visit_id": new_visit_id,
                        "job_id": str(test_job.job_id),
                        "check_in_time": datetime.now(timezone.utc).isoformat(),
                    }
                ],
                "updated": [],
                "deleted": [],
            }
        }
        push_changes(str(test_contractor.contractor_id), client_changes)

        # Cleanup (the visit was created by push_changes)
        sv = SiteVisit.query.filter_by(visit_id=new_visit_id).first()
        if sv:
            db.session.delete(sv)
            db.session.commit()


def test_push_changes_updated(app, test_contractor, test_job):
    """push_changes updates an existing SiteVisit."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import push_changes

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
        )
        db.session.add(visit)
        db.session.commit()

        client_changes = {
            "site_visits": {
                "created": [],
                "updated": [
                    {
                        "visit_id": str(visit.visit_id),
                        "visit_status": "completed",
                    }
                ],
                "deleted": [],
            }
        }
        push_changes(str(test_contractor.contractor_id), client_changes)

        db.session.refresh(visit)
        assert visit.visit_status == "completed"

        db.session.delete(visit)
        db.session.commit()


def test_push_changes_updated_wrong_contractor(app, test_contractor, test_job):
    """push_changes ignores updates for visits owned by another contractor."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import push_changes

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
            visit_status="in_progress",
        )
        db.session.add(visit)
        db.session.commit()

        client_changes = {
            "site_visits": {
                "created": [],
                "updated": [
                    {
                        "visit_id": str(visit.visit_id),
                        "visit_status": "completed",
                    }
                ],
                "deleted": [],
            }
        }
        other_contractor_id = str(uuid.uuid4())
        push_changes(other_contractor_id, client_changes)

        db.session.refresh(visit)
        # Status should remain unchanged
        assert visit.visit_status == "in_progress"

        db.session.delete(visit)
        db.session.commit()


def test_push_changes_deleted(app, test_contractor, test_job):
    """push_changes deletes a SiteVisit by ID."""
    from app.extensions import db
    from app.models.site_visits import SiteVisit
    from app.services.sync_service import push_changes

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
        )
        db.session.add(visit)
        db.session.commit()
        visit_id = visit.visit_id

        client_changes = {
            "site_visits": {
                "created": [],
                "updated": [],
                "deleted": [str(visit_id)],
            }
        }
        push_changes(str(test_contractor.contractor_id), client_changes)

        assert db.session.get(SiteVisit, visit_id) is None


def test_push_changes_delete_nonexistent(app, test_contractor):
    """push_changes silently ignores deletion of nonexistent IDs."""
    from app.services.sync_service import push_changes

    with app.app_context():
        # Should not raise
        push_changes(
            str(test_contractor.contractor_id),
            {
                "site_visits": {
                    "created": [],
                    "updated": [],
                    "deleted": [str(uuid.uuid4())],
                }
            },
        )


def test_push_changes_empty(app, test_contractor):
    """push_changes with empty changes dict is a no-op."""
    from app.services.sync_service import push_changes

    with app.app_context():
        push_changes(str(test_contractor.contractor_id), {})

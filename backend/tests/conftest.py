
import sys
from pathlib import Path
import pytest
from app.extensions import limiter
from app.extensions import db as _db
from sqlalchemy import text
from app import create_app
from config import TestingConfig
import uuid
from flask_jwt_extended import create_access_token, create_refresh_token

# Must insert backend/ onto sys.path before importing app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def disable_limiter(monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)

# -------------------- Core fixtures --------------------


@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        _db.session.commit()
        _db.create_all()
        # Create default partitions for range-partitioned tables so tests can INSERT rows
        for tbl, part in [
            ("vendor_sync_queue", "vendor_sync_queue_default"),
            ("audit_log", "audit_log_default"),
            ("local_sync_queue", "local_sync_queue_default"),
        ]:
            _db.session.execute(
                text(f"CREATE TABLE IF NOT EXISTS {part} " f"PARTITION OF {tbl} DEFAULT")
            )
        _db.session.commit()
        yield app
        # Teardown: drop policies, views, then tables
        _db.session.execute(text("DROP POLICY IF EXISTS " "job_access ON jobs CASCADE;"))
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "contractor_self_access " "ON contractors CASCADE;")
        )
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "site_visits_access " "ON site_visits CASCADE;")
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS " "progress_updates_access " "ON progress_updates CASCADE;"
            )
        )
        _db.session.execute(text("DROP POLICY IF EXISTS issues_access ON issues CASCADE;"))
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "task_executions_access " "ON task_executions CASCADE;")
        )
        _db.session.execute(text("DROP POLICY IF EXISTS photos_access ON photos CASCADE;"))
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "job_completions_access " "ON job_completions CASCADE;")
        )
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "submissions_access " "ON submissions CASCADE;")
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS " "local_sync_queue_access " "ON local_sync_queue CASCADE;"
            )
        )
        _db.session.execute(text("DROP VIEW IF EXISTS " "job_status_summary CASCADE;"))
        _db.session.execute(text("DROP VIEW IF EXISTS " "vendor_sync_status_view CASCADE;"))
        _db.session.commit()
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    """Provide the database session."""
    return _db


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


# -------------------- Test data fixtures --------------------
@pytest.fixture
def test_contractor(app):
    """Create a contractor for testing with a unique email."""
    from app.models.contractors import Contractor
    from app.models.enums import AccountStatus
    from app.services.auth_service import set_password

    with app.app_context():
        unique_email = f"john+{uuid.uuid4()}@example.com"
        c = Contractor(
            first_name="John",
            last_name="Doe",
            email=unique_email,
            username=f"johnuser_{uuid.uuid4().hex[:8]}",
            account_verified=True,
            account_status=AccountStatus.active,
        )
        set_password(c, "password")
        _db.session.add(c)
        _db.session.commit()
        # Refresh from DB to ensure latest state
        _db.session.refresh(c)
        yield c
        # Cleanup: delete the contractor
        _db.session.commit()


@pytest.fixture
def test_contractor_password():
    """Return the password used for test_contractor."""
    return "password"


@pytest.fixture
def contractor_headers(app, test_contractor):
    """Return headers with JWT access token for authenticated requests."""
    with app.app_context():
        access_token = create_access_token(identity=str(test_contractor.contractor_id))
        return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def refresh_headers(app, test_contractor):
    """Return headers with JWT refresh token for refresh endpoint."""
    with app.app_context():
        refresh_token = create_refresh_token(identity=str(test_contractor.contractor_id))
        return {"Authorization": f"Bearer {refresh_token}"}


@pytest.fixture
def test_job(app):
    """Create a job for testing."""
    from app.models.jobs import Job

    with app.app_context():
        job = Job(
            job_number=f"JOB-{uuid.uuid4().hex[:8].upper()}",
            job_name="Test Job",
            status="scheduled",
        )
        _db.session.add(job)
        _db.session.commit()
        yield job
        _db.session.delete(job)
        _db.session.commit()


@pytest.fixture
def test_job_with_assignment(app, test_job, test_contractor):
    """Create a job and assign the test contractor."""
    from app.models.job_assignments import JobAssignment

    with app.app_context():
        assignment = JobAssignment(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            assignment_status="active",
        )
        _db.session.add(assignment)
        _db.session.commit()
        yield test_job
        # Job cleanup handled by test_job fixture


@pytest.fixture
def test_issue(app, test_job, test_contractor):
    """Create an issue for testing."""
    from app.models.issues import Issue

    with app.app_context():
        issue = Issue(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            issue_title="Test Issue",
            issue_status="open",
        )
        _db.session.add(issue)
        _db.session.commit()
        yield issue
        _db.session.commit()


@pytest.fixture
def test_contractor_with_issues(app):
    """Create a contractor with issues for testing."""
    from app.models.contractors import Contractor
    from app.models.enums import AccountStatus
    from app.services.auth_service import set_password

    with app.app_context():
        unique_email = f"contractor+{uuid.uuid4()}@example.com"
        contractor = Contractor(
            first_name="Jane",
            last_name="Smith",
            email=unique_email,
            username=f"janeuser_{uuid.uuid4().hex[:8]}",
            account_verified=True,
            account_status=AccountStatus.active,
        )
        set_password(contractor, "password")
        _db.session.add(contractor)
        _db.session.commit()
        yield contractor
        # Teardown: only delete the contractor; cascade handles issues
        _db.session.delete(contractor)
        _db.session.commit()


@pytest.fixture
def test_vendor(app):
    """Create a vendor for testing."""
    from app.models.vendors import Vendor

    with app.app_context():
        vendor = Vendor(
            vendor_code=f"V-{uuid.uuid4().hex[:8].upper()}",
            vendor_name="Test Vendor",
            vendor_api_config={
                "endpoint": "http://vendor.example.com",
                "apiKey": "test-key",
            },
        )
        _db.session.add(vendor)
        _db.session.commit()
        yield vendor
        try:
            _db.session.delete(vendor)
            _db.session.commit()
        except Exception:
            _db.session.rollback()


@pytest.fixture
def test_task(app, test_job):
    """Create a task linked to test_job for testing."""
    from app.models.tasks import Task

    with app.app_context():
        task = Task(
            job_id=test_job.job_id,
            task_name="Test Task",
        )
        _db.session.add(task)
        _db.session.commit()
        yield task
        try:
            _db.session.delete(task)
            _db.session.commit()
        except Exception:
            _db.session.rollback()


@pytest.fixture
def test_visit(app, test_job, test_contractor):
    """Create a site visit for testing."""
    from datetime import datetime, timezone

    from app.models.site_visits import SiteVisit

    with app.app_context():
        visit = SiteVisit(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            check_in_time=datetime.now(timezone.utc),
        )
        _db.session.add(visit)
        _db.session.commit()
        yield visit
        try:
            _db.session.delete(visit)
            _db.session.commit()
        except Exception:
            _db.session.rollback()

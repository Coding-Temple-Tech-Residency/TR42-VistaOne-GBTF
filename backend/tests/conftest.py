import sys
import uuid
from pathlib import Path

# Must insert backend/ onto sys.path before importing app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402
from flask_jwt_extended import (  # noqa: E402
    create_access_token,
    create_refresh_token,
)
from sqlalchemy import text  # noqa: E402

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from config import TestingConfig  # noqa: E402


# -------------------- Core fixtures --------------------
@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        # Teardown: drop policies, views, then tables
        _db.session.execute(
            text("DROP POLICY IF EXISTS " "job_access ON jobs CASCADE;")
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS "
                "contractor_self_access "
                "ON contractors CASCADE;"
            )
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS " "site_visits_access " "ON site_visits CASCADE;"
            )
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS "
                "progress_updates_access "
                "ON progress_updates CASCADE;"
            )
        )
        _db.session.execute(
            text("DROP POLICY IF EXISTS issues_access ON issues CASCADE;")
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS "
                "task_executions_access "
                "ON task_executions CASCADE;"
            )
        )
        _db.session.execute(
            text("DROP POLICY IF EXISTS photos_access ON photos CASCADE;")
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS "
                "job_completions_access "
                "ON job_completions CASCADE;"
            )
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS " "submissions_access " "ON submissions CASCADE;"
            )
        )
        _db.session.execute(
            text(
                "DROP POLICY IF EXISTS "
                "local_sync_queue_access "
                "ON local_sync_queue CASCADE;"
            )
        )
        _db.session.execute(text("DROP VIEW IF EXISTS " "job_status_summary CASCADE;"))
        _db.session.execute(
            text("DROP VIEW IF EXISTS " "vendor_sync_status_view CASCADE;")
        )
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
    from app.services.auth_service import set_password

    with app.app_context():
        unique_email = f"john+{uuid.uuid4()}@example.com"
        c = Contractor(
            first_name="John",
            last_name="Doe",
            email=unique_email,
        )
        set_password(c, "password")
        _db.session.add(c)
        _db.session.commit()
        # Keep instance attached – do NOT expunge
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
        refresh_token = create_refresh_token(
            identity=str(test_contractor.contractor_id)
        )
        return {"Authorization": f"Bearer {refresh_token}"}


@pytest.fixture
def test_job(app):
    """Create a job for testing."""
    from app.models.jobs import Job

    with app.app_context():
        job = Job(
            job_number="JOB-123",
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
    from app.services.auth_service import set_password

    with app.app_context():
        unique_email = f"contractor+{uuid.uuid4()}@example.com"
        contractor = Contractor(
            first_name="Jane", last_name="Smith", email=unique_email
        )
        set_password(contractor, "password")
        _db.session.add(contractor)
        _db.session.commit()
        yield contractor
        # Teardown: only delete the contractor; cascade handles issues
        _db.session.delete(contractor)
        _db.session.commit()

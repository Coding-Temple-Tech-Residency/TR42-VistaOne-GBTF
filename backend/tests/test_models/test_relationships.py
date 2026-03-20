from app.extensions import db
from app.models.contractors import Contractor
from app.models.issues import Issue


def test_contractor_issues_cascade_delete(app, test_contractor, test_issue):
    """Deleting a contractor should delete related issues (if cascade set)."""
    with app.app_context():
        # Get fresh instances within this session
        contractor = db.session.get(Contractor, test_contractor.contractor_id)
        issue = db.session.get(Issue, test_issue.issue_id)
        assert issue.contractor_id == contractor.contractor_id  # type: ignore
        db.session.delete(contractor)
        db.session.commit()
        # Issue should be gone
        issue = db.session.get(Issue, test_issue.issue_id)
        assert issue is None


def test_job_assignments_foreign_key(app, test_job, test_contractor):
    """Test assigning a contractor to a job."""
    from app.models.job_assignments import JobAssignment

    with app.app_context():
        assignment = JobAssignment(
            job_id=test_job.job_id,
            contractor_id=test_contractor.contractor_id,
            is_primary=True,
        )
        db.session.add(assignment)
        db.session.commit()
        assert assignment.assignment_id is not None

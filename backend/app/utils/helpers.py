import uuid


def generate_job_number():
    """Generate a unique job number."""
    return (
        f"JOB-created_at = db.Column(db.DateTime, "
        f"server_default=func.now())-"
        f"{uuid.uuid4().hex[:6].upper()}"
    )


def generate_submission_number():
    """Generate a unique submission number."""
    return (
        f"SUB-created_at = db.Column(db.DateTime, "
        f"server_default=func.now())-"
        f"{uuid.uuid4().hex[:4].upper()}"
    )

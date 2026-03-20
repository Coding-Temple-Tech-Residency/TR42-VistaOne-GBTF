from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import cache, db
from app.middleware.auth import set_rls
from app.models.job_assignments import JobAssignment
from app.models.jobs import Job
from app.schemas.job import JobSchema
from app.schemas.job_assignment import JobAssignmentSchema
from app.utils.logger import get_logger

logger = get_logger("api.jobs")

bp = Blueprint("jobs", __name__)


@bp.route("/", methods=["GET"])
@jwt_required()
@set_rls
@cache.cached(timeout=60, query_string=True)
def get_jobs():
    get_jwt_identity()
    # RLS will automatically filter, but we can also join assignments if needed
    jobs = Job.query.filter(Job.deleted_at.is_(None)).all()
    schema = JobSchema(many=True)
    return jsonify(schema.dump(jobs))


@bp.route("/<uuid:job_id>", methods=["GET"])
@jwt_required()
@set_rls
def get_job(job_id):
    job = db.session.get(Job, job_id)
    schema = JobSchema()
    return jsonify(schema.dump(job))


@bp.route("/<uuid:job_id>/assignments", methods=["GET"])
@jwt_required()
@set_rls
def get_job_assignments(job_id):
    assignments = db.session.query(JobAssignment).filter_by(job_id=job_id).all()
    schema = JobAssignmentSchema(many=True)
    return jsonify(schema.dump(assignments))

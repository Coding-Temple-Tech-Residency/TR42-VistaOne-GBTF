from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.models.tasks import Task
from app.schemas.task_execution import TaskExecutionSchema
from app.utils.logger import get_logger

logger = get_logger("api.tasks")

bp = Blueprint("tasks", __name__)


@bp.route("/<uuid:task_id>/execute", methods=["POST"])
@jwt_required()
@set_rls
def execute_task(task_id):
    contractor_id = get_jwt_identity()
    task = db.get_or_404(Task, task_id)
    schema = TaskExecutionSchema()
    data = request.get_json()
    data["task_id"] = task_id
    data["job_id"] = task.job_id
    data["contractor_id"] = contractor_id
    execution = schema.load(data)
    db.session.add(execution)
    db.session.commit()
    logger.info("Task %s executed by contractor %s", task_id, contractor_id)
    return jsonify(schema.dump(execution)), 201

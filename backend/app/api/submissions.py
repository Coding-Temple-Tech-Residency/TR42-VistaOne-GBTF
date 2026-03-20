from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.schemas.submission import SubmissionSchema
from app.utils.logger import get_logger

logger = get_logger("api.submissions")

bp = Blueprint("submissions", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
@set_rls
def create_submission():
    contractor_id = get_jwt_identity()
    schema = SubmissionSchema()
    data = request.get_json()
    data["contractor_id"] = contractor_id
    submission = schema.load(data)
    db.session.add(submission)
    db.session.commit()
    logger.info("Submission created by contractor %s", contractor_id)
    return jsonify(schema.dump(submission)), 201

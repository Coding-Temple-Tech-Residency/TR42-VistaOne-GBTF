from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.schemas.issue import IssueSchema
from app.utils.logger import get_logger

logger = get_logger("api.issues")

bp = Blueprint("issues", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
@set_rls
def create_issue():
    contractor_id = get_jwt_identity()
    schema = IssueSchema()
    data = request.get_json()
    data["contractor_id"] = contractor_id
    issue = schema.load(data)
    db.session.add(issue)
    db.session.commit()
    logger.info("Issue created by contractor %s", contractor_id)
    return jsonify(schema.dump(issue)), 201

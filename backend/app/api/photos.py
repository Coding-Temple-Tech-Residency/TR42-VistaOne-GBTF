from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.schemas.photo import PhotoSchema
from app.utils.logger import get_logger

logger = get_logger("api.photos")

bp = Blueprint("photos", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
@set_rls
def upload_photo():
    contractor_id = get_jwt_identity()
    schema = PhotoSchema()
    data = request.get_json()
    data["contractor_id"] = contractor_id
    photo = schema.load(data)
    db.session.add(photo)
    db.session.commit()
    logger.info("Photo uploaded by contractor %s", contractor_id)
    return jsonify(schema.dump(photo)), 201

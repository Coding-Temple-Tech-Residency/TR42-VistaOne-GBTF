from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import limiter
from app.models.contractors import Contractor
from app.schemas.auth import LoginSchema
from app.services.auth_service import verify_password
from app.utils.logger import get_logger

logger = get_logger("api.auth")

bp = Blueprint("auth", __name__)

_login_schema = LoginSchema()


@bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")
def login():
    data = _login_schema.load(request.get_json() or {})

    email = data["email"]  # type: ignore
    contractor = Contractor.query.filter_by(email=email, deleted_at=None).first()
    if contractor and verify_password(contractor, data["password"]):  # type: ignore
        identity = str(contractor.contractor_id)
        logger.info("Login success for contractor %s", identity)
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    logger.warning("Failed login attempt for email %s", email)
    return jsonify({"error": "Invalid credentials", "status": 401}), 401


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

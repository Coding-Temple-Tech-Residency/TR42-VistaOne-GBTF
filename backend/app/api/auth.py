from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy.exc import IntegrityError

from app.extensions import limiter
from app.models.contractors import Contractor
from app.schemas.auth import LoginSchema
from app.schemas.contractor import ContractorSchema
from app.services.auth_service import hash_password, verify_password
from app.utils.logger import get_logger

logger = get_logger("api.auth")


bp = Blueprint("auth", __name__)
_contractor_schema = ContractorSchema()
# Registration endpoint


@bp.route("/register", methods=["POST"])
@limiter.limit("5/minute", override_defaults=False)
def register():
    data = request.get_json() or {}
    # Validate input
    try:
        contractor_data = _contractor_schema.load(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Check for duplicate username/email (pre-check, but DB is source of truth)
    if Contractor.query.filter_by(username=contractor_data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409
    if Contractor.query.filter_by(email=contractor_data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    # Hash password
    password = contractor_data.pop("password")
    contractor_data["password_hash"] = hash_password(password)

    contractor = Contractor(**contractor_data)
    try:
        from app.extensions import db

        db.session.add(contractor)
        db.session.commit()
    except IntegrityError as e:
        # Check if it's a unique constraint violation for username/email
        msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "username" in msg:
            return jsonify({"error": "Username already exists"}), 409
        if "email" in msg:
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": "Duplicate entry"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(_contractor_schema.dump(contractor)), 201


_login_schema = LoginSchema()


@bp.route("/login", methods=["POST"])
@limiter.limit("5/minute", override_defaults=False)
def login():
    data = _login_schema.load(request.get_json() or {})

    email = data["email"]  # type: ignore
    contractor = Contractor.query.filter_by(email=email, deleted_at=None).first()
    if contractor:
        # Check inactive
        if (
            hasattr(contractor, "account_status")
            and getattr(contractor, "account_status", None) is not None
        ):
            status_value = (
                contractor.account_status.value
                if hasattr(contractor.account_status, "value")
                else str(contractor.account_status)
            )
            if status_value.lower() != "active":
                logger.warning("Inactive account login attempt for %s", email)
                return jsonify({"error": "Account is inactive", "status": 403}), 403
        if verify_password(contractor, data["password"]):  # type: ignore
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


# Add /api/auth/me endpoint alias for profile


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    contractor_id = get_jwt_identity()
    contractor = Contractor.query.get(contractor_id)
    if not contractor:
        return jsonify({"error": "Not found"}), 404
    return jsonify(_contractor_schema.dump(contractor))


@bp.route("/refresh", methods=["POST"])
@limiter.limit("5/minute", override_defaults=False)
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

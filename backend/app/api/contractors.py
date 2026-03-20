from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.models.contractors import Contractor
from app.schemas.contractor import ContractorSchema
from app.utils.logger import get_logger

logger = get_logger("api.contractors")

bp = Blueprint("contractors", __name__)


@bp.route("/me", methods=["GET"])
@jwt_required()
@set_rls
def get_me():
    contractor_id = get_jwt_identity()
    contractor = db.get_or_404(Contractor, contractor_id)
    schema = ContractorSchema()
    return jsonify(schema.dump(contractor))


@bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():
    contractor_id = get_jwt_identity()
    contractor = db.get_or_404(Contractor, contractor_id)
    data = request.get_json()
    schema = ContractorSchema()

    new_contractor = schema.load(data, partial=True)

    # Update the existing contractor with only the fields provided
    for field in data.keys():
        if hasattr(new_contractor, field):
            setattr(contractor, field, getattr(new_contractor, field))

    db.session.commit()
    return schema.dump(contractor), 200

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import cache, db
from app.models.vendors import Vendor
from app.schemas.vendor import VendorSchema
from app.tasks.vendor_tasks import trigger_vendor_sync_task
from app.utils.logger import get_logger

logger = get_logger("api.vendors")

bp = Blueprint("vendors", __name__)


@bp.route("/", methods=["GET"])
@jwt_required()
@cache.cached(timeout=120, query_string=True)
def get_vendors():
    vendors = Vendor.query.filter_by(is_active=True).all()
    schema = VendorSchema(many=True)
    return jsonify(schema.dump(vendors))


@bp.route("/<uuid:vendor_id>", methods=["GET"])
@jwt_required()
def get_vendor(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id)
    schema = VendorSchema()
    return jsonify(schema.dump(vendor))


@bp.route("/", methods=["POST"])
@jwt_required()
def create_vendor():
    schema = VendorSchema()
    data = request.get_json()
    vendor = schema.load(data)
    db.session.add(vendor)
    db.session.commit()
    cache.clear()
    logger.info(
        "Vendor created: %s", vendor.vendor_id
    )  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue]
    return jsonify(schema.dump(vendor)), 201


@bp.route("/<uuid:vendor_id>", methods=["PUT"])
@jwt_required()
def update_vendor(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id)
    schema = VendorSchema(partial=True)
    data = request.get_json()
    validated = schema.load(data, partial=True)
    for key in data:
        setattr(vendor, key, getattr(validated, key))
    db.session.commit()
    cache.clear()
    return jsonify(schema.dump(vendor))


@bp.route("/<uuid:vendor_id>", methods=["DELETE"])
@jwt_required()
def delete_vendor(vendor_id):
    vendor = db.get_or_404(Vendor, vendor_id)
    vendor.is_active = False
    db.session.commit()
    cache.clear()
    logger.info("Vendor soft-deleted: %s", vendor_id)
    return "", 204


@bp.route("/<uuid:vendor_id>/sync", methods=["POST"])
@jwt_required()
def sync_vendor(vendor_id):
    db.get_or_404(Vendor, vendor_id)
    trigger_vendor_sync_task.delay(str(vendor_id))  # type: ignore
    logger.info("Vendor sync triggered: %s", vendor_id)
    return jsonify({"message": "Sync started"})

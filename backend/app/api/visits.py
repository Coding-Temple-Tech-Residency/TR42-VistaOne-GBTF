from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.middleware.auth import set_rls
from app.models.site_visits import SiteVisit
from app.schemas.site_visit import SiteVisitSchema
from app.utils.logger import get_logger

logger = get_logger("api.visits")

bp = Blueprint("visits", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
@set_rls
def create_visit():
    contractor_id = get_jwt_identity()
    schema = SiteVisitSchema()
    data = request.get_json()
    data["contractor_id"] = contractor_id
    visit = schema.load(data)
    db.session.add(visit)
    db.session.commit()
    logger.info("Visit created by contractor %s", contractor_id)
    return jsonify(schema.dump(visit)), 201


@bp.route("/<uuid:visit_id>", methods=["PUT"])
@jwt_required()
@set_rls
def update_visit(visit_id):
    contractor_id = get_jwt_identity()
    visit = SiteVisit.query.filter_by(
        visit_id=visit_id, contractor_id=contractor_id
    ).first_or_404()
    schema = SiteVisitSchema(partial=True)
    data = request.get_json()
    validated = schema.load(data, partial=True)
    for key in data:
        setattr(visit, key, getattr(validated, key))
    db.session.commit()
    return jsonify(schema.dump(visit))


@bp.route("/<uuid:visit_id>/checkout", methods=["POST"])
@jwt_required()
@set_rls
def checkout(visit_id):
    contractor_id = get_jwt_identity()
    visit = SiteVisit.query.filter_by(
        visit_id=visit_id, contractor_id=contractor_id
    ).first_or_404()
    data = request.get_json()
    visit.check_out_time = data.get("check_out_time")
    visit.check_out_location = data.get("check_out_location")
    db.session.commit()
    logger.info("Checkout for visit %s by contractor %s", visit_id, contractor_id)
    schema = SiteVisitSchema()
    return jsonify(schema.dump(visit))

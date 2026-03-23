from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import BadRequest

from app.middleware.auth import set_rls
from app.services.sync_service import pull_changes, push_changes
from app.utils.logger import get_logger

logger = get_logger("api.sync")

bp = Blueprint("sync", __name__)


@bp.route("/", methods=["POST"])
@jwt_required()
@set_rls
def sync():
    try:
        data = request.get_json() or {}
        contractor_id = get_jwt_identity()
        last_pulled_at = data.get("lastPulledAt")
        client_changes = data.get("changes", {})

        logger.info("Sync request from contractor %s", contractor_id)
        push_changes(contractor_id, client_changes)
        server_changes, new_timestamp = pull_changes(contractor_id, last_pulled_at)
        logger.info("Sync complete for contractor %s", contractor_id)

        return jsonify(
            {
                "changes": server_changes,
                "timestamp": new_timestamp,
                "conflicts": [],
            }
        )
    except BadRequest as e:
        logger.warning("Malformed JSON in sync endpoint: %s", e)
        return jsonify({"error": "Malformed JSON"}), 400
    except Exception as e:
        logger.exception("Internal error in sync endpoint: %s", e)
        return jsonify({"error": "Internal server error"}), 500

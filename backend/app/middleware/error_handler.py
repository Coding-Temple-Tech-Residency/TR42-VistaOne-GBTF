import traceback

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.utils.logger import get_logger

logger = get_logger("error_handler")


def _error_response(message, status_code, details=None):
    """Build a consistent JSON error envelope."""
    body = {"error": message, "status": status_code}
    if details is not None:
        body["details"] = details
    return jsonify(body), status_code


def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        logger.info("Validation error: %s", e.messages)
        return _error_response("Validation failed", 400, details=e.messages)

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        logger.warning("HTTP %s: %s %s", e.code, e.name, e.description)
        return _error_response(e.description, e.code)

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        logger.critical(
            "Unhandled exception: %s\n%s",
            e,
            traceback.format_exc(),
        )
        # Never expose internals in production
        if app.debug:
            return _error_response(str(e), 500)
        return _error_response("Internal server error", 500)

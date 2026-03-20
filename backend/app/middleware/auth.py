from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.utils.rls import set_current_contractor


def jwt_required_rls(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        contractor_id = get_jwt_identity()
        set_current_contractor(contractor_id)
        return fn(*args, **kwargs)

    return wrapper


def set_rls(f):
    """Decorator to set RLS context after JWT verification."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        contractor_id = get_jwt_identity()
        if contractor_id:
            set_current_contractor(contractor_id)
        return f(*args, **kwargs)

    return decorated_function

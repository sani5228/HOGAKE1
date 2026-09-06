from functools import wraps
from flask import request, g
from backend.utils.security import decode_jwt_token
from backend.utils.responses import error_response

def jwt_required(allowed_roles=None):
    """
    Decorator to protect routes with JWT authentication and optional RBAC.
    allowed_roles can be a string ('admin') or list of strings (['farmer', 'center', 'admin']).
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return error_response(
                    message="Authorization header is required",
                    error_code="UNAUTHORIZED",
                    status_code=401
                )

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return error_response(
                    message="Authorization header must be in format 'Bearer <token>'",
                    error_code="INVALID_HEADER",
                    status_code=401
                )

            token = parts[1]
            try:
                payload = decode_jwt_token(token)
            except ValueError as e:
                return error_response(
                    message=str(e),
                    error_code="TOKEN_ERROR",
                    status_code=401
                )

            user_role = payload.get('role')
            if allowed_roles and user_role not in allowed_roles:
                return error_response(
                    message=f"Forbidden: Access requires one of {allowed_roles} role(s)",
                    error_code="FORBIDDEN",
                    status_code=403
                )

            # Store in flask request context
            g.current_user = payload
            g.user_id = payload.get('user_id')
            g.role = user_role
            g.farmer_id = payload.get('farmer_id')
            g.center_id = payload.get('center_id')
            g.admin_id = payload.get('admin_id')

            return f(*args, **kwargs)
        return decorated_function
    return decorator

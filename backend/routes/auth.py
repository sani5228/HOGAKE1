from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.auth_service import AuthService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/otp/send', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    mobile = data.get('mobile_number')
    purpose = data.get('purpose', 'LOGIN')

    if not mobile:
        return error_response("Mobile number is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = AuthService.send_otp(db, mobile_number=mobile, purpose=purpose)
        return success_response(data=res, message="OTP generated and sent via simulated SMS.")
    except ValueError as e:
        return error_response(str(e), error_code="OTP_ERROR")
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@auth_bp.route('/otp/verify', methods=['POST'])
def verify_otp():
    data = request.get_json() or {}
    mobile = data.get('mobile_number')
    otp = data.get('otp')

    if not mobile or not otp:
        return error_response("Mobile number and OTP are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = AuthService.verify_otp(db, mobile_number=mobile, otp_input=otp)
        return success_response(data=res, message="OTP verified successfully.")
    except ValueError as e:
        return error_response(str(e), error_code="INVALID_OTP")
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@auth_bp.route('/center/login', methods=['POST'])
def center_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return error_response("Username and password are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = AuthService.login_center(db, username=username, password=password)
        return success_response(data=res, message="Procurement center login successful.")
    except ValueError as e:
        return error_response(str(e), error_code="AUTH_FAILED", status_code=401)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return error_response("Username and password are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = AuthService.login_admin(db, username=username, password=password)
        return success_response(data=res, message="Admin login successful.")
    except ValueError as e:
        return error_response(str(e), error_code="AUTH_FAILED", status_code=401)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return success_response(data=None, message="Logged out successfully.")

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    return success_response(data=g.current_user, message="Current authenticated user session.")

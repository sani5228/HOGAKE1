from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.farmer_service import FarmerService
from backend.services.booking_service import BookingService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

farmer_bp = Blueprint('farmer', __name__, url_prefix='/api/farmer')

@farmer_bp.route('/register', methods=['POST'])
def register_farmer():
    data = request.get_json() or {}
    db = next(get_db())
    try:
        res = FarmerService.register_farmer(db, data)
        return success_response(data=res, message="Farmer registration completed successfully.", status_code=201)
    except ValueError as e:
        return error_response(str(e), error_code="REGISTRATION_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@farmer_bp.route('/me', methods=['GET'])
@jwt_required(allowed_roles=['farmer'])
def get_farmer_profile():
    farmer_id = g.farmer_id
    if not farmer_id:
        return error_response("Farmer ID missing from session.", error_code="UNAUTHORIZED", status_code=401)

    db = next(get_db())
    profile = FarmerService.get_profile(db, farmer_id)
    if not profile:
        return error_response("Farmer profile not found.", error_code="NOT_FOUND", status_code=404)

    return success_response(data=profile, message="Farmer profile retrieved.")

@farmer_bp.route('/me/crops', methods=['PUT'])
@jwt_required(allowed_roles=['farmer'])
def update_farmer_crops():
    farmer_id = g.farmer_id
    data = request.get_json() or {}
    crop_ids = data.get('crop_ids', [])

    db = next(get_db())
    try:
        updated = FarmerService.update_crops(db, farmer_id, crop_ids)
        return success_response(data=updated, message="Registered crops updated successfully.")
    except Exception as e:
        return error_response(str(e), error_code="UPDATE_ERROR")

@farmer_bp.route('/me/bookings', methods=['GET'])
@jwt_required(allowed_roles=['farmer'])
def list_my_bookings():
    farmer_id = g.farmer_id
    status = request.args.get('status')
    db = next(get_db())
    bookings = BookingService.list_farmer_bookings(db, farmer_id, status=status)
    return success_response(data=[b.to_dict() for b in bookings], message="Bookings retrieved.")

@farmer_bp.route('/me/procurement-history', methods=['GET'])
@jwt_required(allowed_roles=['farmer'])
def list_my_procurements():
    farmer_id = g.farmer_id
    db = next(get_db())
    history = FarmerService.get_procurement_history(db, farmer_id)
    return success_response(data=history, message="Procurement and payment history retrieved.")

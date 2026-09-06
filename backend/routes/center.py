from datetime import datetime, date
from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.center_service import CenterService
from backend.services.booking_service import BookingService
from backend.services.procurement_service import ProcurementService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

center_bp = Blueprint('center', __name__, url_prefix='/api/center')

@center_bp.route('/register', methods=['POST'])
def register_center():
    data = request.get_json() or {}
    db = next(get_db())
    try:
        res = CenterService.register_center(db, data)
        return success_response(data=res, message="Center registration submitted for approval.", status_code=201)
    except ValueError as e:
        return error_response(str(e), error_code="REGISTRATION_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@center_bp.route('/me', methods=['GET'])
@jwt_required(allowed_roles=['center'])
def get_center_profile():
    center_id = g.center_id
    db = next(get_db())
    profile = CenterService.get_profile(db, center_id)
    if not profile:
        return error_response("Center profile not found.", error_code="NOT_FOUND", status_code=404)
    return success_response(data=profile, message="Center profile retrieved.")

@center_bp.route('/me/capacity', methods=['PUT'])
@jwt_required(allowed_roles=['center', 'admin'])
def update_capacity():
    center_id = g.center_id or request.args.get('center_id')
    data = request.get_json() or {}
    db = next(get_db())
    try:
        updated = CenterService.update_capacity(db, center_id, data)
        return success_response(data=updated, message="Capacity updated successfully.")
    except Exception as e:
        return error_response(str(e), error_code="UPDATE_ERROR")

@center_bp.route('/me/crops', methods=['PUT'])
@jwt_required(allowed_roles=['center', 'admin'])
def update_crops():
    center_id = g.center_id or request.args.get('center_id')
    data = request.get_json() or {}
    crop_ids = data.get('crop_ids', [])
    db = next(get_db())
    try:
        updated = CenterService.update_crops(db, center_id, crop_ids)
        return success_response(data=updated, message="Accepted crops updated successfully.")
    except Exception as e:
        return error_response(str(e), error_code="UPDATE_ERROR")

@center_bp.route('/me/schedule', methods=['GET'])
@jwt_required(allowed_roles=['center', 'admin'])
def get_schedule():
    center_id = g.center_id or request.args.get('center_id')
    date_str = request.args.get('date')
    sched_date = None
    if date_str:
        try:
            sched_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return error_response("Invalid date format. Use YYYY-MM-DD.", error_code="INVALID_DATE")

    db = next(get_db())
    try:
        schedule = CenterService.get_schedule_and_capacity(db, center_id, sched_date)
        return success_response(data=schedule, message="Daily schedule and capacity retrieved.")
    except Exception as e:
        return error_response(str(e), error_code="SCHEDULE_ERROR")

@center_bp.route('/me/bookings', methods=['GET'])
@jwt_required(allowed_roles=['center'])
def list_center_bookings():
    center_id = g.center_id
    date_str = request.args.get('date')
    shift = request.args.get('shift')
    status = request.args.get('status')
    sched_date = None
    if date_str:
        try:
            sched_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db = next(get_db())
    bookings = BookingService.list_center_bookings(db, center_id, sched_date=sched_date, shift=shift, status=status)
    return success_response(data=[b.to_dict() for b in bookings], message="Center bookings retrieved.")

@center_bp.route('/me/procurements', methods=['GET'])
@jwt_required(allowed_roles=['center'])
def list_center_procurements():
    center_id = g.center_id
    db = next(get_db())
    procurements = ProcurementService.list_center_procurements(db, center_id)
    return success_response(data=[p.to_dict() for p in procurements], message="Procurement records retrieved.")

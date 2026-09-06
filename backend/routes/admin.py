from datetime import datetime
from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.admin_service import AdminService
from backend.services.crop_service import CropService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def get_stats():
    db = next(get_db())
    stats = AdminService.get_system_stats(db)
    return success_response(data=stats, message="System statistics retrieved.")

@admin_bp.route('/farmers', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def list_farmers():
    query_str = request.args.get('search')
    status = request.args.get('status')
    db = next(get_db())
    farmers = AdminService.list_farmers(db, query_str=query_str, status=status)
    return success_response(data=farmers, message="Farmers list retrieved.")

@admin_bp.route('/farmers/<string:farmer_id>/status', methods=['PUT'])
@jwt_required(allowed_roles=['admin'])
def set_farmer_status(farmer_id: str):
    data = request.get_json() or {}
    new_status = data.get('status', 'ACTIVE')
    db = next(get_db())
    try:
        updated = AdminService.set_farmer_status(db, farmer_id, new_status)
        return success_response(data=updated, message="Farmer status updated.")
    except Exception as e:
        return error_response(str(e), error_code="UPDATE_ERROR")

@admin_bp.route('/centers', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def list_centers():
    status = request.args.get('status')
    query_str = request.args.get('search')
    db = next(get_db())
    centers = AdminService.list_centers(db, status=status, query_str=query_str)
    return success_response(data=centers, message="Centers list retrieved.")

@admin_bp.route('/centers/<string:center_id>/verify', methods=['PUT'])
@jwt_required(allowed_roles=['admin'])
def verify_center(center_id: str):
    data = request.get_json() or {}
    action = data.get('action', 'APPROVE')
    db = next(get_db())
    try:
        center = AdminService.verify_center(db, center_id, action)
        return success_response(data=center, message=f"Center status updated: {center['status']}")
    except ValueError as ve:
        return error_response(str(ve), error_code="VERIFY_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@admin_bp.route('/crops', methods=['GET'])
def list_crops():
    season = request.args.get('season')
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    db = next(get_db())
    crops = CropService.list_crops(db, season=season, active_only=active_only)
    return success_response(data=[c.to_dict() for c in crops], message="Crops list retrieved.")

@admin_bp.route('/crops', methods=['POST'])
@jwt_required(allowed_roles=['admin'])
def create_crop():
    data = request.get_json() or {}
    if not data.get('name') or data.get('rate_per_quintal') is None:
        return error_response("name and rate_per_quintal are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        crop = CropService.create_crop(db, data)
        return success_response(data=crop.to_dict(), message="Crop created successfully.", status_code=201)
    except Exception as e:
        return error_response(str(e), error_code="CREATE_ERROR")

@admin_bp.route('/crops/<int:crop_id>', methods=['PUT'])
@jwt_required(allowed_roles=['admin'])
def update_crop(crop_id: int):
    data = request.get_json() or {}
    db = next(get_db())
    try:
        crop = CropService.update_crop(db, crop_id, data)
        if not crop:
            return error_response(f"Crop #{crop_id} not found.", error_code="NOT_FOUND", status_code=404)
        return success_response(data=crop.to_dict(), message="Crop updated successfully.")
    except Exception as e:
        return error_response(str(e), error_code="UPDATE_ERROR")

@admin_bp.route('/crops/<int:crop_id>', methods=['DELETE'])
@jwt_required(allowed_roles=['admin'])
def delete_crop(crop_id: int):
    db = next(get_db())
    ok = CropService.delete_crop(db, crop_id)
    if not ok:
        return error_response(f"Crop #{crop_id} not found.", error_code="NOT_FOUND", status_code=404)
    return success_response(data=None, message="Crop deactivated successfully.")

@admin_bp.route('/bookings', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def list_all_bookings():
    center_id = request.args.get('center_id')
    crop_id = request.args.get('crop_id', type=int)
    status = request.args.get('status')
    date_str = request.args.get('date')
    b_date = None
    if date_str:
        try:
            b_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db = next(get_db())
    bookings = AdminService.list_all_bookings(db, center_id=center_id, crop_id=crop_id, status=status, booking_date=b_date)
    return success_response(data=bookings, message="All bookings retrieved.")

@admin_bp.route('/procurement-records', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def list_procurement_records():
    center_id = request.args.get('center_id')
    db = next(get_db())
    records = AdminService.list_procurement_records(db, center_id=center_id)
    return success_response(data=records, message="Procurement records retrieved.")

@admin_bp.route('/reports/capacity-utilization', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def capacity_report():
    date_str = request.args.get('date')
    target_date = None
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    db = next(get_db())
    report = AdminService.get_capacity_utilization_report(db, target_date=target_date)
    return success_response(data=report, message="Capacity utilization report generated.")

@admin_bp.route('/audit-log', methods=['GET'])
@jwt_required(allowed_roles=['admin'])
def get_audit_log():
    limit = request.args.get('limit', default=50, type=int)
    db = next(get_db())
    logs = AdminService.list_audit_logs(db, limit=limit)
    return success_response(data=logs, message="Audit log entries retrieved.")

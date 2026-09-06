from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.booking_service import BookingService
from backend.services.crop_service import CropService
from backend.services.scheduling_service import SchedulingService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

booking_bp = Blueprint('booking', __name__, url_prefix='/api/bookings')

@booking_bp.route('/eligible-crops', methods=['GET'])
@jwt_required(allowed_roles=['farmer'])
def get_eligible_crops():
    farmer_id = g.farmer_id
    db = next(get_db())
    crops = CropService.get_eligible_crops_for_farmer(db, farmer_id)
    return success_response(data=[c.to_dict() for c in crops], message="Eligible in-season crops retrieved.")

@booking_bp.route('', methods=['POST'])
@jwt_required(allowed_roles=['farmer', 'admin'])
def create_booking():
    data = request.get_json() or {}
    farmer_id = g.farmer_id or data.get('farmer_id')
    crop_id = data.get('crop_id')
    quantity = data.get('expected_quantity_quintal')
    channel = data.get('channel', 'WEB')

    if not farmer_id or not crop_id or quantity is None:
        return error_response("farmer_id, crop_id, and expected_quantity_quintal are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        booking = BookingService.create_booking(
            db=db,
            farmer_id=farmer_id,
            crop_id=int(crop_id),
            expected_quantity_quintal=float(quantity),
            channel=channel
        )
        return success_response(
            data=booking.to_dict(),
            message="Procurement slot allocated and booked successfully.",
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), error_code="BOOKING_REJECTED", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id: int):
    db = next(get_db())
    try:
        user_role = g.role
        identifier = g.farmer_id if user_role == 'farmer' else (g.center_id if user_role == 'center' else None)
        booking = BookingService.get_booking_by_id(db, booking_id, user_role=user_role, user_identifier=identifier)
        if not booking:
            return error_response(f"Booking #{booking_id} not found.", error_code="NOT_FOUND", status_code=404)
        return success_response(data=booking.to_dict(), message="Booking retrieved.")
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except Exception as e:
        return error_response(str(e), error_code="SERVER_ERROR", status_code=500)

@booking_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@jwt_required(allowed_roles=['farmer', 'admin'])
def cancel_booking(booking_id: int):
    db = next(get_db())
    actor_role = 'ADMIN' if g.role == 'admin' else 'FARMER'
    actor_id = g.admin_id if g.role == 'admin' else g.farmer_id
    try:
        booking = BookingService.cancel_booking(db, booking_id, actor_role=actor_role, actor_id=actor_id)
        return success_response(data=booking.to_dict(), message="Booking cancelled and capacity released successfully.")
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except ValueError as ve:
        return error_response(str(ve), error_code="CANCELLATION_ERROR", status_code=400)
    except Exception as e:
        return error_response(str(e), error_code="SERVER_ERROR", status_code=500)

@booking_bp.route('/<int:booking_id>/rebook', methods=['POST'])
@jwt_required(allowed_roles=['farmer'])
def rebook_booking(booking_id: int):
    data = request.get_json() or {}
    new_quantity = data.get('expected_quantity_quintal')
    db = next(get_db())
    try:
        new_booking = BookingService.rebook_booking(
            db,
            booking_id=booking_id,
            actor_id=g.farmer_id,
            new_quantity=new_quantity,
            channel=data.get('channel', 'WEB')
        )
        return success_response(
            data=new_booking.to_dict(),
            message="Booking rescheduled successfully. New slot allocated.",
            status_code=201
        )
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except ValueError as ve:
        return error_response(str(ve), error_code="REBOOK_ERROR", status_code=400)
    except Exception as e:
        return error_response(str(e), error_code="SERVER_ERROR", status_code=500)

@booking_bp.route('/estimate', methods=['GET'])
def estimate_time():
    crop_id = request.args.get('crop_id')
    quantity = request.args.get('quantity')
    if not crop_id or not quantity:
        return error_response("crop_id and quantity query parameters are required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    crop = CropService.get_crop_by_id(db, int(crop_id))
    if not crop:
        return error_response(f"Crop {crop_id} not found.", error_code="NOT_FOUND", status_code=404)

    try:
        qty = float(quantity)
        minutes = SchedulingService.calculate_estimated_time(crop, qty)
        return success_response(data={
            "crop_id": crop.crop_id,
            "crop_name": crop.name,
            "quantity_quintals": qty,
            "rate_per_quintal": float(crop.rate_per_quintal),
            "estimated_time_minutes": minutes,
            "estimated_total_value": round(qty * float(crop.rate_per_quintal), 2)
        }, message="Estimate calculated.")
    except Exception as e:
        return error_response(str(e), error_code="CALCULATION_ERROR")

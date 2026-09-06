from flask import Blueprint, request, g
from backend.database import get_db
from backend.services.procurement_service import ProcurementService
from backend.utils.responses import success_response, error_response
from backend.middleware.auth_middleware import jwt_required

procurement_bp = Blueprint('procurement', __name__, url_prefix='/api/procurement')

@procurement_bp.route('/<int:booking_id>/arrival', methods=['POST'])
@jwt_required(allowed_roles=['center'])
def mark_arrival(booking_id: int):
    center_id = g.center_id
    db = next(get_db())
    try:
        booking = ProcurementService.mark_arrival(db, booking_id=booking_id, center_id=center_id)
        return success_response(data=booking.to_dict(), message="Farmer marked as arrived.")
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except ValueError as ve:
        return error_response(str(ve), error_code="PROCUREMENT_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@procurement_bp.route('/verify-token', methods=['POST'])
@jwt_required(allowed_roles=['center'])
def verify_token():
    data = request.get_json() or {}
    token = data.get('token_number')
    if not token:
        return error_response("token_number is required.", error_code="VALIDATION_ERROR")

    center_id = g.center_id
    db = next(get_db())
    try:
        res = ProcurementService.verify_token(db, token_number=token, center_id=center_id)
        return success_response(data=res, message="Token verified.")
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except ValueError as ve:
        return error_response(str(ve), error_code="TOKEN_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@procurement_bp.route('/<int:booking_id>/record', methods=['POST'])
@jwt_required(allowed_roles=['center'])
def record_procurement(booking_id: int):
    data = request.get_json() or {}
    actual_weight = data.get('actual_weight_quintal')
    if actual_weight is None:
        return error_response("actual_weight_quintal is required.", error_code="VALIDATION_ERROR")

    center_id = g.center_id
    recorded_by = g.current_user.get('center_name', 'Center Staff')
    db = next(get_db())
    try:
        record = ProcurementService.complete_procurement(
            db,
            booking_id=booking_id,
            actual_weight_quintal=float(actual_weight),
            center_id=center_id,
            recorded_by=recorded_by
        )
        return success_response(
            data=record.to_dict(),
            message="Procurement completed and payment calculated successfully.",
            status_code=201
        )
    except PermissionError as pe:
        return error_response(str(pe), error_code="FORBIDDEN", status_code=403)
    except ValueError as ve:
        return error_response(str(ve), error_code="PROCUREMENT_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

@procurement_bp.route('/<int:record_id>', methods=['GET'])
@jwt_required()
def get_record(record_id: int):
    db = next(get_db())
    record = ProcurementService.get_procurement_record(db, record_id)
    if not record:
        return error_response(f"Procurement record #{record_id} not found.", error_code="NOT_FOUND", status_code=404)

    # Scoping check
    if g.role == 'farmer' and record.farmer_id != g.farmer_id:
        return error_response("Access denied: Not your procurement record.", error_code="FORBIDDEN", status_code=403)
    if g.role == 'center' and record.center_id != g.center_id:
        return error_response("Access denied: Not your center's record.", error_code="FORBIDDEN", status_code=403)

    return success_response(data=record.to_dict(), message="Procurement record retrieved.")

@procurement_bp.route('/payment/<int:payment_id>/status', methods=['PUT'])
@jwt_required(allowed_roles=['center', 'admin'])
def update_payment_status(payment_id: int):
    data = request.get_json() or {}
    new_status = data.get('status')
    if not new_status:
        return error_response("status is required (PENDING, PROCESSED, PAID, FAILED).", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        payment = ProcurementService.update_payment_status(
            db,
            payment_id=payment_id,
            new_status=new_status,
            transaction_ref=data.get('transaction_ref'),
            mode=data.get('mode')
        )
        return success_response(data=payment.to_dict(), message="Payment status updated.")
    except ValueError as ve:
        return error_response(str(ve), error_code="PAYMENT_ERROR", status_code=400)
    except Exception as e:
        return error_response(f"Internal error: {str(e)}", error_code="SERVER_ERROR", status_code=500)

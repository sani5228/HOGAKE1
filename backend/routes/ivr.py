from flask import Blueprint, request
from backend.database import get_db
from backend.services.ivr_service import IvrService
from backend.utils.responses import success_response, error_response

ivr_bp = Blueprint('ivr', __name__, url_prefix='/api/ivr')

@ivr_bp.route('/session/start', methods=['POST'])
def start_ivr_session():
    data = request.get_json() or {}
    mobile = data.get('caller_mobile')
    if not mobile:
        return error_response("caller_mobile is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = IvrService.start_session(db, caller_mobile=mobile)
        return success_response(data=res, message="IVR session initiated.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_ERROR")

@ivr_bp.route('/session/<string:session_id>/select-language', methods=['POST'])
def select_language(session_id: str):
    data = request.get_json() or {}
    digit = str(data.get('digit', '2')).strip()
    db = next(get_db())
    try:
        res = IvrService.select_language(db, session_id=session_id, language_digit=digit)
        return success_response(data=res, message="Language selected.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_ERROR")

@ivr_bp.route('/session/<string:session_id>/select-crop', methods=['POST'])
def select_crop(session_id: str):
    data = request.get_json() or {}
    crop_digit = data.get('digit')
    if crop_digit is None:
        return error_response("digit is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = IvrService.select_crop(db, session_id=session_id, crop_index=int(crop_digit))
        return success_response(data=res, message="Crop selected.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_ERROR")

@ivr_bp.route('/session/<string:session_id>/enter-quantity', methods=['POST'])
def enter_quantity(session_id: str):
    data = request.get_json() or {}
    quantity = data.get('quantity')
    if quantity is None:
        return error_response("quantity is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = IvrService.enter_quantity(db, session_id=session_id, quantity_quintals=float(quantity))
        return success_response(data=res, message="Quantity entered.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_ERROR")

@ivr_bp.route('/session/<string:session_id>/confirm-booking', methods=['POST'])
def confirm_booking(session_id: str):
    db = next(get_db())
    try:
        res = IvrService.confirm_booking(db, session_id=session_id)
        return success_response(data=res, message="IVR booking finalized and slot confirmed.", status_code=201)
    except Exception as e:
        return error_response(str(e), error_code="IVR_BOOKING_ERROR")

@ivr_bp.route('/session/<string:session_id>/cancel', methods=['POST'])
def cancel_booking(session_id: str):
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    if not booking_id:
        return error_response("booking_id is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = IvrService.cancel_via_ivr(db, session_id=session_id, booking_id=int(booking_id))
        return success_response(data=res, message="Booking cancelled via IVR.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_CANCEL_ERROR")

@ivr_bp.route('/session/<string:session_id>/rebook', methods=['POST'])
def rebook(session_id: str):
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    if not booking_id:
        return error_response("booking_id is required.", error_code="VALIDATION_ERROR")

    db = next(get_db())
    try:
        res = IvrService.rebook_via_ivr(db, session_id=session_id, booking_id=int(booking_id))
        return success_response(data=res, message="Booking rebooked via IVR.")
    except Exception as e:
        return error_response(str(e), error_code="IVR_REBOOK_ERROR")

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.notification import IvrSession
from backend.models.user import Farmer
from backend.models.crop import Crop
from backend.services.booking_service import BookingService
from backend.services.crop_service import CropService

class IvrService:
    @classmethod
    def start_session(cls, db: Session, caller_mobile: str) -> Dict[str, Any]:
        clean_mobile = str(caller_mobile).strip().replace('+91', '').replace(' ', '')
        farmer = db.query(Farmer).filter(Farmer.mobile_number == clean_mobile).first()

        session_id = str(uuid.uuid4())
        session = IvrSession(
            session_id=session_id,
            caller_mobile=clean_mobile,
            farmer_id=farmer.farmer_id if farmer else None,
            step='START',
            created_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()

        if not farmer:
            return {
                "session_id": session_id,
                "is_registered": False,
                "prompt": "Welcome to FASAL Kisan IVR line. Your mobile number is not registered. Please register online at our portal to use slot booking.",
                "menu_options": ["0: Repeat this message", "9: Speak to representative"]
            }

        return {
            "session_id": session_id,
            "is_registered": True,
            "farmer_name": farmer.name,
            "farmer_id": farmer.farmer_id,
            "prompt": f"Namaste {farmer.name}! Welcome to FASAL Agricultural Procurement Slot Booking. Press 1 for Hindi, Press 2 for English.",
            "next_step": "select-language"
        }

    @classmethod
    def select_language(cls, db: Session, session_id: str, language_digit: str) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session:
            raise ValueError("Invalid or expired IVR session.")

        lang = 'hi' if language_digit == '1' else 'en'
        session.language = lang
        session.step = 'LANGUAGE_SELECTED'
        db.commit()

        # Fetch in-season crops for this farmer
        eligible_crops = CropService.get_eligible_crops_for_farmer(db, session.farmer_id)
        crop_menu = []
        for idx, c in enumerate(eligible_crops, start=1):
            crop_menu.append(f"Press {idx} for {c.name}")

        prompt = (
            f"Please select your crop for procurement:\n" + "\n".join(crop_menu)
            if lang == 'en' else
            f"कृपया खरीद के लिए अपनी फसल चुनें:\n" + "\n".join(crop_menu)
        )

        return {
            "session_id": session_id,
            "language": lang,
            "prompt": prompt,
            "crops": [c.to_dict() for c in eligible_crops],
            "next_step": "select-crop"
        }

    @classmethod
    def select_crop(cls, db: Session, session_id: str, crop_index: int) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session:
            raise ValueError("Invalid IVR session.")

        eligible_crops = CropService.get_eligible_crops_for_farmer(db, session.farmer_id)
        if crop_index < 1 or crop_index > len(eligible_crops):
            raise ValueError(f"Invalid crop selection digit '{crop_index}'.")

        selected_crop = eligible_crops[crop_index - 1]
        session.selected_crop_id = selected_crop.crop_id
        session.step = 'CROP_SELECTED'
        db.commit()

        prompt = (
            f"You selected {selected_crop.name}. Please enter the expected quantity in quintals followed by hash (#)."
            if session.language == 'en' else
            f"आपने {selected_crop.name} चुना है। कृपया क्विंटल में मात्रा दर्ज करें और हैश (#) दबाएं।"
        )

        return {
            "session_id": session_id,
            "crop": selected_crop.to_dict(),
            "prompt": prompt,
            "next_step": "enter-quantity"
        }

    @classmethod
    def enter_quantity(cls, db: Session, session_id: str, quantity_quintals: float) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session:
            raise ValueError("Invalid IVR session.")

        qty = float(quantity_quintals)
        if qty <= 0:
            raise ValueError("Quantity must be a positive number in quintals.")

        session.entered_quantity = qty
        session.step = 'QUANTITY_ENTERED'
        db.commit()

        crop = db.query(Crop).filter(Crop.crop_id == session.selected_crop_id).first()
        crop_name = crop.name if crop else "Produce"

        prompt = (
            f"You entered {qty} quintals of {crop_name}. Press 1 to confirm booking, Press 2 to cancel."
            if session.language == 'en' else
            f"आपने {crop_name} के {qty} क्विंटल दर्ज किए हैं। पुष्टि के लिए 1 दबाएं, रद्द करने के लिए 2 दबाएं।"
        )

        return {
            "session_id": session_id,
            "quantity": qty,
            "prompt": prompt,
            "next_step": "confirm-booking"
        }

    @classmethod
    def confirm_booking(cls, db: Session, session_id: str) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session:
            raise ValueError("Invalid IVR session.")

        if not session.farmer_id or not session.selected_crop_id or not session.entered_quantity:
            raise ValueError("Incomplete IVR booking details.")

        # Calls the SAME shared BookingService as web (rules.md §16)
        booking = BookingService.create_booking(
            db=db,
            farmer_id=session.farmer_id,
            crop_id=session.selected_crop_id,
            expected_quantity_quintal=float(session.entered_quantity),
            channel='IVR'
        )

        session.booking_id = booking.booking_id
        session.step = 'CONFIRMED'
        db.commit()

        prompt = (
            f"Your booking is confirmed! Your token number is {booking.token_number}. "
            f"Your slot is at {booking.center.name} on {booking.assigned_date.strftime('%d-%m-%Y')} during {booking.shift}. "
            f"Confirmation SMS has been sent to your phone."
        )

        return {
            "session_id": session_id,
            "booking": booking.to_dict(),
            "prompt": prompt,
            "status": "CONFIRMED"
        }

    @classmethod
    def cancel_via_ivr(cls, db: Session, session_id: str, booking_id: int) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session or not session.farmer_id:
            raise ValueError("Invalid IVR session.")

        booking = BookingService.cancel_booking(db, booking_id, actor_role='FARMER', actor_id=session.farmer_id)
        session.step = 'CANCELLED'
        db.commit()

        return {
            "session_id": session_id,
            "message": f"Booking with token {booking.token_number} has been cancelled successfully via IVR."
        }

    @classmethod
    def rebook_via_ivr(cls, db: Session, session_id: str, booking_id: int) -> Dict[str, Any]:
        session = db.query(IvrSession).filter(IvrSession.session_id == session_id).first()
        if not session or not session.farmer_id:
            raise ValueError("Invalid IVR session.")

        new_booking = BookingService.rebook_booking(db, booking_id, actor_id=session.farmer_id, channel='IVR')
        return {
            "session_id": session_id,
            "new_booking": new_booking.to_dict(),
            "message": f"Slot successfully rebooked via IVR! New Token: {new_booking.token_number}."
        }

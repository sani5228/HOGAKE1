import sys
from datetime import datetime, timezone
from backend.database import SessionLocal
from backend.models.notification import Notification

class NotificationService:
    @staticmethod
    def send_sms(to_mobile: str, message: str, notification_type: str = "GENERAL",
                 farmer_id: str = None, center_id: str = None, booking_id: int = None) -> dict:
        """
        Authoritative prototype SMS simulation:
        Prints realistic SMS banner to backend terminal stdout, and persists an audit record.
        Does NOT use external providers (Twilio etc.).
        """
        # Format terminal SMS banner
        border = "=" * 52
        print(f"\n{border}", file=sys.stdout)
        print("SMS SIMULATION", file=sys.stdout)
        print(f"To: {to_mobile}", file=sys.stdout)
        print(f"Event: {notification_type}", file=sys.stdout)
        print("-" * 52, file=sys.stdout)
        print(message.strip(), file=sys.stdout)
        print(f"{border}\n", file=sys.stdout)
        sys.stdout.flush()

        # Record in database for audit and history using isolated engine connection
        try:
            from backend.database import engine
            from sqlalchemy import text
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO notifications (farmer_id, center_id, booking_id, type, message, channel, status, sent_at)
                        VALUES (:farmer_id, :center_id, :booking_id, :type, :message, :channel, :status, :sent_at)
                    """),
                    {
                        "farmer_id": farmer_id,
                        "center_id": center_id,
                        "booking_id": booking_id,
                        "type": notification_type,
                        "message": message.strip(),
                        "channel": 'SMS',
                        "status": 'SENT',
                        "sent_at": datetime.now(timezone.utc)
                    }
                )
            return {"sent": True, "channel": "SMS_SIMULATION", "to": to_mobile, "status": "SENT"}
        except Exception as e:
            print(f"[NotificationService Warning] Could not save notification to DB: {e}", file=sys.stderr)
            return {"sent": True, "channel": "SMS_SIMULATION", "to": to_mobile, "status": "TERMINAL_ONLY"}

    @classmethod
    def send_otp(cls, mobile_number: str, otp: str, purpose: str = "LOGIN") -> dict:
        message = (
            f"Your FASAL one-time password (OTP) is: {otp}\n"
            f"Purpose: {purpose}. Valid for 5 minutes.\n"
            f"Do not share this OTP with anyone."
        )
        return cls.send_sms(to_mobile=mobile_number, message=message, notification_type=f"OTP_{purpose}")

    @classmethod
    def send_registration_confirmation(cls, farmer_id: str, name: str, mobile_number: str) -> dict:
        message = (
            f"Welcome to FASAL, {name}!\n"
            f"Your registration is confirmed.\n"
            f"Farmer ID: {farmer_id}\n"
            f"You can now book procurement slots online or via IVR."
        )
        return cls.send_sms(to_mobile=mobile_number, message=message, notification_type="REGISTRATION_SUCCESS", farmer_id=farmer_id)

    @classmethod
    def send_booking_confirmation(cls, booking) -> dict:
        farmer_mobile = booking.farmer.mobile_number if booking.farmer else "Unknown"
        crop_name = booking.crop.name if booking.crop else "Produce"
        center_name = booking.center.name if booking.center else "Assigned Center"
        message = (
            f"Booking Confirmed!\n"
            f"Token: {booking.token_number}\n"
            f"Crop: {crop_name}\n"
            f"Quantity: {float(booking.expected_quantity_quintal)} Quintals\n"
            f"Procurement Center: {center_name}\n"
            f"Date: {booking.assigned_date.strftime('%d-%m-%Y')}\n"
            f"Shift: {booking.shift} ({booking.start_time} - {booking.end_time})\n"
            f"Est. Unloading Time: {booking.estimated_time_minutes} minutes"
        )
        return cls.send_sms(
            to_mobile=farmer_mobile,
            message=message,
            notification_type="BOOKING_CONFIRMATION",
            farmer_id=booking.farmer_id,
            center_id=booking.center_id,
            booking_id=booking.booking_id
        )

    @classmethod
    def send_cancellation(cls, booking) -> dict:
        farmer_mobile = booking.farmer.mobile_number if booking.farmer else "Unknown"
        message = (
            f"Your booking has been cancelled.\n"
            f"Token: {booking.token_number}\n"
            f"Date: {booking.assigned_date.strftime('%d-%m-%Y')}\n"
            f"Committed capacity has been released. You may rebook anytime."
        )
        return cls.send_sms(
            to_mobile=farmer_mobile,
            message=message,
            notification_type="BOOKING_CANCELLED",
            farmer_id=booking.farmer_id,
            center_id=booking.center_id,
            booking_id=booking.booking_id
        )

    @classmethod
    def send_procurement_completion(cls, record) -> dict:
        farmer_mobile = record.farmer.mobile_number if record.farmer else "Unknown"
        crop_name = record.crop.name if record.crop else "Produce"
        message = (
            f"Procurement Completed successfully!\n"
            f"Booking Token: {record.booking.token_number if record.booking else 'N/A'}\n"
            f"Crop: {crop_name}\n"
            f"Actual Weight: {float(record.actual_weight_quintal)} Quintals\n"
            f"Rate: Rs {float(record.rate_per_quintal)}/Quintal\n"
            f"Total Payable Amount: Rs {float(record.total_amount):,.2f}\n"
            f"Payment Status: PENDING (Direct Benefit Transfer in progress)"
        )
        return cls.send_sms(
            to_mobile=farmer_mobile,
            message=message,
            notification_type="PROCUREMENT_COMPLETED",
            farmer_id=record.farmer_id,
            center_id=record.center_id,
            booking_id=record.booking_id
        )

    @classmethod
    def send_payment_update(cls, payment, farmer_mobile: str, token_number: str = None) -> dict:
        message = (
            f"Payment Status Update:\n"
            f"Amount: Rs {float(payment.amount):,.2f}\n"
            f"Status: {payment.status}\n"
            f"Mode: {payment.mode}\n"
            f"Txn Ref: {payment.transaction_ref or 'DBT-PENDING'}\n"
            f"Thank you for using FASAL platform."
        )
        return cls.send_sms(to_mobile=farmer_mobile, message=message, notification_type="PAYMENT_STATUS")

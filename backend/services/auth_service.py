import random
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.user import User, Farmer, ProcurementCenter, AdminUser
from backend.models.notification import OtpVerification
from backend.utils.security import verify_password, create_jwt_token, hash_password
from backend.services.notification_service import NotificationService

class AuthService:
    @classmethod
    def send_otp(cls, db: Session, mobile_number: str, purpose: str = "LOGIN") -> Dict[str, Any]:
        clean_mobile = str(mobile_number).strip().replace('+91', '').replace(' ', '')
        if not (len(clean_mobile) == 10 and clean_mobile.isdigit()):
            raise ValueError("Mobile number must be a valid 10-digit numeric value.")

        # Check rate-limit cooldown: check if recent OTP was requested within 30 seconds
        from backend.config import Config
        if not Config.DEBUG:
            recent = (
                db.query(OtpVerification)
                .filter(OtpVerification.mobile_number == clean_mobile)
                .order_by(OtpVerification.created_at.desc())
                .first()
            )
            if recent and recent.created_at:
                elapsed = (datetime.now(timezone.utc) - recent.created_at.replace(tzinfo=timezone.utc)).total_seconds()
                if elapsed < 30:
                    raise ValueError(f"Please wait {int(30 - elapsed)} seconds before requesting another OTP.")

        # Generate 6-digit OTP
        #otp_val = f"{random.randint(100000, 999999)}"
        otp_val = "123456"
        otp_hash = hashlib.sha256(otp_val.encode('utf-8')).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        otp_record = OtpVerification(
            mobile_number=clean_mobile,
            otp_hash=otp_hash,
            otp_plain=otp_val,
            purpose=purpose.upper(),
            expires_at=expires_at,
            verified=False,
            attempts=0,
            created_at=datetime.now(timezone.utc)
        )
        db.add(otp_record)
        db.commit()

        # Send simulated SMS to terminal
        NotificationService.send_otp(clean_mobile, otp_val, purpose=purpose)

        # Check if farmer is already registered
        is_registered = db.query(Farmer).filter(Farmer.mobile_number == clean_mobile).first() is not None

        return {
            "mobile_number": clean_mobile,
            "purpose": purpose,
            "expires_in_seconds": 300,
            "is_registered": is_registered,
            # Convenient demo testing helper
            "demo_otp": otp_val,
            "message": "OTP generated and logged to backend terminal successfully."
        }

    @classmethod
    def verify_otp(cls, db: Session, mobile_number: str, otp_input: str) -> Dict[str, Any]:
        clean_mobile = str(mobile_number).strip().replace('+91', '').replace(' ', '')
        clean_otp = str(otp_input).strip()

        if not (len(clean_otp) == 6 and clean_otp.isdigit()):
            raise ValueError("OTP must be a 6-digit number.")

        # Find latest unexpired record
        now = datetime.now(timezone.utc)
        record = (
            db.query(OtpVerification)
            .filter(
                OtpVerification.mobile_number == clean_mobile,
                OtpVerification.verified == False
            )
            .order_by(OtpVerification.created_at.desc())
            .first()
        )

        if not record:
            raise ValueError("No pending OTP request found for this mobile number. Please request a new OTP.")

        if record.expires_at.replace(tzinfo=timezone.utc) < now:
            raise ValueError("OTP has expired. Please request a new OTP.")

        if record.attempts >= 3:
            raise ValueError("Maximum verification attempts (3) exceeded. Please request a new OTP.")

        record.attempts += 1

        input_hash = hashlib.sha256(clean_otp.encode('utf-8')).hexdigest()
        # In demo mode, also allow matching plain OTP or demo bypass
        if input_hash != record.otp_hash and clean_otp != record.otp_plain:
            db.commit()
            remaining = 3 - record.attempts
            raise ValueError(f"Invalid OTP. {remaining} attempt(s) remaining.")

        record.verified = True
        db.commit()

        # Check if farmer exists
        farmer = db.query(Farmer).filter(Farmer.mobile_number == clean_mobile).first()
        if farmer:
            token = create_jwt_token({
                "user_id": farmer.user_id,
                "role": "farmer",
                "farmer_id": farmer.farmer_id,
                "name": farmer.name,
                "mobile": clean_mobile
            })
            return {
                "verified": True,
                "is_registered": True,
                "token": token,
                "role": "farmer",
                "farmer": farmer.to_dict(mask_aadhaar=True)
            }
        else:
            # Verified but not yet registered
            temp_token = create_jwt_token({
                "role": "guest",
                "mobile": clean_mobile,
                "verified_otp": True
            })
            return {
                "verified": True,
                "is_registered": False,
                "temp_token": temp_token,
                "mobile_number": clean_mobile,
                "message": "OTP verified successfully. Please complete farmer registration."
            }

    @classmethod
    def login_center(cls, db: Session, username: str, password: str) -> Dict[str, Any]:
        clean_user = username.strip()
        user = db.query(User).filter(User.mobile_number == clean_user, User.role == 'center').first()
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid center username or password.")

        center = user.center_profile
        if not center:
            raise ValueError("Center profile not associated with this account.")

        token = create_jwt_token({
            "user_id": user.user_id,
            "role": "center",
            "center_id": center.center_id,
            "center_name": center.name
        })

        return {
            "token": token,
            "role": "center",
            "center": center.to_dict()
        }

    @classmethod
    def login_admin(cls, db: Session, username: str, password: str) -> Dict[str, Any]:
        clean_user = username.strip()
        admin = db.query(AdminUser).filter(AdminUser.username == clean_user).first()
        if not admin or not verify_password(password, admin.password_hash):
            raise ValueError("Invalid administrator credentials.")

        token = create_jwt_token({
            "role": "admin",
            "admin_id": admin.admin_id,
            "username": admin.username
        })

        return {
            "token": token,
            "role": "admin",
            "admin": admin.to_dict()
        }

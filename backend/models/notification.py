from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Numeric
from backend.database import Base

class Notification(Base):
    __tablename__ = 'notifications'

    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String(20), nullable=True, index=True)
    center_id = Column(String(20), nullable=True, index=True)
    booking_id = Column(Integer, nullable=True, index=True)
    type = Column(String(50), nullable=False)  # e.g. OTP, BOOKING_CONFIRMATION, ARRIVAL, PROCUREMENT_COMPLETED, PAYMENT_UPDATE, CANCELLATION
    message = Column(Text, nullable=False)
    channel = Column(String(10), default='SMS', nullable=False)
    status = Column(String(20), default='SENT', nullable=False)  # 'QUEUED', 'SENT', 'FAILED'
    sent_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "farmer_id": self.farmer_id,
            "center_id": self.center_id,
            "booking_id": self.booking_id,
            "type": self.type,
            "message": self.message,
            "channel": self.channel,
            "status": self.status,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }

class OtpVerification(Base):
    __tablename__ = 'otp_verifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    mobile_number = Column(String(15), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)
    otp_plain = Column(String(10), nullable=True)  # For simulation/demo visibility in terminal/API
    purpose = Column(String(30), default='LOGIN', nullable=False)  # 'LOGIN', 'REGISTRATION'
    expires_at = Column(DateTime, nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class IvrSession(Base):
    __tablename__ = 'ivr_sessions'

    session_id = Column(String(50), primary_key=True)  # UUID
    caller_mobile = Column(String(15), nullable=False, index=True)
    language = Column(String(10), default='en', nullable=False)
    farmer_id = Column(String(20), nullable=True)
    selected_crop_id = Column(Integer, nullable=True)
    entered_quantity = Column(Numeric(10, 2), nullable=True)
    booking_id = Column(Integer, nullable=True)
    step = Column(String(30), default='START', nullable=False)
    # Steps: 'START', 'LANGUAGE_SELECTED', 'CROP_SELECTED', 'QUANTITY_ENTERED', 'CONFIRMED', 'CANCELLED'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "caller_mobile": self.caller_mobile,
            "language": self.language,
            "farmer_id": self.farmer_id,
            "selected_crop_id": self.selected_crop_id,
            "entered_quantity": float(self.entered_quantity) if self.entered_quantity is not None else None,
            "booking_id": self.booking_id,
            "step": self.step,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AuditLog(Base):
    __tablename__ = 'audit_log'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    actor_type = Column(String(20), nullable=False)  # 'FARMER', 'CENTER', 'ADMIN', 'SYSTEM'
    actor_id = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details_json": self.details_json,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

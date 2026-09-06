from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base

class ProcurementRecord(Base):
    __tablename__ = 'procurement_records'

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey('bookings.booking_id'), unique=True, nullable=False, index=True)
    farmer_id = Column(String(20), ForeignKey('farmers.farmer_id'), nullable=False, index=True)
    center_id = Column(String(20), ForeignKey('procurement_centers.center_id'), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey('crops.crop_id'), nullable=False)
    actual_weight_quintal = Column(Numeric(10, 2), nullable=False)
    rate_per_quintal = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)  # actual_weight * rate_per_quintal
    actual_procurement_time_minutes = Column(Integer, nullable=True)
    procurement_date = Column(Date, default=date.today, nullable=False)
    recorded_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    booking = relationship("Booking", back_populates="procurement_record")
    farmer = relationship("Farmer", back_populates="procurement_records")
    center = relationship("ProcurementCenter", back_populates="procurement_records")
    crop = relationship("Crop")
    payment = relationship("Payment", back_populates="procurement_record", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        payment_dict = self.payment.to_dict() if self.payment else None
        return {
            "record_id": self.record_id,
            "booking_id": self.booking_id,
            "token_number": self.booking.token_number if self.booking else None,
            "farmer_id": self.farmer_id,
            "farmer_name": self.farmer.name if self.farmer else None,
            "center_id": self.center_id,
            "center_name": self.center.name if self.center else None,
            "crop_id": self.crop_id,
            "crop_name": self.crop.name if self.crop else None,
            "actual_weight_quintal": float(self.actual_weight_quintal) if self.actual_weight_quintal is not None else 0.0,
            "rate_per_quintal": float(self.rate_per_quintal) if self.rate_per_quintal is not None else 0.0,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0.0,
            "procurement_date": self.procurement_date.isoformat() if self.procurement_date else None,
            "recorded_by": self.recorded_by,
            "payment_id": payment_dict["payment_id"] if payment_dict else None,
            "payment_status": payment_dict["status"] if payment_dict else 'PENDING',
            "payment": payment_dict,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    procurement_record_id = Column(Integer, ForeignKey('procurement_records.record_id', ondelete="CASCADE"), unique=True, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(20), default='PENDING', nullable=False)  # 'PENDING', 'PROCESSED', 'PAID', 'FAILED'
    payment_date = Column(DateTime, nullable=True)
    mode = Column(String(50), default='Direct Benefit Transfer (DBT)')
    transaction_ref = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    procurement_record = relationship("ProcurementRecord", back_populates="payment")

    def to_dict(self):
        return {
            "payment_id": self.payment_id,
            "procurement_record_id": self.procurement_record_id,
            "amount": float(self.amount) if self.amount is not None else 0.0,
            "status": self.status,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "mode": self.mode,
            "transaction_ref": self.transaction_ref,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

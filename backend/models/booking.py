from datetime import datetime, timezone, date
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base

class Booking(Base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    token_number = Column(String(50), unique=True, nullable=False, index=True)
    farmer_id = Column(String(20), ForeignKey('farmers.farmer_id'), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey('crops.crop_id'), nullable=False)
    center_id = Column(String(20), ForeignKey('procurement_centers.center_id'), nullable=False, index=True)
    expected_quantity_quintal = Column(Numeric(10, 2), nullable=False)
    estimated_time_minutes = Column(Integer, nullable=False)
    booking_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    assigned_date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=False)  # 'SHIFT_1', 'SHIFT_2'
    start_time = Column(String(10), nullable=True)  # e.g. "09:00"
    end_time = Column(String(10), nullable=True)    # e.g. "10:15"
    status = Column(String(30), default='SCHEDULED', nullable=False, index=True)
    # Statuses: 'BOOKED', 'SCHEDULED', 'ARRIVED', 'PROCUREMENT', 'COMPLETED', 'CANCELLED', 'RESCHEDULED'
    channel = Column(String(10), default='WEB', nullable=False)  # 'WEB', 'IVR'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    farmer = relationship("Farmer", back_populates="bookings")
    crop = relationship("Crop", back_populates="bookings")
    center = relationship("ProcurementCenter", back_populates="bookings")
    procurement_record = relationship("ProcurementRecord", back_populates="booking", uselist=False)

    def to_dict(self):
        return {
            "booking_id": self.booking_id,
            "token_number": self.token_number,
            "farmer_id": self.farmer_id,
            "farmer_name": self.farmer.name if self.farmer else None,
            "farmer_mobile": self.farmer.mobile_number if self.farmer else None,
            "crop_id": self.crop_id,
            "crop_name": self.crop.name if self.crop else None,
            "center_id": self.center_id,
            "center_name": self.center.name if self.center else None,
            "expected_quantity_quintal": float(self.expected_quantity_quintal) if self.expected_quantity_quintal is not None else 0.0,
            "rate_per_quintal": float(self.crop.rate_per_quintal) if self.crop and self.crop.rate_per_quintal else 0.0,
            "estimated_time_minutes": self.estimated_time_minutes,
            "booking_timestamp": self.booking_timestamp.isoformat() if self.booking_timestamp else None,
            "assigned_date": self.assigned_date.isoformat() if self.assigned_date else None,
            "shift": self.shift,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "channel": self.channel,
            "booking_method": self.channel,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class CenterDailySchedule(Base):
    __tablename__ = 'center_daily_schedule'

    id = Column(Integer, primary_key=True, autoincrement=True)
    center_id = Column(String(20), ForeignKey('procurement_centers.center_id', ondelete="CASCADE"), nullable=False)
    schedule_date = Column(Date, nullable=False, index=True)
    shift = Column(String(20), nullable=False)  # 'SHIFT_1', 'SHIFT_2'
    committed_minutes = Column(Integer, default=0, nullable=False)
    capacity_minutes = Column(Integer, default=210, nullable=False)  # 210 min per shift = 420 min / day

    center = relationship("ProcurementCenter", back_populates="daily_schedules")

    __table_args__ = (
        UniqueConstraint('center_id', 'schedule_date', 'shift', name='uq_center_date_shift'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "center_id": self.center_id,
            "schedule_date": self.schedule_date.isoformat() if self.schedule_date else None,
            "shift": self.shift,
            "committed_minutes": self.committed_minutes,
            "capacity_minutes": self.capacity_minutes,
            "remaining_minutes": max(0, self.capacity_minutes - self.committed_minutes)
        }

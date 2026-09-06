from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    mobile_number = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False)  # 'farmer', 'center', 'admin'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    farmer_profile = relationship("Farmer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    center_profile = relationship("ProcurementCenter", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "mobile_number": self.mobile_number,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Farmer(Base):
    __tablename__ = 'farmers'

    farmer_id = Column(String(20), primary_key=True)  # Format: FA000125
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    mobile_number = Column(String(15), unique=True, nullable=False, index=True)
    aadhaar_encrypted = Column(String(255), nullable=False)
    aadhaar_last4 = Column(String(4), nullable=False)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    village_town = Column(String(100), nullable=False)
    status = Column(String(20), default='ACTIVE')  # 'ACTIVE', 'SUSPENDED'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="farmer_profile")
    farmer_crops = relationship("FarmerCrop", back_populates="farmer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="farmer")
    procurement_records = relationship("ProcurementRecord", back_populates="farmer")

    def to_dict(self, mask_aadhaar=True):
        return {
            "farmer_id": self.farmer_id,
            "user_id": self.user_id,
            "name": self.name,
            "mobile_number": self.mobile_number,
            "aadhaar_last4": self.aadhaar_last4 if mask_aadhaar else self.aadhaar_encrypted,
            "state": self.state,
            "district": self.district,
            "village_town": self.village_town,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ProcurementCenter(Base):
    __tablename__ = 'procurement_centers'

    center_id = Column(String(20), primary_key=True)  # Format: PC000045
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    contact_number = Column(String(15), nullable=False)
    authorized_person_aadhaar_encrypted = Column(String(255), nullable=True)
    state = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    village_town = Column(String(100), nullable=False)
    daily_capacity_minutes = Column(Integer, default=420)  # 7 hours planning limit
    shift1_capacity_minutes = Column(Integer, default=210)
    shift2_capacity_minutes = Column(Integer, default=210)
    status = Column(String(30), default='PENDING_VERIFICATION')  # 'PENDING_VERIFICATION', 'ACTIVE', 'SUSPENDED'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="center_profile")
    center_crops = relationship("CenterCrop", back_populates="center", cascade="all, delete-orphan")
    documents = relationship("CenterDocument", back_populates="center", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="center")
    daily_schedules = relationship("CenterDailySchedule", back_populates="center", cascade="all, delete-orphan")
    procurement_records = relationship("ProcurementRecord", back_populates="center")

    def to_dict(self):
        return {
            "center_id": self.center_id,
            "user_id": self.user_id,
            "name": self.name,
            "contact_number": self.contact_number,
            "state": self.state,
            "district": self.district,
            "village_town": self.village_town,
            "daily_capacity_minutes": self.daily_capacity_minutes,
            "shift1_capacity_minutes": self.shift1_capacity_minutes,
            "shift2_capacity_minutes": self.shift2_capacity_minutes,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AdminUser(Base):
    __tablename__ = 'admin_users'

    admin_id = Column(String(20), primary_key=True)  # Format: AD001
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

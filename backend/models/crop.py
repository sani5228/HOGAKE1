from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.database import Base

class Crop(Base):
    __tablename__ = 'crops'

    crop_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)  # e.g. Cereals, Pulses, Commercial, Millets, Oilseeds
    rate_per_quintal = Column(Numeric(10, 2), nullable=False)  # ₹ per Quintal
    time_to_unload_per_quintal_minutes = Column(Integer, default=5, nullable=False)  # Unload/processing time
    season = Column(String(30), nullable=False)  # 'Kharif', 'Rabi', 'Zaid', 'All'
    status = Column(String(20), default='ACTIVE')  # 'ACTIVE', 'INACTIVE'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    farmer_crops = relationship("FarmerCrop", back_populates="crop", cascade="all, delete-orphan")
    center_crops = relationship("CenterCrop", back_populates="crop", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="crop")

    def to_dict(self):
        return {
            "crop_id": self.crop_id,
            "name": self.name,
            "category": self.category,
            "rate_per_quintal": float(self.rate_per_quintal) if self.rate_per_quintal is not None else 0.0,
            "time_to_unload_per_quintal_minutes": self.time_to_unload_per_quintal_minutes,
            "season": self.season,
            "status": self.status
        }

class FarmerCrop(Base):
    __tablename__ = 'farmer_crops'

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(String(20), ForeignKey('farmers.farmer_id', ondelete="CASCADE"), nullable=False)
    crop_id = Column(Integer, ForeignKey('crops.crop_id', ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    farmer = relationship("Farmer", back_populates="farmer_crops")
    crop = relationship("Crop", back_populates="farmer_crops")

class CenterCrop(Base):
    __tablename__ = 'center_crops'

    id = Column(Integer, primary_key=True, autoincrement=True)
    center_id = Column(String(20), ForeignKey('procurement_centers.center_id', ondelete="CASCADE"), nullable=False)
    crop_id = Column(Integer, ForeignKey('crops.crop_id', ondelete="CASCADE"), nullable=False)

    center = relationship("ProcurementCenter", back_populates="center_crops")
    crop = relationship("Crop", back_populates="center_crops")

class CenterDocument(Base):
    __tablename__ = 'center_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    center_id = Column(String(20), ForeignKey('procurement_centers.center_id', ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)  # License, ID proof, Center certificate
    file_reference = Column(String(255), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    center = relationship("ProcurementCenter", back_populates="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "center_id": self.center_id,
            "document_type": self.document_type,
            "file_reference": self.file_reference,
            "verified": self.verified
        }

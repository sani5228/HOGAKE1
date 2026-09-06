from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.user import User, Farmer
from backend.models.crop import Crop, FarmerCrop
from backend.models.booking import Booking
from backend.models.procurement import ProcurementRecord
from backend.utils.security import hash_aadhaar, mask_aadhaar, hash_password, create_jwt_token
from backend.services.notification_service import NotificationService

class FarmerService:
    @classmethod
    def register_farmer(cls, db: Session, data: dict) -> Dict[str, Any]:
        """
        Registers a new farmer.
        Enforces rules.md §3 (Farmer Registration Rules) & PRD.md §9.1.
        """
        name = data.get('name', '').strip()
        mobile = str(data.get('mobile_number', '')).strip().replace('+91', '').replace(' ', '')
        aadhaar = str(data.get('aadhaar', '')).strip().replace('-', '').replace(' ', '')
        state = data.get('state', '').strip()
        district = data.get('district', '').strip()
        village_town = data.get('village_town', '').strip()
        crop_ids = data.get('crop_ids', [])
        password = data.get('password', None)

        # Validation
        if len(name) < 2:
            raise ValueError("Farmer full name must be at least 2 characters.")
        if not (len(mobile) == 10 and mobile.isdigit()):
            raise ValueError("Mobile number must be a valid 10-digit number.")
        if not (len(aadhaar) == 12 and aadhaar.isdigit()):
            raise ValueError("Aadhaar must be a valid 12-digit number.")
        if not state or not district or not village_town:
            raise ValueError("State, District, and Village/Town are required location fields.")

        # Duplicate checks (FR-006)
        if db.query(User).filter(User.mobile_number == mobile).first():
            raise ValueError("Mobile number is already registered. Please login instead.")

        aadhaar_hash = hash_aadhaar(aadhaar)
        if db.query(Farmer).filter(Farmer.aadhaar_encrypted == aadhaar_hash).first():
            raise ValueError("A farmer with this Aadhaar number is already registered.")

        # Generate unique Farmer ID: FA###### (e.g. FA000101)
        count = db.query(Farmer).count()
        farmer_id = f"FA{count + 1:06d}"
        while db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first():
            count += 1
            farmer_id = f"FA{count + 1:06d}"

        # Create user record
        pw_hash = hash_password(password) if password else None
        user = User(
            mobile_number=mobile,
            password_hash=pw_hash,
            role='farmer',
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.flush()

        # Create farmer profile
        farmer = Farmer(
            farmer_id=farmer_id,
            user_id=user.user_id,
            name=name,
            mobile_number=mobile,
            aadhaar_encrypted=aadhaar_hash,
            aadhaar_last4=mask_aadhaar(aadhaar),
            state=state,
            district=district,
            village_town=village_town,
            status='ACTIVE',
            created_at=datetime.now(timezone.utc)
        )
        db.add(farmer)

        # Register crops
        valid_crops = db.query(Crop).filter(Crop.crop_id.in_(crop_ids)).all() if crop_ids else []
        for c in valid_crops:
            fc = FarmerCrop(farmer_id=farmer_id, crop_id=c.crop_id)
            db.add(fc)

        db.commit()
        db.refresh(farmer)

        # Send welcome notification
        NotificationService.send_registration_confirmation(farmer_id, name, mobile)

        # Generate JWT session token
        token = create_jwt_token({
            "user_id": user.user_id,
            "role": "farmer",
            "farmer_id": farmer_id,
            "name": name,
            "mobile": mobile
        })

        return {
            "token": token,
            "farmer": farmer.to_dict(mask_aadhaar=True),
            "registered_crops": [c.to_dict() for c in valid_crops]
        }

    @classmethod
    def get_profile(cls, db: Session, farmer_id: str) -> Optional[Dict[str, Any]]:
        farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            return None

        # Registered crops
        crops = (
            db.query(Crop)
            .join(FarmerCrop, Crop.crop_id == FarmerCrop.crop_id)
            .filter(FarmerCrop.farmer_id == farmer_id)
            .all()
        )

        res = farmer.to_dict(mask_aadhaar=True)
        res["crops"] = [c.to_dict() for c in crops]
        return res

    @classmethod
    def update_crops(cls, db: Session, farmer_id: str, crop_ids: List[int]) -> List[dict]:
        farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            raise ValueError(f"Farmer '{farmer_id}' not found.")

        # Clear existing
        db.query(FarmerCrop).filter(FarmerCrop.farmer_id == farmer_id).delete()

        valid_crops = db.query(Crop).filter(Crop.crop_id.in_(crop_ids), Crop.status == 'ACTIVE').all()
        for c in valid_crops:
            db.add(FarmerCrop(farmer_id=farmer_id, crop_id=c.crop_id))

        db.commit()
        return [c.to_dict() for c in valid_crops]

    @classmethod
    def get_procurement_history(cls, db: Session, farmer_id: str) -> List[dict]:
        records = (
            db.query(ProcurementRecord)
            .filter(ProcurementRecord.farmer_id == farmer_id)
            .order_by(ProcurementRecord.procurement_date.desc(), ProcurementRecord.created_at.desc())
            .all()
        )
        return [r.to_dict() for r in records]

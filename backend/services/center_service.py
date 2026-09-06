from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.user import User, ProcurementCenter
from backend.models.crop import Crop, CenterCrop, CenterDocument
from backend.models.booking import Booking, CenterDailySchedule
from backend.models.procurement import ProcurementRecord
from backend.utils.security import hash_password
from backend.config import Config

class CenterService:
    @classmethod
    def register_center(cls, db: Session, data: dict) -> Dict[str, Any]:
        """
        Registers a new procurement center (PRD.md §9.2, FR-010).
        Starts in PENDING_VERIFICATION status until Admin approval.
        """
        name = data.get('name', '').strip()
        contact_number = str(data.get('contact_number', '')).strip()
        state = data.get('state', '').strip()
        district = data.get('district', '').strip()
        village_town = data.get('village_town', '').strip()
        crop_ids = data.get('crop_ids', [])
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        daily_cap = int(data.get('daily_capacity_minutes', Config.DAILY_PLANNING_MINUTES))
        shift1_cap = int(data.get('shift1_capacity_minutes', daily_cap // 2))
        shift2_cap = int(data.get('shift2_capacity_minutes', daily_cap - shift1_cap))

        if len(name) < 3:
            raise ValueError("Center name must be at least 3 characters.")
        if not contact_number:
            raise ValueError("Contact number is required.")
        if not username or len(password) < 6:
            raise ValueError("Username and password (min 6 chars) are required for center login.")

        # Check duplicate username
        if db.query(User).filter(User.mobile_number == username).first():
            raise ValueError("Username or contact number is already registered.")

        # Generate unique Center ID: PC######
        count = db.query(ProcurementCenter).count()
        center_id = f"PC{count + 1:06d}"
        while db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first():
            count += 1
            center_id = f"PC{count + 1:06d}"

        # Create user record
        user = User(
            mobile_number=username,
            password_hash=hash_password(password),
            role='center',
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.flush()

        center = ProcurementCenter(
            center_id=center_id,
            user_id=user.user_id,
            name=name,
            contact_number=contact_number,
            state=state,
            district=district,
            village_town=village_town,
            daily_capacity_minutes=daily_cap,
            shift1_capacity_minutes=shift1_cap,
            shift2_capacity_minutes=shift2_cap,
            status='PENDING_VERIFICATION',
            created_at=datetime.now(timezone.utc)
        )
        db.add(center)

        # Connect crops
        valid_crops = db.query(Crop).filter(Crop.crop_id.in_(crop_ids)).all() if crop_ids else []
        for c in valid_crops:
            db.add(CenterCrop(center_id=center_id, crop_id=c.crop_id))

        # Sample document record if provided
        doc_ref = data.get('license_document', 'mandi_board_license.pdf')
        db.add(CenterDocument(
            center_id=center_id,
            document_type='Mandi Board License',
            file_reference=doc_ref,
            verified=False
        ))

        db.commit()
        db.refresh(center)

        return {
            "center": center.to_dict(),
            "accepted_crops": [c.to_dict() for c in valid_crops],
            "status": "PENDING_VERIFICATION",
            "message": "Center registered successfully. Awaiting administrator verification."
        }

    @classmethod
    def get_profile(cls, db: Session, center_id: str) -> Optional[Dict[str, Any]]:
        center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first()
        if not center:
            return None

        crops = (
            db.query(Crop)
            .join(CenterCrop, Crop.crop_id == CenterCrop.crop_id)
            .filter(CenterCrop.center_id == center_id)
            .all()
        )

        res = center.to_dict()
        res["accepted_crops"] = [c.to_dict() for c in crops]
        return res

    @classmethod
    def update_capacity(cls, db: Session, center_id: str, data: dict) -> Dict[str, Any]:
        center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first()
        if not center:
            raise ValueError(f"Center '{center_id}' not found.")

        if 'daily_capacity_minutes' in data:
            cap = int(data['daily_capacity_minutes'])
            center.daily_capacity_minutes = cap
            center.shift1_capacity_minutes = cap // 2
            center.shift2_capacity_minutes = cap - (cap // 2)

        if 'shift1_capacity_minutes' in data:
            center.shift1_capacity_minutes = int(data['shift1_capacity_minutes'])
        if 'shift2_capacity_minutes' in data:
            center.shift2_capacity_minutes = int(data['shift2_capacity_minutes'])

        db.commit()
        db.refresh(center)
        return center.to_dict()

    @classmethod
    def update_crops(cls, db: Session, center_id: str, crop_ids: List[int]) -> List[dict]:
        center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first()
        if not center:
            raise ValueError(f"Center '{center_id}' not found.")

        db.query(CenterCrop).filter(CenterCrop.center_id == center_id).delete()
        valid_crops = db.query(Crop).filter(Crop.crop_id.in_(crop_ids), Crop.status == 'ACTIVE').all()
        for c in valid_crops:
            db.add(CenterCrop(center_id=center_id, crop_id=c.crop_id))

        db.commit()
        return [c.to_dict() for c in valid_crops]

    @classmethod
    def get_schedule_and_capacity(cls, db: Session, center_id: str, sched_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Provides schedule and live capacity meter for the center dashboard (PRD §13.2, §16.10).
        Strictly scopes farmers/bookings to this center and masks sensitive data (Aadhaar).
        """
        center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first()
        if not center:
            raise ValueError(f"Center '{center_id}' not found.")

        target_date = sched_date or date.today()

        # Bookings for this date and center
        bookings = (
            db.query(Booking)
            .filter(
                Booking.center_id == center_id,
                Booking.assigned_date == target_date
            )
            .order_by(Booking.shift.asc(), Booking.start_time.asc())
            .all()
        )

        # Committed minutes by shift from ledger
        shift1_schedule = db.query(CenterDailySchedule).filter(
            CenterDailySchedule.center_id == center_id,
            CenterDailySchedule.schedule_date == target_date,
            CenterDailySchedule.shift == 'SHIFT_1'
        ).first()

        shift2_schedule = db.query(CenterDailySchedule).filter(
            CenterDailySchedule.center_id == center_id,
            CenterDailySchedule.schedule_date == target_date,
            CenterDailySchedule.shift == 'SHIFT_2'
        ).first()

        s1_committed = shift1_schedule.committed_minutes if shift1_schedule else sum(
            b.estimated_time_minutes for b in bookings if b.shift == 'SHIFT_1' and b.status != 'CANCELLED'
        )
        s2_committed = shift2_schedule.committed_minutes if shift2_schedule else sum(
            b.estimated_time_minutes for b in bookings if b.shift == 'SHIFT_2' and b.status != 'CANCELLED'
        )
        total_committed = s1_committed + s2_committed

        # Mask Aadhaar and format response
        safe_bookings = []
        for b in bookings:
            b_dict = b.to_dict()
            safe_bookings.append(b_dict)

        return {
            "center_id": center_id,
            "center_name": center.name,
            "date": target_date.isoformat(),
            "daily_capacity_minutes": center.daily_capacity_minutes,
            "total_committed_minutes": total_committed,
            "total_remaining_minutes": max(0, center.daily_capacity_minutes - total_committed),
            "hard_ceiling_minutes": Config.HARD_CEILING_MINUTES,
            "available_operational_bandwidth_minutes": max(0, Config.HARD_CEILING_MINUTES - total_committed),
            "shift_1": {
                "capacity": center.shift1_capacity_minutes,
                "committed": s1_committed,
                "remaining": max(0, center.shift1_capacity_minutes - s1_committed)
            },
            "shift_2": {
                "capacity": center.shift2_capacity_minutes,
                "committed": s2_committed,
                "remaining": max(0, center.shift2_capacity_minutes - s2_committed)
            },
            "bookings": safe_bookings
        }

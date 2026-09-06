import json
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.user import Farmer, ProcurementCenter
from backend.models.crop import Crop, FarmerCrop
from backend.models.booking import Booking
from backend.models.notification import AuditLog
from backend.services.scheduling_service import SchedulingService
from backend.services.notification_service import NotificationService
from backend.config import Config

class BookingService:
    @classmethod
    def create_booking(cls, db: Session, farmer_id: str, crop_id: int,
                       expected_quantity_quintal: float, channel: str = "WEB") -> Booking:
        """
        Validates farmer, crop, quantity, and delegates scheduling to SchedulingService.
        Enforces rules.md §6, §9, §11, PRD.md §10, §11.
        """
        # Validate quantity
        try:
            qty = float(expected_quantity_quintal)
        except (ValueError, TypeError):
            raise ValueError("Expected quantity must be a valid positive number in quintals.")

        if qty <= 0:
            raise ValueError("Quantity in quintals must be greater than zero.")

        # Validate farmer
        farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            raise ValueError(f"Farmer with ID '{farmer_id}' not found.")
        if farmer.status != 'ACTIVE':
            raise ValueError("Farmer account is not active.")

        # Validate crop
        crop = db.query(Crop).filter(Crop.crop_id == crop_id).first()
        if not crop:
            raise ValueError(f"Crop with ID {crop_id} not found.")
        if crop.status != 'ACTIVE':
            raise ValueError(f"Crop '{crop.name}' is currently inactive.")

        # Validate farmer-crop association
        farmer_has_crop = db.query(FarmerCrop).filter(
            FarmerCrop.farmer_id == farmer_id,
            FarmerCrop.crop_id == crop_id
        ).first()
        if not farmer_has_crop:
            raise ValueError(f"Crop '{crop.name}' is not registered under your farmer profile.")

        # Season check (rule: PRD §10.3, rules.md §5)
        current_season = Config.CURRENT_SEASON
        if current_season and current_season != 'All':
            if crop.season not in [current_season, 'All']:
                raise ValueError(f"Crop '{crop.name}' belongs to {crop.season} season, but current procurement season is {current_season}.")

        # Check for active existing booking for this farmer + crop combination (duplicate protection)
        existing_active = db.query(Booking).filter(
            Booking.farmer_id == farmer_id,
            Booking.crop_id == crop_id,
            Booking.status.in_(['BOOKED', 'SCHEDULED', 'ARRIVED', 'PROCUREMENT'])
        ).first()
        if existing_active:
            raise ValueError(f"You already have an active booking for {crop.name} (Token: {existing_active.token_number}, Date: {existing_active.assigned_date.strftime('%d-%m-%Y')}). Please complete or cancel it before booking again.")

        # Allocate slot via Scheduling Service
        now = datetime.now(timezone.utc)
        allocation = SchedulingService.allocate_slot(db, farmer, crop, qty, booking_time=now)

        assigned_date = allocation["assigned_date"]

        # Duplicate same-day booking prevention for same farmer + same crop (PRD §11.8)
        existing_duplicate = db.query(Booking).filter(
            Booking.farmer_id == farmer_id,
            Booking.crop_id == crop_id,
            Booking.assigned_date == assigned_date,
            Booking.status.in_(['BOOKED', 'SCHEDULED', 'ARRIVED', 'PROCUREMENT'])
        ).first()
        if existing_duplicate:
            # Rollback schedule ledger change made during allocate_slot
            SchedulingService.release_capacity(db, Booking(
                center_id=allocation["center_id"],
                assigned_date=assigned_date,
                shift=allocation["shift"],
                estimated_time_minutes=allocation["estimated_time_minutes"]
            ))
            raise ValueError(f"You already have an active booking for {crop.name} on {assigned_date.strftime('%d-%m-%Y')}.")

        # Create booking record
        booking = Booking(
            token_number=allocation["token_number"],
            farmer_id=farmer_id,
            crop_id=crop_id,
            center_id=allocation["center_id"],
            expected_quantity_quintal=qty,
            estimated_time_minutes=allocation["estimated_time_minutes"],
            booking_timestamp=now,
            assigned_date=assigned_date,
            shift=allocation["shift"],
            start_time=allocation["start_time"],
            end_time=allocation["end_time"],
            status='SCHEDULED',
            channel=channel.upper(),
            created_at=now
        )
        db.add(booking)

        # Audit log
        audit = AuditLog(
            actor_type='FARMER' if channel.upper() == 'WEB' else 'SYSTEM',
            actor_id=farmer_id,
            action='CREATE_BOOKING',
            entity_type='booking',
            entity_id=allocation["token_number"],
            details_json=json.dumps({
                "crop": crop.name,
                "quantity": qty,
                "assigned_date": assigned_date.isoformat(),
                "shift": allocation["shift"],
                "center_id": allocation["center_id"]
            })
        )
        db.add(audit)
        db.commit()
        db.refresh(booking)

        # Send simulated SMS confirmation
        NotificationService.send_booking_confirmation(booking)

        return booking

    @classmethod
    def get_booking_by_id(cls, db: Session, booking_id: int, user_role: str = None, user_identifier: str = None) -> Optional[Booking]:
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        if not booking:
            return None

        # RBAC ownership check
        if user_role == 'farmer' and user_identifier and booking.farmer_id != user_identifier:
            raise PermissionError("Access denied: You can only view your own bookings.")
        if user_role == 'center' and user_identifier and booking.center_id != user_identifier:
            raise PermissionError("Access denied: Booking belongs to a different procurement center.")

        return booking

    @classmethod
    def cancel_booking(cls, db: Session, booking_id: int, actor_role: str = "FARMER", actor_id: str = None) -> Booking:
        """
        Cancels booking, releases planning capacity immediately (rules.md §14, PRD §16.8).
        """
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).with_for_update().first()
        if not booking:
            raise ValueError(f"Booking #{booking_id} not found.")

        if booking.status in ['COMPLETED', 'CANCELLED', 'RESCHEDULED']:
            raise ValueError(f"Cannot cancel booking with current status '{booking.status}'.")

        if actor_role == 'FARMER' and actor_id and booking.farmer_id != actor_id:
            raise PermissionError("Access denied: You cannot cancel another farmer's booking.")

        # Release capacity
        SchedulingService.release_capacity(db, booking)

        old_status = booking.status
        booking.status = 'CANCELLED'
        booking.updated_at = datetime.now(timezone.utc)

        # Audit log
        audit = AuditLog(
            actor_type=actor_role,
            actor_id=actor_id or booking.farmer_id,
            action='CANCEL_BOOKING',
            entity_type='booking',
            entity_id=booking.token_number,
            details_json=json.dumps({"old_status": old_status, "new_status": "CANCELLED"})
        )
        db.add(audit)
        db.commit()
        db.refresh(booking)

        # Send simulated cancellation SMS
        NotificationService.send_cancellation(booking)

        return booking

    @classmethod
    def rebook_booking(cls, db: Session, booking_id: int, actor_id: str = None,
                       new_quantity: Optional[float] = None, channel: str = "WEB") -> Booking:
        """
        Rebooking (rules.md §15, PRD §16.8):
        Cancels old booking and creates a new booking through normal allocation engine.
        """
        old_booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        if not old_booking:
            raise ValueError(f"Booking #{booking_id} not found.")

        if actor_id and old_booking.farmer_id != actor_id:
            raise PermissionError("Access denied: You cannot rebook another farmer's slot.")

        farmer_id = old_booking.farmer_id
        crop_id = old_booking.crop_id
        qty = float(new_quantity) if new_quantity else float(old_booking.expected_quantity_quintal)

        # Cancel old booking first to release its slot
        cls.cancel_booking(db, booking_id, actor_role='FARMER', actor_id=actor_id)
        old_booking.status = 'RESCHEDULED'
        db.commit()

        # Create fresh booking
        new_booking = cls.create_booking(db, farmer_id=farmer_id, crop_id=crop_id,
                                          expected_quantity_quintal=qty, channel=channel)
        return new_booking

    @classmethod
    def list_farmer_bookings(cls, db: Session, farmer_id: str, status: Optional[str] = None) -> List[Booking]:
        query = db.query(Booking).filter(Booking.farmer_id == farmer_id)
        if status:
            query = query.filter(Booking.status == status.upper())
        return query.order_by(Booking.assigned_date.desc(), Booking.booking_timestamp.desc()).all()

    @classmethod
    def list_center_bookings(cls, db: Session, center_id: str, sched_date: Optional[date] = None,
                             shift: Optional[str] = None, status: Optional[str] = None) -> List[Booking]:
        query = db.query(Booking).filter(Booking.center_id == center_id)
        if sched_date:
            query = query.filter(Booking.assigned_date == sched_date)
        if shift:
            query = query.filter(Booking.shift == shift.upper())
        if status:
            query = query.filter(Booking.status == status.upper())
        return query.order_by(Booking.assigned_date.asc(), Booking.start_time.asc(), Booking.token_number.asc()).all()

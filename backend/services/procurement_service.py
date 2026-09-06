import json
from datetime import datetime, date, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.models.booking import Booking
from backend.models.procurement import ProcurementRecord, Payment
from backend.models.notification import AuditLog
from backend.services.scheduling_service import SchedulingService
from backend.services.notification_service import NotificationService

class ProcurementService:
    @classmethod
    def verify_token(cls, db: Session, token_number: str, center_id: str) -> Dict[str, Any]:
        """
        Procurement center staff verifies farmer's token upon arrival.
        Checks center ownership and late arrival status.
        """
        booking = db.query(Booking).filter(Booking.token_number == token_number.strip()).first()
        if not booking:
            raise ValueError(f"Token '{token_number}' is invalid or does not exist.")

        if booking.center_id != center_id:
            raise PermissionError("This token is assigned to a different procurement center.")

        if booking.status in ['COMPLETED', 'CANCELLED', 'RESCHEDULED']:
            raise ValueError(f"Booking token cannot be processed. Status: {booking.status}.")

        late_eval = None
        # Check if arriving past assigned date or schedule
        if booking.assigned_date < date.today():
            late_eval = SchedulingService.evaluate_late_arrival(db, booking)

        b_dict = booking.to_dict()
        return {
            **b_dict,
            "booking": b_dict,
            "status": booking.status,
            "late_arrival": late_eval
        }

    @classmethod
    def mark_arrival(cls, db: Session, booking_id: int, center_id: str) -> Booking:
        """
        Marks farmer as arrived at the procurement center (rules.md §19).
        """
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking #{booking_id} not found.")

        if booking.center_id != center_id:
            raise PermissionError("Access denied: Booking is assigned to another procurement center.")

        if booking.status in ['CANCELLED', 'COMPLETED', 'RESCHEDULED']:
            raise ValueError(f"Cannot mark arrival for booking in '{booking.status}' status.")

        booking.status = 'ARRIVED'
        booking.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(booking)
        return booking

    @classmethod
    def complete_procurement(cls, db: Session, booking_id: int, actual_weight_quintal: float,
                             center_id: str, recorded_by: str) -> ProcurementRecord:
        """
        Records actual weight, calculates total amount = actual_weight * rate_per_quintal,
        marks booking COMPLETED, creates initial PENDING payment record.
        Enforces rules.md §20-22, PRD.md §12, §16.9.
        """
        booking = db.query(Booking).filter(Booking.booking_id == booking_id).with_for_update().first()
        if not booking:
            raise ValueError(f"Booking #{booking_id} not found.")

        if booking.center_id != center_id:
            raise PermissionError("Access denied: Booking belongs to a different procurement center.")

        if booking.status in ['CANCELLED', 'COMPLETED', 'RESCHEDULED']:
            raise ValueError(f"Cannot complete procurement for booking with status '{booking.status}'.")

        # Check existing procurement record
        existing = db.query(ProcurementRecord).filter(ProcurementRecord.booking_id == booking_id).first()
        if existing:
            raise ValueError(f"Procurement record already exists for booking #{booking_id}.")

        try:
            actual_qty = float(actual_weight_quintal)
        except (ValueError, TypeError):
            raise ValueError("Actual weight must be a valid number in quintals.")

        if actual_qty <= 0:
            raise ValueError("Actual weight must be greater than zero quintals.")

        # Rate is current rate per quintal from crop master (authoritative)
        crop = booking.crop
        rate_per_quintal = float(crop.rate_per_quintal)
        total_amount = round(actual_qty * rate_per_quintal, 2)

        # Create procurement record
        record = ProcurementRecord(
            booking_id=booking.booking_id,
            farmer_id=booking.farmer_id,
            center_id=booking.center_id,
            crop_id=booking.crop_id,
            actual_weight_quintal=actual_qty,
            rate_per_quintal=rate_per_quintal,
            total_amount=total_amount,
            actual_procurement_time_minutes=booking.estimated_time_minutes,
            procurement_date=date.today(),
            recorded_by=recorded_by,
            created_at=datetime.now(timezone.utc)
        )
        db.add(record)
        db.flush()  # assign record_id

        # Update booking status
        booking.status = 'COMPLETED'
        booking.updated_at = datetime.now(timezone.utc)

        # Create initial Payment record (Pending DBT payment to farmer)
        payment = Payment(
            procurement_record_id=record.record_id,
            amount=total_amount,
            status='PENDING',
            mode='Direct Benefit Transfer (DBT)',
            transaction_ref=f"TXN-DBT-{date.today().strftime('%Y%m%d')}-{record.record_id:04d}",
            created_at=datetime.now(timezone.utc)
        )
        db.add(payment)

        # Audit log
        audit = AuditLog(
            actor_type='CENTER',
            actor_id=center_id,
            action='COMPLETE_PROCUREMENT',
            entity_type='procurement',
            entity_id=str(record.record_id),
            details_json=json.dumps({
                "token": booking.token_number,
                "crop": crop.name,
                "actual_weight": actual_qty,
                "rate": rate_per_quintal,
                "total_amount": total_amount
            })
        )
        db.add(audit)
        db.commit()
        db.refresh(record)

        # Send completion SMS simulation
        NotificationService.send_procurement_completion(record)

        return record

    @classmethod
    def update_payment_status(cls, db: Session, payment_id: int, new_status: str,
                              transaction_ref: Optional[str] = None, mode: Optional[str] = None) -> Payment:
        """
        Updates payment status (PENDING -> PROCESSED -> PAID) and triggers notification.
        """
        valid_statuses = ['PENDING', 'PROCESSED', 'PAID', 'FAILED']
        clean_status = new_status.upper().strip()
        if clean_status not in valid_statuses:
            raise ValueError(f"Invalid payment status. Must be one of {valid_statuses}.")

        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment record #{payment_id} not found.")

        payment.status = clean_status
        if transaction_ref:
            payment.transaction_ref = transaction_ref.strip()
        if mode:
            payment.mode = mode.strip()

        if clean_status == 'PAID':
            payment.payment_date = datetime.now(timezone.utc)

        db.commit()
        db.refresh(payment)

        # Send simulated SMS to farmer
        record = payment.procurement_record
        if record and record.farmer:
            NotificationService.send_payment_update(
                payment=payment,
                farmer_mobile=record.farmer.mobile_number,
                token_number=record.booking.token_number if record.booking else None
            )

        return payment

    @classmethod
    def get_procurement_record(cls, db: Session, record_id: int) -> Optional[ProcurementRecord]:
        return db.query(ProcurementRecord).filter(ProcurementRecord.record_id == record_id).first()

    @classmethod
    def list_center_procurements(cls, db: Session, center_id: str) -> List[ProcurementRecord]:
        return db.query(ProcurementRecord).filter(ProcurementRecord.center_id == center_id).order_by(ProcurementRecord.procurement_date.desc()).all()

    @classmethod
    def list_farmer_procurements(cls, db: Session, farmer_id: str) -> List[ProcurementRecord]:
        return db.query(ProcurementRecord).filter(ProcurementRecord.farmer_id == farmer_id).order_by(ProcurementRecord.procurement_date.desc()).all()

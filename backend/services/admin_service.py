from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.user import Farmer, ProcurementCenter, AdminUser, User
from backend.models.crop import Crop
from backend.models.booking import Booking, CenterDailySchedule
from backend.models.procurement import ProcurementRecord, Payment
from backend.models.notification import AuditLog

class AdminService:
    @classmethod
    def get_system_stats(cls, db: Session) -> Dict[str, Any]:
        total_farmers = db.query(Farmer).count()
        total_centers = db.query(ProcurementCenter).count()
        active_centers = db.query(ProcurementCenter).filter(ProcurementCenter.status == 'ACTIVE').count()
        pending_centers = db.query(ProcurementCenter).filter(ProcurementCenter.status == 'PENDING_VERIFICATION').count()
        total_crops = db.query(Crop).filter(Crop.status == 'ACTIVE').count()

        today = date.today()
        bookings_today = db.query(Booking).filter(Booking.assigned_date == today).count()
        total_bookings = db.query(Booking).count()
        completed_bookings = db.query(Booking).filter(Booking.status == 'COMPLETED').count()

        total_procured_weight = db.query(func.coalesce(func.sum(ProcurementRecord.actual_weight_quintal), 0)).scalar()
        total_payment_amount = db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar()
        total_paid_amount = db.query(func.coalesce(func.sum(Payment.amount), 0)).filter(Payment.status == 'PAID').scalar()

        return {
            "total_farmers": total_farmers,
            "total_centers": total_centers,
            "active_centers": active_centers,
            "pending_verification_centers": pending_centers,
            "total_crops": total_crops,
            "total_bookings": total_bookings,
            "bookings_today": bookings_today,
            "completed_bookings": completed_bookings,
            "total_procured_weight_quintals": float(total_procured_weight),
            "total_payment_amount_inr": float(total_payment_amount),
            "total_paid_amount_inr": float(total_paid_amount),
            "farmers": {"total": total_farmers},
            "centers": {
                "total": total_centers,
                "active": active_centers,
                "pending_verification": pending_centers
            },
            "bookings": {
                "total": total_bookings,
                "today": bookings_today,
                "completed": completed_bookings
            },
            "procurements": {
                "completed": completed_bookings,
                "total_weight_quintals": float(total_procured_weight),
                "total_payout_amount": float(total_payment_amount),
                "total_paid_amount": float(total_paid_amount)
            },
            "crops": {
                "active": total_crops
            }
        }

    @classmethod
    def list_farmers(cls, db: Session, query_str: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        q = db.query(Farmer)
        if status:
            q = q.filter(Farmer.status == status.upper())
        if query_str:
            term = f"%{query_str.strip()}%"
            q = q.filter((Farmer.name.ilike(term)) | (Farmer.farmer_id.ilike(term)) | (Farmer.mobile_number.ilike(term)) | (Farmer.district.ilike(term)))
        farmers = q.order_by(Farmer.created_at.desc()).all()
        return [f.to_dict(mask_aadhaar=True) for f in farmers]

    @classmethod
    def set_farmer_status(cls, db: Session, farmer_id: str, new_status: str) -> dict:
        farmer = db.query(Farmer).filter(Farmer.farmer_id == farmer_id).first()
        if not farmer:
            raise ValueError(f"Farmer '{farmer_id}' not found.")
        farmer.status = new_status.upper()
        db.commit()
        return farmer.to_dict(mask_aadhaar=True)

    @classmethod
    def list_centers(cls, db: Session, status: Optional[str] = None, query_str: Optional[str] = None) -> List[dict]:
        q = db.query(ProcurementCenter)
        if status:
            q = q.filter(ProcurementCenter.status == status.upper())
        if query_str:
            term = f"%{query_str.strip()}%"
            q = q.filter((ProcurementCenter.name.ilike(term)) | (ProcurementCenter.center_id.ilike(term)) | (ProcurementCenter.district.ilike(term)))
        centers = q.order_by(ProcurementCenter.created_at.desc()).all()
        return [c.to_dict() for c in centers]

    @classmethod
    def verify_center(cls, db: Session, center_id: str, action: str) -> dict:
        """Approves or rejects a procurement center (PRD §9.2, FR-021)."""
        center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == center_id).first()
        if not center:
            raise ValueError(f"Center '{center_id}' not found.")

        if action.upper() == 'APPROVE':
            center.status = 'ACTIVE'
        elif action.upper() == 'REJECT' or action.upper() == 'SUSPEND':
            center.status = 'SUSPENDED'
        else:
            raise ValueError("Action must be 'APPROVE' or 'SUSPEND'.")

        db.commit()
        db.refresh(center)
        return center.to_dict()

    @classmethod
    def list_all_bookings(cls, db: Session, center_id: Optional[str] = None,
                          crop_id: Optional[int] = None, status: Optional[str] = None,
                          booking_date: Optional[date] = None) -> List[dict]:
        q = db.query(Booking)
        if center_id:
            q = q.filter(Booking.center_id == center_id)
        if crop_id:
            q = q.filter(Booking.crop_id == crop_id)
        if status:
            q = q.filter(Booking.status == status.upper())
        if booking_date:
            q = q.filter(Booking.assigned_date == booking_date)
        bookings = q.order_by(Booking.assigned_date.desc(), Booking.booking_timestamp.desc()).all()
        return [b.to_dict() for b in bookings]

    @classmethod
    def list_procurement_records(cls, db: Session, center_id: Optional[str] = None) -> List[dict]:
        q = db.query(ProcurementRecord)
        if center_id:
            q = q.filter(ProcurementRecord.center_id == center_id)
        records = q.order_by(ProcurementRecord.procurement_date.desc()).all()
        return [r.to_dict() for r in records]

    @classmethod
    def get_capacity_utilization_report(cls, db: Session, target_date: Optional[date] = None) -> List[dict]:
        report_date = target_date or date.today()
        centers = db.query(ProcurementCenter).filter(ProcurementCenter.status == 'ACTIVE').all()
        report = []

        for c in centers:
            schedules = db.query(CenterDailySchedule).filter(
                CenterDailySchedule.center_id == c.center_id,
                CenterDailySchedule.schedule_date == report_date
            ).all()

            s1 = next((s for s in schedules if s.shift == 'SHIFT_1'), None)
            s2 = next((s for s in schedules if s.shift == 'SHIFT_2'), None)

            s1_comm = s1.committed_minutes if s1 else 0
            s2_comm = s2.committed_minutes if s2 else 0
            total_comm = s1_comm + s2_comm
            plan_cap = c.daily_capacity_minutes or 420
            pct = round((total_comm / plan_cap * 100), 1) if plan_cap else 0

            report.append({
                "center_id": c.center_id,
                "center_name": c.name,
                "district": c.district,
                "date": report_date.isoformat(),
                "planning_capacity_minutes": plan_cap,
                "committed_minutes": total_comm,
                "remaining_minutes": max(0, plan_cap - total_comm),
                "utilization_percentage": min(100.0, pct),
                "shift_1_committed": s1_comm,
                "shift_2_committed": s2_comm
            })

        return report

    @classmethod
    def list_audit_logs(cls, db: Session, limit: int = 50) -> List[dict]:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
        return [l.to_dict() for l in logs]

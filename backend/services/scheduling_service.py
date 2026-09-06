from datetime import datetime, date, timedelta, time, timezone
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from backend.models.crop import Crop, CenterCrop
from backend.models.user import ProcurementCenter, Farmer
from backend.models.booking import Booking, CenterDailySchedule
from backend.config import Config

class SchedulingService:
    """
    Sole authority for all scheduling and slot allocation decisions.
    Enforces rules.md §8-12, PRD.md §11, architecture.md §9.
    Used identically by Web and IVR booking flows.
    """

    @classmethod
    def calculate_estimated_time(cls, crop: Crop, quantity_quintals: float) -> int:
        """
        Procurement duration formula (rules.md §7):
        Estimated Time (min) = time_to_unload_per_quintal_minutes * quantity_in_quintals
        """
        rate_time = crop.time_to_unload_per_quintal_minutes or 5
        duration = int(round(float(quantity_quintals) * rate_time))
        return max(1, duration)

    @classmethod
    def find_eligible_centers(cls, db: Session, crop_id: int, farmer: Optional[Farmer] = None) -> List[ProcurementCenter]:
        """
        Finds active procurement centers that accept the specified crop (rules.md §5, PRD §11.4).
        Ranked deterministically:
        1. Same district as farmer (if farmer provided)
        2. Same state as farmer (if farmer provided)
        3. center_id ascending
        """
        centers = (
            db.query(ProcurementCenter)
            .join(CenterCrop, ProcurementCenter.center_id == CenterCrop.center_id)
            .filter(
                CenterCrop.crop_id == crop_id,
                ProcurementCenter.status == 'ACTIVE'
            )
            .all()
        )

        if not centers:
            return []

        def sort_key(c: ProcurementCenter):
            score = 0
            if farmer:
                if c.district.strip().lower() == farmer.district.strip().lower():
                    score -= 20
                if c.state.strip().lower() == farmer.state.strip().lower():
                    score -= 10
            return (score, c.center_id)

        centers.sort(key=sort_key)
        return centers

    @classmethod
    def allocate_slot(cls, db: Session, farmer: Farmer, crop: Crop,
                      quantity_quintals: float, booking_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Main allocation engine:
        1. Calculates estimated duration.
        2. Finds eligible centers.
        3. Looks for earliest available date & shift satisfying the 7-hour (420 min) planning limit.
        4. Calculates precise start_time and end_time.
        5. Atomically commits capacity and generates unique token.
        """
        estimated_minutes = cls.calculate_estimated_time(crop, quantity_quintals)
        eligible_centers = cls.find_eligible_centers(db, crop.crop_id, farmer)

        if not eligible_centers:
            raise ValueError(f"No active procurement center currently accepts {crop.name}.")

        booking_ts = booking_time or datetime.now(timezone.utc)
        # Search starting from tomorrow (or today if early enough, but standard practice is next operating day)
        start_date = date.today()
        # Look ahead up to 30 days
        for day_offset in range(1, 31):
            candidate_date = start_date + timedelta(days=day_offset)

            # Skip date if farmer already has an active booking for the same crop on this date (PRD §11.8)
            existing_for_day = db.query(Booking).filter(
                Booking.farmer_id == farmer.farmer_id,
                Booking.crop_id == crop.crop_id,
                Booking.assigned_date == candidate_date,
                Booking.status.in_(['BOOKED', 'SCHEDULED', 'ARRIVED', 'PROCUREMENT'])
            ).first()
            if existing_for_day:
                continue

            for center in eligible_centers:
                # Try Shift 1, then Shift 2
                for shift_name in ['SHIFT_1', 'SHIFT_2']:
                    shift_capacity = (center.shift1_capacity_minutes if shift_name == 'SHIFT_1'
                                      else center.shift2_capacity_minutes) or Config.SHIFT_PLANNING_MINUTES

                    # Fetch or create schedule row with row-level locking
                    schedule = (
                        db.query(CenterDailySchedule)
                        .filter(
                            CenterDailySchedule.center_id == center.center_id,
                            CenterDailySchedule.schedule_date == candidate_date,
                            CenterDailySchedule.shift == shift_name
                        )
                        .with_for_update()
                        .first()
                    )

                    committed = schedule.committed_minutes if schedule else 0

                    # Check 7-hour rule: shift planning capacity limit
                    if committed + estimated_minutes <= shift_capacity:
                        # Check full day total across both shifts <= 420 minutes
                        day_committed_total = cls._get_day_committed_total(db, center.center_id, candidate_date)
                        if day_committed_total + estimated_minutes <= Config.DAILY_PLANNING_MINUTES:
                            # Found capacity! Calculate slot timing
                            start_str, end_str = cls._compute_shift_time_window(shift_name, committed, estimated_minutes)

                            # Reserve capacity
                            if not schedule:
                                schedule = CenterDailySchedule(
                                    center_id=center.center_id,
                                    schedule_date=candidate_date,
                                    shift=shift_name,
                                    committed_minutes=committed + estimated_minutes,
                                    capacity_minutes=shift_capacity
                                )
                                db.add(schedule)
                            else:
                                schedule.committed_minutes = committed + estimated_minutes

                            # Generate unique token
                            token = cls._generate_token(db, candidate_date)

                            return {
                                "center": center,
                                "center_id": center.center_id,
                                "assigned_date": candidate_date,
                                "shift": shift_name,
                                "start_time": start_str,
                                "end_time": end_str,
                                "estimated_time_minutes": estimated_minutes,
                                "token_number": token,
                                "booking_timestamp": booking_ts
                            }

        raise ValueError("Could not find an available procurement slot within the next 30 days.")

    @classmethod
    def _get_day_committed_total(cls, db: Session, center_id: str, sched_date: date) -> int:
        total = (
            db.query(func.coalesce(func.sum(CenterDailySchedule.committed_minutes), 0))
            .filter(
                CenterDailySchedule.center_id == center_id,
                CenterDailySchedule.schedule_date == sched_date
            )
            .scalar()
        )
        return int(total)

    @classmethod
    def _compute_shift_time_window(cls, shift: str, committed_before: int, duration: int) -> Tuple[str, str]:
        """
        Shift 1: 09:00 - 12:30 (210 min)
        Shift 2: 14:00 - 17:30 (210 min)
        """
        base_hour, base_minute = (9, 0) if shift == 'SHIFT_1' else (14, 0)
        start_total_min = base_minute + committed_before
        start_h = base_hour + (start_total_min // 60)
        start_m = start_total_min % 60

        end_total_min = start_total_min + duration
        end_h = base_hour + (end_total_min // 60)
        end_m = end_total_min % 60

        return f"{start_h:02d}:{start_m:02d}", f"{end_h:02d}:{end_m:02d}"

    @classmethod
    def _generate_token(cls, db: Session, assigned_date: date) -> str:
        """
        Format: TK-YYYYMMDD-####
        e.g. TK-20260906-0001
        """
        date_str = assigned_date.strftime("%Y%m%d")
        prefix = f"TK-{date_str}-"
        # Count existing bookings on that date
        count = db.query(Booking).filter(Booking.assigned_date == assigned_date).count()
        token = f"{prefix}{count + 1:04d}"
        # Ensure uniqueness
        while db.query(Booking).filter(Booking.token_number == token).first():
            count += 1
            token = f"{prefix}{count + 1:04d}"
        return token

    @classmethod
    def release_capacity(cls, db: Session, booking: Booking):
        """
        Releases committed capacity when a booking is cancelled.
        Rules.md §14.3: A cancelled booking must not continue occupying normal scheduling capacity.
        """
        if not booking.center_id or not booking.assigned_date or not booking.shift:
            return

        schedule = (
            db.query(CenterDailySchedule)
            .filter(
                CenterDailySchedule.center_id == booking.center_id,
                CenterDailySchedule.schedule_date == booking.assigned_date,
                CenterDailySchedule.shift == booking.shift
            )
            .with_for_update()
            .first()
        )

        if schedule:
            schedule.committed_minutes = max(0, schedule.committed_minutes - booking.estimated_time_minutes)

    @classmethod
    def evaluate_late_arrival(cls, db: Session, booking: Booking) -> Dict[str, Any]:
        """
        Late arrival rule (rules.md §13, PRD §12.2):
        Checks if center's remaining real operational bandwidth (up to ~8.5h / 510 min) can absorb this farmer.
        """
        center_id = booking.center_id
        assigned_date = booking.assigned_date

        total_day_committed = cls._get_day_committed_total(db, center_id, assigned_date)
        duration = booking.estimated_time_minutes

        if total_day_committed + duration <= Config.HARD_CEILING_MINUTES:
            return {
                "can_accommodate": True,
                "message": "Farmer accommodated within operational delay buffer (operational bandwidth available).",
                "remaining_bandwidth_minutes": Config.HARD_CEILING_MINUTES - (total_day_committed + duration)
            }
        else:
            return {
                "can_accommodate": False,
                "message": "Center operational capacity exhausted for today. Farmer must rebook.",
                "remaining_bandwidth_minutes": max(0, Config.HARD_CEILING_MINUTES - total_day_committed)
            }

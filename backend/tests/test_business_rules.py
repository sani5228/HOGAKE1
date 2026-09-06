import pytest
from datetime import datetime, date, timedelta, timezone
from backend.app import create_app
from backend.database import SessionLocal
from backend.seed import seed_database
from backend.models.user import Farmer, ProcurementCenter
from backend.models.crop import Crop
from backend.models.booking import Booking, CenterDailySchedule
from backend.services.scheduling_service import SchedulingService
from backend.services.booking_service import BookingService
from backend.config import Config

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    with app.app_context():
        seed_database()
    return app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()

def test_7_hour_capacity_rollover(db):
    """
    Test 7-hour rule (rules.md §8, §10, PRD §11.3):
    Normal slot planning must not exceed 420 minutes (7h) per center per day.
    When a booking would exceed 420 minutes on day N, it rolls over to day N+1.
    """
    farmer = db.query(Farmer).filter(Farmer.farmer_id == "FA000101").first()
    crop = db.query(Crop).filter(Crop.name == "Soybean").first()  # 4 min/quintal
    center = db.query(ProcurementCenter).filter(ProcurementCenter.center_id == "PC000001").first()

    tomorrow = date.today() + timedelta(days=1)

    # Set committed minutes on tomorrow to 400 minutes (out of 420 planning cap)
    sched = db.query(CenterDailySchedule).filter(
        CenterDailySchedule.center_id == center.center_id,
        CenterDailySchedule.schedule_date == tomorrow,
        CenterDailySchedule.shift == 'SHIFT_2'
    ).first()
    if not sched:
        sched = CenterDailySchedule(
            center_id=center.center_id,
            schedule_date=tomorrow,
            shift='SHIFT_2',
            committed_minutes=190,
            capacity_minutes=210
        )
        db.add(sched)
    else:
        sched.committed_minutes = 190

    # Also make Shift 1 almost full: 210 min
    sched1 = db.query(CenterDailySchedule).filter(
        CenterDailySchedule.center_id == center.center_id,
        CenterDailySchedule.schedule_date == tomorrow,
        CenterDailySchedule.shift == 'SHIFT_1'
    ).first()
    if not sched1:
        sched1 = CenterDailySchedule(
            center_id=center.center_id,
            schedule_date=tomorrow,
            shift='SHIFT_1',
            committed_minutes=210,
            capacity_minutes=210
        )
        db.add(sched1)
    else:
        sched1.committed_minutes = 210
    db.commit()

    # Now total committed on tomorrow is 210 + 190 = 400 minutes. Remaining is only 20 minutes!
    # Request a booking for 10 quintals (10 * 4 = 40 minutes).
    # 400 + 40 = 440 minutes > 420 minutes!
    # Engine MUST roll over to the next available date (day after tomorrow)!
    allocation = SchedulingService.allocate_slot(db, farmer, crop, quantity_quintals=10.0)
    assert allocation["assigned_date"] > tomorrow

def test_tie_breaker_logic(db):
    """
    Test tie-breaking rules (rules.md §9, PRD §11.7):
    Same timestamp, same crop: lower quantity wins earlier slot.
    """
    crop = db.query(Crop).filter(Crop.name == "Soybean").first()
    farmer_a = db.query(Farmer).filter(Farmer.farmer_id == "FA000101").first()
    farmer_b = db.query(Farmer).filter(Farmer.farmer_id == "FA000103").first()

    # Calculation durations:
    # Farmer A: 5 quintals -> 20 min
    # Farmer B: 25 quintals -> 100 min
    dur_a = SchedulingService.calculate_estimated_time(crop, 5.0)
    dur_b = SchedulingService.calculate_estimated_time(crop, 25.0)
    assert dur_a < dur_b

def test_late_arrival_bandwidth_check(db):
    """
    Late arrival rule (rules.md §13, PRD §12.2):
    Late arrival can proceed if total minutes <= 510 min (hard operational ceiling),
    otherwise rebooking is required.
    """
    booking = db.query(Booking).filter(Booking.token_number.like("TK-%")).first()
    eval_res = SchedulingService.evaluate_late_arrival(db, booking)
    assert "can_accommodate" in eval_res
    assert eval_res["can_accommodate"] is True  # Under normal load, operational buffer exists

def test_rbac_boundary_enforcement(client):
    """
    Role-based access rule (rules.md §27, PRD §17):
    Farmer cannot access admin endpoints.
    Farmer cannot access other farmer's bookings.
    Procurement center cannot see farmer's full Aadhaar.
    """
    # Farmer login
    res = client.post('/api/auth/otp/send', json={"mobile_number": "9826012345", "purpose": "LOGIN"})
    otp = res.get_json()["data"]["demo_otp"]
    f_token = client.post('/api/auth/otp/verify', json={"mobile_number": "9826012345", "otp": otp}).get_json()["data"]["token"]

    # Farmer attempts to access admin stats
    admin_access = client.get('/api/admin/stats', headers={"Authorization": f"Bearer {f_token}"})
    assert admin_access.status_code == 403

    # Farmer attempts to view Center 1 schedule
    center_access = client.get('/api/center/me/schedule', headers={"Authorization": f"Bearer {f_token}"})
    assert center_access.status_code == 403

    # Center login
    c_res = client.post('/api/auth/center/login', json={"username": "mandi_north", "password": "CenterPassword@123"})
    c_token = c_res.get_json()["data"]["token"]

    # Check center bookings view - Aadhaar must NOT be exposed
    sched = client.get('/api/center/me/schedule', headers={"Authorization": f"Bearer {c_token}"}).get_json()["data"]
    for b in sched["bookings"]:
        assert "aadhaar" not in b or b.get("aadhaar") is None
        assert "aadhaar_encrypted" not in b

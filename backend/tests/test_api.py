import pytest
from datetime import date, timedelta
from backend.app import create_app
from backend.database import SessionLocal, init_db
from backend.seed import seed_database
from backend.models.user import Farmer, ProcurementCenter, AdminUser
from backend.models.crop import Crop
from backend.models.booking import Booking
from backend.models.procurement import ProcurementRecord, Payment
from backend.services.scheduling_service import SchedulingService

@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    with app.app_context():
        seed_database()
    return app

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture
def db():
    db = SessionLocal()
    yield db
    db.close()

# 1. AUTHENTICATION TESTS
def test_otp_send_and_verify(client):
    # Send OTP
    res = client.post('/api/auth/otp/send', json={"mobile_number": "9826099999", "purpose": "REGISTRATION"})
    assert res.status_code == 200
    data = res.get_json()["data"]
    otp = data["demo_otp"]
    assert len(otp) == 6

    # Verify invalid OTP
    bad_res = client.post('/api/auth/otp/verify', json={"mobile_number": "9826099999", "otp": "000000"})
    assert bad_res.status_code == 400

    # Verify valid OTP
    good_res = client.post('/api/auth/otp/verify', json={"mobile_number": "9826099999", "otp": otp})
    assert good_res.status_code == 200
    assert good_res.get_json()["data"]["verified"] is True

def test_farmer_login_via_otp(client):
    # Farmer 1 (Ramesh Chandra: 9826012345)
    res = client.post('/api/auth/otp/send', json={"mobile_number": "9826012345", "purpose": "LOGIN"})
    assert res.status_code == 200
    otp = res.get_json()["data"]["demo_otp"]

    verify_res = client.post('/api/auth/otp/verify', json={"mobile_number": "9826012345", "otp": otp})
    assert verify_res.status_code == 200
    token = verify_res.get_json()["data"]["token"]
    assert token is not None

def test_center_and_admin_login(client):
    # Center login
    c_res = client.post('/api/auth/center/login', json={"username": "mandi_north", "password": "CenterPassword@123"})
    assert c_res.status_code == 200
    assert c_res.get_json()["data"]["role"] == "center"

    # Admin login
    a_res = client.post('/api/auth/admin/login', json={"username": "admin", "password": "AdminPassword@123"})
    assert a_res.status_code == 200
    assert a_res.get_json()["data"]["role"] == "admin"

    # Bad password
    bad = client.post('/api/auth/admin/login', json={"username": "admin", "password": "WrongPassword"})
    assert bad.status_code == 401

# 2. FARMER REGISTRATION TESTS
def test_farmer_registration_workflow(client):
    reg_data = {
        "name": "Kailash Verma",
        "mobile_number": "9826088888",
        "aadhaar": "999888777666",
        "state": "Madhya Pradesh",
        "district": "Indore",
        "village_town": "Mhow",
        "crop_ids": [1, 2]
    }
    res = client.post('/api/farmer/register', json=reg_data)
    assert res.status_code == 201
    d = res.get_json()["data"]
    assert d["farmer"]["farmer_id"].startswith("FA")
    assert d["farmer"]["aadhaar_last4"] == "7666"

    # Duplicate mobile check
    dup = client.post('/api/farmer/register', json=reg_data)
    assert dup.status_code == 400

# 3. BOOKING AND SCHEDULING TESTS
def test_slot_booking_and_capacity(client, db):
    # Log in as Farmer 1
    otp_res = client.post('/api/auth/otp/send', json={"mobile_number": "9826012345", "purpose": "LOGIN"})
    otp = otp_res.get_json()["data"]["demo_otp"]
    token = client.post('/api/auth/otp/verify', json={"mobile_number": "9826012345", "otp": otp}).get_json()["data"]["token"]

    # Fetch eligible crops
    crops_res = client.get('/api/bookings/eligible-crops', headers={"Authorization": f"Bearer {token}"})
    assert crops_res.status_code == 200
    eligible = crops_res.get_json()["data"]
    assert len(eligible) > 0

    # Book a slot for in-season crop (Soybean)
    soybean = next(c for c in eligible if "Soybean" in c["name"])
    booking_req = {
        "crop_id": soybean["crop_id"],
        "expected_quantity_quintal": 10.0,
        "channel": "WEB"
    }
    b_res = client.post('/api/bookings', json=booking_req, headers={"Authorization": f"Bearer {token}"})
    assert b_res.status_code == 201
    booking = b_res.get_json()["data"]
    assert booking["token_number"].startswith("TK-")
    assert booking["estimated_time_minutes"] == 40  # 10 quintals * 4 min/quintal

    # Test Duplicate same-day booking prevention
    # Trying to book the exact same crop again
    dup_res = client.post('/api/bookings', json=booking_req, headers={"Authorization": f"Bearer {token}"})
    assert dup_res.status_code == 400

# 4. PROCUREMENT AND PAYMENT TESTS
def test_procurement_completion_and_payment(client):
    # Login as Center Staff
    c_res = client.post('/api/auth/center/login', json={"username": "mandi_north", "password": "CenterPassword@123"})
    c_token = c_res.get_json()["data"]["token"]

    # Verify token for today's arrived booking (Booking 2 from seed: Moong)
    verify_res = client.post('/api/procurement/verify-token', json={"token_number": f"TK-{date.today().strftime('%Y%m%d')}-0001"}, headers={"Authorization": f"Bearer {c_token}"})
    assert verify_res.status_code == 200
    booking = verify_res.get_json()["data"]["booking"]
    b_id = booking["booking_id"]

    # Record actual weight (16.0 quintals instead of expected 15.0)
    rec_res = client.post(f'/api/procurement/{b_id}/record', json={"actual_weight_quintal": 16.0}, headers={"Authorization": f"Bearer {c_token}"})
    assert rec_res.status_code == 201
    record = rec_res.get_json()["data"]
    assert record["actual_weight_quintal"] == 16.0
    # Moong rate is 8558 -> 16.0 * 8558 = 136928.00
    assert record["total_amount"] == 16.0 * record["rate_per_quintal"]
    assert record["payment_status"] == "PENDING"

    # Update payment status to PAID
    rec_detail = client.get(f'/api/procurement/{record["record_id"]}', headers={"Authorization": f"Bearer {c_token}"})
    # Fetch payment record ID
    db = SessionLocal()
    pay = db.query(Payment).filter(Payment.procurement_record_id == record["record_id"]).first()
    pay_id = pay.payment_id
    db.close()

    p_update = client.put(f'/api/procurement/payment/{pay_id}/status', json={"status": "PAID", "transaction_ref": "TXN-TEST-9999"}, headers={"Authorization": f"Bearer {c_token}"})
    assert p_update.status_code == 200
    assert p_update.get_json()["data"]["status"] == "PAID"

# 5. CANCELLATION AND REBOOKING TESTS
def test_cancellation_and_rebooking(client):
    # Login as Farmer 3 (Aditi Mishra)
    res = client.post('/api/auth/otp/send', json={"mobile_number": "9826034567", "purpose": "LOGIN"})
    otp = res.get_json()["data"]["demo_otp"]
    token = client.post('/api/auth/otp/verify', json={"mobile_number": "9826034567", "otp": otp}).get_json()["data"]["token"]

    # Get my bookings
    my_b = client.get('/api/farmer/me/bookings', headers={"Authorization": f"Bearer {token}"}).get_json()["data"]
    assert len(my_b) > 0
    target_booking = my_b[0]
    b_id = target_booking["booking_id"]

    # Rebook
    rebook_res = client.post(f'/api/bookings/{b_id}/rebook', json={"expected_quantity_quintal": 30.0}, headers={"Authorization": f"Bearer {token}"})
    assert rebook_res.status_code == 201
    new_b = rebook_res.get_json()["data"]
    assert new_b["token_number"] != target_booking["token_number"]
    assert new_b["expected_quantity_quintal"] == 30.0

    # Cancel the new booking
    cancel_res = client.post(f'/api/bookings/{new_b["booking_id"]}/cancel', headers={"Authorization": f"Bearer {token}"})
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["data"]["status"] == "CANCELLED"

# 6. SIMULATED IVR TESTS
def test_simulated_ivr_workflow(client):
    # Start IVR session for Farmer 2 (Suresh Kumar - mobile: 9826023456)
    s_res = client.post('/api/ivr/session/start', json={"caller_mobile": "9826023456"})
    assert s_res.status_code == 200
    session_id = s_res.get_json()["data"]["session_id"]

    # Select language (1 for Hindi)
    l_res = client.post(f'/api/ivr/session/{session_id}/select-language', json={"digit": "1"})
    assert l_res.status_code == 200

    # Select crop (digit 1)
    c_res = client.post(f'/api/ivr/session/{session_id}/select-crop', json={"digit": 1})
    assert c_res.status_code == 200

    # Enter quantity (12.0 quintals)
    q_res = client.post(f'/api/ivr/session/{session_id}/enter-quantity', json={"quantity": 12.0})
    assert q_res.status_code == 200

    # Confirm booking
    conf_res = client.post(f'/api/ivr/session/{session_id}/confirm-booking')
    assert conf_res.status_code == 201
    b_data = conf_res.get_json()["data"]["booking"]
    assert b_data["channel"] == "IVR"

# 7. CHATBOT TESTS
def test_chatbot_faq(client):
    intents = client.get('/api/chatbot/intents').get_json()["data"]
    assert len(intents) >= 5

    q1 = client.post('/api/chatbot/query', json={"query": "how do I book a slot"}).get_json()["data"]
    assert q1["matched"] is True
    assert "Book Slot" in q1["answer"]

    q2 = client.post('/api/chatbot/query', json={"query": "how is payment calculated"}).get_json()["data"]
    assert q2["matched"] is True
    assert "Rate per Quintal" in q2["answer"]

# 8. ADMIN DASHBOARD & REPORTS TESTS
def test_admin_reports_and_management(client):
    a_res = client.post('/api/auth/admin/login', json={"username": "admin", "password": "AdminPassword@123"})
    a_token = a_res.get_json()["data"]["token"]

    stats = client.get('/api/admin/stats', headers={"Authorization": f"Bearer {a_token}"}).get_json()["data"]
    assert stats["total_farmers"] >= 3
    assert stats["total_centers"] >= 3

    # Capacity utilization report
    report = client.get('/api/admin/reports/capacity-utilization', headers={"Authorization": f"Bearer {a_token}"}).get_json()["data"]
    assert len(report) >= 2

    # Center verification
    verify = client.put('/api/admin/centers/PC000003/verify', json={"action": "APPROVE"}, headers={"Authorization": f"Bearer {a_token}"})
    assert verify.status_code == 200
    assert verify.get_json()["data"]["status"] == "ACTIVE"

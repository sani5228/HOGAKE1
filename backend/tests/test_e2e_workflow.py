import pytest
from datetime import date, timedelta
from backend.app import create_app
from backend.database import SessionLocal
from backend.seed import seed_database
from backend.models.user import Farmer, ProcurementCenter, AdminUser
from backend.models.crop import Crop
from backend.models.booking import Booking
from backend.models.procurement import ProcurementRecord, Payment
from backend.services.scheduling_service import SchedulingService

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

def test_complete_end_to_end_procurement_workflow(client, db):
    """
    Tests the complete end-to-end workflow per PRD and User Request:
    Farmer Registration -> OTP -> Login -> Slot Booking -> Token Generated
    -> Center Token Verification -> Arrival -> Actual Weighing & Procurement
    -> Payment Settlement -> Audit Trail & SMS Simulation
    """
    # 1. Farmer Registration with OTP
    reg_mobile = "9826077777"
    otp_res = client.post('/api/auth/otp/send', json={"mobile_number": reg_mobile, "purpose": "REGISTRATION"})
    assert otp_res.status_code == 200
    otp = otp_res.get_json()["data"]["demo_otp"]

    verify_otp_res = client.post('/api/auth/otp/verify', json={"mobile_number": reg_mobile, "otp": otp})
    assert verify_otp_res.status_code == 200

    active_crops = db.query(Crop).filter(Crop.status == 'ACTIVE', Crop.season == 'Kharif').all()
    c_soybean = next(c for c in active_crops if "Soybean" in c.name)
    c_rice = next(c for c in active_crops if "Paddy" in c.name or "Rice" in c.name)

    farmer_payload = {
        "name": "Devendra Patidar",
        "mobile_number": reg_mobile,
        "aadhaar": "555544443333",
        "state": "Madhya Pradesh",
        "district": "Indore",
        "village_town": "Depalpur",
        "crop_ids": [c_soybean.crop_id, c_rice.crop_id],
        "password": "FarmerPassword@123"
    }
    reg_res = client.post('/api/farmer/register', json=farmer_payload)
    assert reg_res.status_code == 201
    farmer_data = reg_res.get_json()["data"]["farmer"]
    farmer_id = farmer_data["farmer_id"]
    assert farmer_id.startswith("FA")

    # 2. Farmer Login via OTP
    login_otp_res = client.post('/api/auth/otp/send', json={"mobile_number": reg_mobile, "purpose": "LOGIN"})
    login_otp = login_otp_res.get_json()["data"]["demo_otp"]
    login_res = client.post('/api/auth/otp/verify', json={"mobile_number": reg_mobile, "otp": login_otp})
    assert login_res.status_code == 200
    farmer_token = login_res.get_json()["data"]["token"]
    headers_farmer = {"Authorization": f"Bearer {farmer_token}"}

    # 3. Farmer views eligible crops
    crops_res = client.get('/api/bookings/eligible-crops', headers=headers_farmer)
    assert crops_res.status_code == 200
    crops = crops_res.get_json()["data"]
    assert len(crops) > 0

    # 4. Farmer books slot: Soybean, 20 quintals
    booking_res = client.post('/api/bookings', headers=headers_farmer, json={
        "crop_id": c_soybean.crop_id,
        "expected_quantity_quintal": 20.0
    })
    assert booking_res.status_code == 201
    booking = booking_res.get_json()["data"]
    booking_id = booking["booking_id"]
    token_num = booking["token_number"]
    assert token_num.startswith("TK-")
    assert booking["status"] in ["BOOKED", "SCHEDULED"]
    assert booking["center_id"] is not None

    # 5. Center Staff Login (mandi_north)
    center_login_res = client.post('/api/auth/center/login', json={
        "username": "mandi_north",
        "password": "CenterPassword@123"
    })
    assert center_login_res.status_code == 200
    center_token = center_login_res.get_json()["data"]["token"]
    headers_center = {"Authorization": f"Bearer {center_token}"}

    # 6. Center verifies Token
    token_verify_res = client.post('/api/procurement/verify-token', headers=headers_center, json={
        "token_number": token_num
    })
    assert token_verify_res.status_code == 200
    assert token_verify_res.get_json()["data"]["booking_id"] == booking_id

    # 7. Center marks Arrival
    arr_res = client.post(f'/api/procurement/{booking_id}/arrival', headers=headers_center)
    assert arr_res.status_code == 200
    assert arr_res.get_json()["data"]["status"] == "ARRIVED"

    # 8. Center records Actual Weight & completes Procurement
    # Actual weighed is 20.5 quintals at MSP ₹4,600/quintal
    proc_res = client.post(f'/api/procurement/{booking_id}/record', headers=headers_center, json={
        "actual_weight_quintal": 20.5
    })
    assert proc_res.status_code == 201
    proc_record = proc_res.get_json()["data"]
    expected_amount = round(20.5 * 4600.0, 2)
    assert proc_record["total_amount"] == expected_amount
    assert proc_record["payment_status"] == "PENDING"
    payment_id = proc_record["payment_id"]

    # 9. Center or Admin updates Payment Status to PAID
    pay_res = client.put(f'/api/procurement/payment/{payment_id}/status', headers=headers_center, json={
        "status": "PAID",
        "transaction_ref": "TXN-E2E-998811",
        "mode": "DIRECT_BENEFIT_TRANSFER"
    })
    assert pay_res.status_code == 200
    assert pay_res.get_json()["data"]["status"] == "PAID"

    # 10. Farmer checks procurement & payment history
    history_res = client.get('/api/farmer/me/procurement-history', headers=headers_farmer)
    assert history_res.status_code == 200
    history_items = history_res.get_json()["data"]
    assert any(h["booking_id"] == booking_id and h["payment_status"] == "PAID" for h in history_items)

def test_ivr_booking_simulation_e2e(client):
    """
    Tests the simulated IVR telephone flow:
    Start call -> Select Language -> Select Crop -> Enter Quantity -> Confirm Booking
    """
    caller = "9826012345" # Ramesh Patel (pre-seeded farmer)

    # 1. Start Call
    call_start = client.post('/api/ivr/session/start', json={"caller_mobile": caller})
    assert call_start.status_code == 200
    session_id = call_start.get_json()["data"]["session_id"]

    # 2. Select Language (1 = Hindi)
    lang_res = client.post(f'/api/ivr/session/{session_id}/select-language', json={"digit": "1"})
    assert lang_res.status_code == 200
    assert lang_res.get_json()["data"]["next_step"] == "select-crop"

    # 3. Select Crop (1 = First eligible crop)
    crop_res = client.post(f'/api/ivr/session/{session_id}/select-crop', json={"digit": 1})
    assert crop_res.status_code == 200

    # 4. Enter Quantity (12 quintals)
    qty_res = client.post(f'/api/ivr/session/{session_id}/enter-quantity', json={"quantity": 12.0})
    assert qty_res.status_code == 200

    # 5. Confirm Booking
    confirm_res = client.post(f'/api/ivr/session/{session_id}/confirm-booking')
    assert confirm_res.status_code == 201
    ivr_booking = confirm_res.get_json()["data"]["booking"]
    assert ivr_booking["token_number"].startswith("TK-")
    assert ivr_booking["booking_method"] == "IVR"

def test_admin_portal_workflows(client):
    """
    Tests Administrator functionality: stats, center verification, crop catalog management
    """
    # 1. Login as Admin
    admin_login = client.post('/api/auth/admin/login', json={
        "username": "admin",
        "password": "AdminPassword@123"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.get_json()["data"]["token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 2. View Stats
    stats_res = client.get('/api/admin/stats', headers=headers_admin)
    assert stats_res.status_code == 200
    assert stats_res.get_json()["data"]["farmers"]["total"] >= 3

    # 3. Create a new Crop (e.g. Groundnut / Peanut)
    new_crop_res = client.post('/api/admin/crops', headers=headers_admin, json={
        "name": "Groundnut",
        "category": "Oilseeds",
        "rate_per_quintal": 6780.0,
        "time_to_unload_per_quintal_minutes": 5,
        "season": "Kharif"
    })
    assert new_crop_res.status_code == 201
    crop_id = new_crop_res.get_json()["data"]["crop_id"]

    # 4. Update Crop MSP rate
    update_crop_res = client.put(f'/api/admin/crops/{crop_id}', headers=headers_admin, json={
        "rate_per_quintal": 6850.0
    })
    assert update_crop_res.status_code == 200
    assert update_crop_res.get_json()["data"]["rate_per_quintal"] == 6850.0

    # 5. Review and Approve Pending Center (PC000003: mandi_east)
    verify_res = client.put('/api/admin/centers/PC000003/verify', headers=headers_admin, json={
        "action": "APPROVE"
    })
    assert verify_res.status_code == 200
    assert verify_res.get_json()["data"]["status"] == "ACTIVE"

    # 6. Capacity Utilization Report
    cap_res = client.get('/api/admin/reports/capacity-utilization', headers=headers_admin)
    assert cap_res.status_code == 200
    assert len(cap_res.get_json()["data"]) >= 3

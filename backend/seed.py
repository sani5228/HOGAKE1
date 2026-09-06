import os
import sys
from datetime import datetime, date, timedelta, timezone
from backend.database import SessionLocal, init_db, engine, Base
from backend.models.user import User, Farmer, ProcurementCenter, AdminUser
from backend.models.crop import Crop, FarmerCrop, CenterCrop, CenterDocument
from backend.models.booking import Booking, CenterDailySchedule
from backend.models.procurement import ProcurementRecord, Payment
from backend.models.notification import AuditLog, Notification
from backend.utils.security import hash_password, hash_aadhaar, mask_aadhaar

def seed_database():
    print("🌱 Starting FASAL database seeding...")
    init_db()
    db = SessionLocal()

    try:
        # Clear existing tables for clean idempotent seed
        db.query(Payment).delete()
        db.query(ProcurementRecord).delete()
        db.query(Booking).delete()
        db.query(CenterDailySchedule).delete()
        db.query(FarmerCrop).delete()
        db.query(CenterCrop).delete()
        db.query(CenterDocument).delete()
        db.query(Notification).delete()
        db.query(AuditLog).delete()
        db.query(Farmer).delete()
        db.query(ProcurementCenter).delete()
        db.query(AdminUser).delete()
        db.query(User).delete()
        db.query(Crop).delete()
        db.commit()

        # 1. Seed Admin User
        admin_auth = User(
            mobile_number="admin@fasal.gov.in",
            password_hash=hash_password("AdminPassword@123"),
            role="admin",
            created_at=datetime.now(timezone.utc)
        )
        db.add(admin_auth)
        db.flush()

        admin_profile = AdminUser(
            admin_id="AD001",
            user_id=admin_auth.user_id,
            username="admin",
            password_hash=hash_password("AdminPassword@123"),
            created_at=datetime.now(timezone.utc)
        )
        db.add(admin_profile)
        print("  ✓ Seeded Administrator (username: admin, pass: AdminPassword@123)")

        # 2. Seed Crops (Official MSP Rates)
        crops_data = [
            {"name": "Soybean", "category": "Oilseeds", "rate": 4600.00, "unload_min": 4, "season": "Kharif"},
            {"name": "Paddy / Rice", "category": "Cereals", "rate": 2183.00, "unload_min": 6, "season": "Kharif"},
            {"name": "Moong (Green Gram)", "category": "Pulses", "rate": 8558.00, "unload_min": 4, "season": "Kharif"},
            {"name": "Maize", "category": "Cereals", "rate": 2090.00, "unload_min": 5, "season": "Kharif"},
            {"name": "Cotton", "category": "Commercial", "rate": 6620.00, "unload_min": 7, "season": "Kharif"},
            {"name": "Wheat", "category": "Cereals", "rate": 2275.00, "unload_min": 5, "season": "Rabi"},
            {"name": "Gram / Chana", "category": "Pulses", "rate": 5440.00, "unload_min": 5, "season": "Rabi"},
            {"name": "Mustard", "category": "Oilseeds", "rate": 5650.00, "unload_min": 4, "season": "Rabi"},
        ]

        crop_map = {}
        for c in crops_data:
            crop = Crop(
                name=c["name"],
                category=c["category"],
                rate_per_quintal=c["rate"],
                time_to_unload_per_quintal_minutes=c["unload_min"],
                season=c["season"],
                status="ACTIVE",
                created_at=datetime.now(timezone.utc)
            )
            db.add(crop)
            db.flush()
            crop_map[c["name"]] = crop

        print(f"  ✓ Seeded {len(crop_map)} agricultural crops")

        # 3. Seed Procurement Centers
        centers_data = [
            {
                "id": "PC000001",
                "username": "mandi_north",
                "name": "APMC Mandi Central North",
                "contact": "9876543210",
                "state": "Madhya Pradesh",
                "district": "Indore",
                "village_town": "Sanwer Road",
                "status": "ACTIVE",
                "daily_cap": 420,
                "crops": ["Soybean", "Paddy / Rice", "Moong (Green Gram)", "Maize", "Wheat", "Gram / Chana", "Mustard"]
            },
            {
                "id": "PC000002",
                "username": "krishi_south",
                "name": "Kisan Samriddhi Kendra South",
                "contact": "9876543211",
                "state": "Madhya Pradesh",
                "district": "Ujjain",
                "village_town": "Barnagar Mandi",
                "status": "ACTIVE",
                "daily_cap": 420,
                "crops": ["Soybean", "Cotton", "Moong (Green Gram)", "Wheat", "Gram / Chana"]
            },
            {
                "id": "PC000003",
                "username": "mandi_east",
                "name": "Gramin Krishi Mandi East",
                "contact": "9876543212",
                "state": "Madhya Pradesh",
                "district": "Dewas",
                "village_town": "Sonkatch",
                "status": "PENDING_VERIFICATION",
                "daily_cap": 420,
                "crops": ["Soybean", "Paddy / Rice", "Wheat"]
            }
        ]

        center_map = {}
        for cd in centers_data:
            c_auth = User(
                mobile_number=cd["username"],
                password_hash=hash_password("CenterPassword@123"),
                role="center",
                created_at=datetime.now(timezone.utc)
            )
            db.add(c_auth)
            db.flush()

            center = ProcurementCenter(
                center_id=cd["id"],
                user_id=c_auth.user_id,
                name=cd["name"],
                contact_number=cd["contact"],
                state=cd["state"],
                district=cd["district"],
                village_town=cd["village_town"],
                daily_capacity_minutes=cd["daily_cap"],
                shift1_capacity_minutes=cd["daily_cap"] // 2,
                shift2_capacity_minutes=cd["daily_cap"] // 2,
                status=cd["status"],
                created_at=datetime.now(timezone.utc)
            )
            db.add(center)
            db.flush()
            center_map[cd["id"]] = center

            # Add accepted crops
            for c_name in cd["crops"]:
                if c_name in crop_map:
                    db.add(CenterCrop(center_id=center.center_id, crop_id=crop_map[c_name].crop_id))

            # Add document
            db.add(CenterDocument(
                center_id=center.center_id,
                document_type="Mandi Board Operating License",
                file_reference=f"documents/license_{center.center_id.lower()}.pdf",
                verified=(cd["status"] == "ACTIVE")
            ))

        print(f"  ✓ Seeded {len(center_map)} procurement centers (pass: CenterPassword@123)")

        # 4. Seed Farmers
        farmers_data = [
            {
                "id": "FA000101",
                "name": "Ramesh Chandra Patidar",
                "mobile": "9826012345",
                "aadhaar": "123456789012",
                "state": "Madhya Pradesh",
                "district": "Indore",
                "village_town": "Depalpur",
                "crops": ["Soybean", "Wheat", "Gram / Chana"]
            },
            {
                "id": "FA000102",
                "name": "Suresh Kumar Yadav",
                "mobile": "9826023456",
                "aadhaar": "234567890123",
                "state": "Madhya Pradesh",
                "district": "Ujjain",
                "village_town": "Ghatiya",
                "crops": ["Paddy / Rice", "Moong (Green Gram)", "Maize"]
            },
            {
                "id": "FA000103",
                "name": "Aditi Mishra",
                "mobile": "9826034567",
                "aadhaar": "345678901234",
                "state": "Madhya Pradesh",
                "district": "Indore",
                "village_town": "Rau",
                "crops": ["Soybean", "Cotton", "Wheat"]
            }
        ]

        farmer_map = {}
        for fd in farmers_data:
            f_auth = User(
                mobile_number=fd["mobile"],
                password_hash=hash_password("FarmerPassword@123"),
                role="farmer",
                created_at=datetime.now(timezone.utc)
            )
            db.add(f_auth)
            db.flush()

            farmer = Farmer(
                farmer_id=fd["id"],
                user_id=f_auth.user_id,
                name=fd["name"],
                mobile_number=fd["mobile"],
                aadhaar_encrypted=hash_aadhaar(fd["aadhaar"]),
                aadhaar_last4=mask_aadhaar(fd["aadhaar"]),
                state=fd["state"],
                district=fd["district"],
                village_town=fd["village_town"],
                status="ACTIVE",
                created_at=datetime.now(timezone.utc)
            )
            db.add(farmer)
            db.flush()
            farmer_map[fd["id"]] = farmer

            for c_name in fd["crops"]:
                if c_name in crop_map:
                    db.add(FarmerCrop(farmer_id=farmer.farmer_id, crop_id=crop_map[c_name].crop_id))

        print(f"  ✓ Seeded {len(farmer_map)} farmers (pass: FarmerPassword@123)")

        # 5. Seed Example Bookings & Capacity Ledgers
        today = date.today()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)

        # Booking 1: Past Completed Procurement for Farmer 1
        b1 = Booking(
            token_number=f"TK-{yesterday.strftime('%Y%m%d')}-0001",
            farmer_id="FA000101",
            crop_id=crop_map["Soybean"].crop_id,
            center_id="PC000001",
            expected_quantity_quintal=20.0,
            estimated_time_minutes=80,
            booking_timestamp=datetime.now(timezone.utc) - timedelta(days=3),
            assigned_date=yesterday,
            shift="SHIFT_1",
            start_time="09:00",
            end_time="10:20",
            status="COMPLETED",
            channel="WEB",
            created_at=datetime.now(timezone.utc) - timedelta(days=3)
        )
        db.add(b1)
        db.flush()

        # Procurement Record for Booking 1 (Actual weight 21.5 quintals)
        rate1 = float(crop_map["Soybean"].rate_per_quintal)
        amount1 = round(21.5 * rate1, 2)
        pr1 = ProcurementRecord(
            booking_id=b1.booking_id,
            farmer_id=b1.farmer_id,
            center_id=b1.center_id,
            crop_id=b1.crop_id,
            actual_weight_quintal=21.5,
            rate_per_quintal=rate1,
            total_amount=amount1,
            actual_procurement_time_minutes=75,
            procurement_date=yesterday,
            recorded_by="APMC Staff Officer",
            created_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.add(pr1)
        db.flush()

        # Payment for Booking 1 (Status: PAID)
        db.add(Payment(
            procurement_record_id=pr1.record_id,
            amount=amount1,
            status="PAID",
            payment_date=datetime.now(timezone.utc),
            mode="Direct Benefit Transfer (DBT)",
            transaction_ref=f"TXN-DBT-{yesterday.strftime('%Y%m%d')}-0001",
            created_at=datetime.now(timezone.utc) - timedelta(days=1)
        ))

        # Booking 2: Today's Booking - Arrived at Center 1
        b2 = Booking(
            token_number=f"TK-{today.strftime('%Y%m%d')}-0001",
            farmer_id="FA000102",
            crop_id=crop_map["Moong (Green Gram)"].crop_id,
            center_id="PC000001",
            expected_quantity_quintal=15.0,
            estimated_time_minutes=60,
            booking_timestamp=datetime.now(timezone.utc) - timedelta(days=2),
            assigned_date=today,
            shift="SHIFT_1",
            start_time="09:00",
            end_time="10:00",
            status="ARRIVED",
            channel="IVR",
            created_at=datetime.now(timezone.utc) - timedelta(days=2)
        )
        db.add(b2)

        # Booking 3: Tomorrow's Scheduled Booking for Farmer 3
        b3 = Booking(
            token_number=f"TK-{tomorrow.strftime('%Y%m%d')}-0001",
            farmer_id="FA000103",
            crop_id=crop_map["Soybean"].crop_id,
            center_id="PC000001",
            expected_quantity_quintal=25.0,
            estimated_time_minutes=100,
            booking_timestamp=datetime.now(timezone.utc) - timedelta(hours=12),
            assigned_date=tomorrow,
            shift="SHIFT_1",
            start_time="09:00",
            end_time="10:40",
            status="SCHEDULED",
            channel="WEB",
            created_at=datetime.now(timezone.utc) - timedelta(hours=12)
        )
        db.add(b3)

        # 6. Seed Center Daily Schedule Ledgers
        db.add(CenterDailySchedule(
            center_id="PC000001",
            schedule_date=today,
            shift="SHIFT_1",
            committed_minutes=60,
            capacity_minutes=210
        ))
        db.add(CenterDailySchedule(
            center_id="PC000001",
            schedule_date=tomorrow,
            shift="SHIFT_1",
            committed_minutes=100,
            capacity_minutes=210
        ))

        db.commit()
        print("  ✓ Seeded example bookings, procurement records, and capacity ledgers")
        print("🎉 Database seeding completed successfully!\n")

        print("=" * 60)
        print("DEMO CREDENTIALS SUMMARY (Local Prototype)")
        print("=" * 60)
        print("1. Administrator:")
        print("   Username: admin")
        print("   Password: AdminPassword@123")
        print("\n2. Procurement Centers:")
        print("   Center 1 (Indore):  mandi_north / CenterPassword@123")
        print("   Center 2 (Ujjain):  krishi_south / CenterPassword@123")
        print("   Center 3 (Pending): mandi_east   / CenterPassword@123")
        print("\n3. Farmers:")
        print("   Farmer 1 (Ramesh Chandra): Mobile: 9826012345 (or pass: FarmerPassword@123)")
        print("   Farmer 2 (Suresh Kumar):   Mobile: 9826023456 (or pass: FarmerPassword@123)")
        print("   Farmer 3 (Aditi Mishra):   Mobile: 9826034567 (or pass: FarmerPassword@123)")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise e
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()

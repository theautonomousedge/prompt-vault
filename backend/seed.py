"""Seed the database with sample data for development."""
from datetime import datetime, timezone, timedelta

from models import (
    User, Profile, Address, Transaction,
    UserType, DeliveryMethod, TransactionStatus,
    init_db, SessionLocal,
)
from auth import hash_password
from encryption import encrypt_value


def seed():
    init_db()
    db = SessionLocal()

    # Check if already seeded
    if db.query(User).first():
        print("Database already seeded. Skipping.")
        db.close()
        return

    # --- Admin User ---
    admin = User(
        id="admin-001",
        email="admin@promptvault.org",
        display_name="Admin",
        user_type=UserType.admin,
        password_hash=hash_password("admin1234"),
        is_verified=True,
    )
    db.add(admin)

    # --- Test Donor ---
    donor = User(
        id="donor-001",
        email="donor@test.com",
        display_name="Generous Gina",
        user_type=UserType.giver,
        password_hash=hash_password("donor1234"),
        is_verified=True,
    )
    db.add(donor)

    # --- 5 Sample Recipients ---
    recipients = [
        {
            "id": "recv-001",
            "email": "maria@test.com",
            "display_name": "Maria G.",
            "phone": "555-0101",
            "city": "Houston",
            "state": "TX",
            "story": "Single mom of three kids. Lost my job last month when the restaurant I worked at closed down. My kids are my world, and I just want to make sure they have warm meals every night. Any help means the world to us.",
            "street": "123 Oak Lane",
            "zip": "77001",
        },
        {
            "id": "recv-002",
            "email": "james@test.com",
            "display_name": "James W.",
            "phone": "555-0102",
            "city": "Detroit",
            "state": "MI",
            "story": "Retired veteran living on a fixed income. Medical bills have eaten into my food budget this winter. I served this country for 22 years, and I'm not too proud to ask neighbors for a hand when I need one.",
            "street": "456 Elm Street",
            "zip": "48201",
        },
        {
            "id": "recv-003",
            "email": "aisha@test.com",
            "display_name": "Aisha T.",
            "phone": "555-0103",
            "city": "Atlanta",
            "state": "GA",
            "story": "College student working two part-time jobs to pay tuition. Some weeks I have to choose between textbooks and groceries. A meal delivery would help me focus on my studies and building a better future.",
            "street": "789 Pine Road",
            "zip": "30301",
        },
        {
            "id": "recv-004",
            "email": "carlos@test.com",
            "display_name": "Carlos M.",
            "phone": "555-0104",
            "city": "Phoenix",
            "state": "AZ",
            "story": "Recently became the full-time caregiver for my elderly mother after her stroke. Had to quit my construction job. Between her medications and keeping the lights on, food has become a luxury. We are grateful for any kindness.",
            "street": "321 Desert View",
            "zip": "85001",
        },
        {
            "id": "recv-005",
            "email": "sarah@test.com",
            "display_name": "Sarah L.",
            "phone": "555-0105",
            "city": "Portland",
            "state": "OR",
            "story": "Recovering from surgery and unable to work for the next two months. My disability claim is still processing. A warm meal delivered to my door would be a blessing while I heal and get back on my feet.",
            "street": "654 Maple Ave",
            "zip": "97201",
        },
    ]

    for r in recipients:
        user = User(
            id=r["id"],
            email=r["email"],
            display_name=r["display_name"],
            phone=r["phone"],
            user_type=UserType.receiver,
            password_hash=hash_password("password123"),
            is_verified=True,
        )
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=r["id"],
            city=r["city"],
            state=r["state"],
            story=r["story"],
            is_public=True,
            is_verified=True,
        )
        db.add(profile)

        address = Address(
            user_id=r["id"],
            encrypted_street=encrypt_value(r["street"]),
            encrypted_zip=encrypt_value(r["zip"]),
            city=r["city"],
            state=r["state"],
        )
        db.add(address)

    db.commit()

    # --- Sample Transactions ---
    profiles = db.query(Profile).all()
    for i, profile in enumerate(profiles[:3]):
        txn = Transaction(
            giver_id="donor-001",
            receiver_id=profile.user_id,
            amount=25.00,
            tip_amount=3.00,
            delivery_method=DeliveryMethod.doordash,
            status=TransactionStatus.completed,
            message="Stay strong! Sending you a warm meal.",
            created_at=datetime.now(timezone.utc) - timedelta(days=i * 2),
        )
        db.add(txn)

    db.commit()
    db.close()
    print("Database seeded successfully!")
    print("  Admin:  admin@promptvault.org / admin1234")
    print("  Donor:  donor@test.com / donor1234")
    print("  Recipients: maria@test.com, james@test.com, etc. / password123")


if __name__ == "__main__":
    seed()

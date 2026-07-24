from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app.models import (
    User,
    UserProfile,
    Studio,
    Trainer,
    ClassCategory,
    FitnessClass,
    MembershipPass,
    PurchasedPass,
    Booking,
)

app = create_app()

def seed_database():
    with app.app_context():
        print(" Starting database seed...")

        # 1. Clean existing data (order matters to respect Foreign Keys)
        print("Cleaning old data...")
        Booking.query.delete()
        PurchasedPass.query.delete()
        MembershipPass.query.delete()
        FitnessClass.query.delete()
        ClassCategory.query.delete()
        Trainer.query.delete()
        Studio.query.delete()
        UserProfile.query.delete()
        User.query.delete()
        db.session.commit()

        # 2. Users & UserProfiles
        print("Seeding Users and Profiles...")
        
        # Admin
        admin = User(email="admin@fitpass.com", role="admin")
        admin.set_password("AdminPass123!")
        db.session.add(admin)
        db.session.flush()

        admin_profile = UserProfile(
            user_id=admin.id,
            full_name="System Admin",
            phone="555-0100",
            waiver_signed=True,
            waiver_signed_at=datetime.utcnow(),
        )
        db.session.add(admin_profile)

        # Trainers
        trainer_user1 = User(email="maya@fitpass.com", role="trainer")
        trainer_user1.set_password("TrainerPass123!")
        trainer_user2 = User(email="alex@fitpass.com", role="trainer")
        trainer_user2.set_password("TrainerPass123!")
        db.session.add_all([trainer_user1, trainer_user2])
        db.session.flush()

        trainer_prof1 = UserProfile(
            user_id=trainer_user1.id,
            full_name="Maya Lin",
            phone="555-0101",
            waiver_signed=True,
            waiver_signed_at=datetime.utcnow(),
        )
        trainer_prof2 = UserProfile(
            user_id=trainer_user2.id,
            full_name="Alex Rivera",
            phone="555-0102",
            waiver_signed=True,
            waiver_signed_at=datetime.utcnow(),
        )
        db.session.add_all([trainer_prof1, trainer_prof2])

        trainer1 = Trainer(
            user_id=trainer_user1.id,
            bio="10+ years teaching Vinyasa and Power Yoga with focus on alignment.",
            specialties="Vinyasa, Pilates Core",
        )
        trainer2 = Trainer(
            user_id=trainer_user2.id,
            bio="Former competitive athlete specializing in high-intensity conditioning.",
            specialties="HIIT, Strength, Boxing",
        )
        db.session.add_all([trainer1, trainer2])

        # Clients
        client1 = User(email="sarah@example.com", role="client")
        client1.set_password("ClientPass123!")
        client2 = User(email="david@example.com", role="client")
        client2.set_password("ClientPass123!")
        db.session.add_all([client1, client2])
        db.session.flush()

        client_prof1 = UserProfile(
            user_id=client1.id,
            full_name="Sarah Connor",
            phone="555-0199",
            waiver_signed=True,
            waiver_signed_at=datetime.utcnow() - timedelta(days=15),
            medical_clearance_notes="Mild asthma; carries inhaler.",
        )
        client_prof2 = UserProfile(
            user_id=client2.id,
            full_name="David Miller",
            phone="555-0198",
            waiver_signed=False, # Has not signed waiver yet
        )
        db.session.add_all([client_prof1, client_prof2])

        # 3. Studios
        print("Seeding Studios...")
        studio1 = Studio(
            name="Zen Flow Loft",
            location="123 Main St, Downtown",
            description="A calm, sunlit space built for yoga, meditation, and low-impact movement.",
        )
        studio2 = Studio(
            name="Iron Pulse Lab",
            location="456 Market Ave, Westside",
            description="High-energy facility packed with heavy turf, kettlebells, and heavy bags.",
        )
        db.session.add_all([studio1, studio2])

        # 4. Class Categories
        print("Seeding Class Categories...")
        cat_yoga = ClassCategory(name="Yoga")
        cat_hiit = ClassCategory(name="HIIT")
        cat_boxing = ClassCategory(name="Boxing")
        cat_pilates = ClassCategory(name="Pilates")
        db.session.add_all([cat_yoga, cat_hiit, cat_boxing, cat_pilates])
        db.session.flush()

        # 5. Fitness Classes
        print("Seeding Fitness Classes...")
        now = datetime.utcnow()
        
        class1 = FitnessClass(
            title="Sunrise Vinyasa",
            description="Start your day with dynamic flows and breathwork suitable for all levels.",
            capacity=15,
            start_time=now + timedelta(days=1, hours=2),
            end_time=now + timedelta(days=1, hours=3),
            studio_id=studio1.id,
            trainer_id=trainer1.id,
            category_id=cat_yoga.id,
        )
        
        class2 = FitnessClass(
            title="Full-Body Burn HIIT",
            description="Heart-pumping interval training using kettlebells, rowers, and bodyweight movements.",
            capacity=10,
            start_time=now + timedelta(days=2, hours=4),
            end_time=now + timedelta(days=2, hours=5),
            studio_id=studio2.id,
            trainer_id=trainer2.id,
            category_id=cat_hiit.id,
        )

        class3 = FitnessClass(
            title="Core & Reformer Pilates",
            description="Targeted deep-core work to improve posture, balance, and stability.",
            capacity=8,
            start_time=now - timedelta(days=2, hours=3), # Past class for completed review demo
            end_time=now - timedelta(days=2, hours=2),
            studio_id=studio1.id,
            trainer_id=trainer1.id,
            category_id=cat_pilates.id,
        )
        db.session.add_all([class1, class2, class3])

        # 6. Membership Passes
        print("Seeding Membership Passes...")
        pass_dropin = MembershipPass(
            name="Single Class Drop-In",
            credits=1,
            price=25.00,
            duration_days=30,
        )
        pass_10pack = MembershipPass(
            name="10-Class Flex Pass",
            credits=10,
            price=180.00,
            duration_days=90,
        )
        pass_monthly = MembershipPass(
            name="Monthly Unlimited",
            credits=99,
            price=150.00,
            duration_days=30,
        )
        db.session.add_all([pass_dropin, pass_10pack, pass_monthly])
        db.session.flush()

        # 7. Purchased Passes
        print("Seeding Purchased Passes...")
        user_pass1 = PurchasedPass(
            user_id=client1.id,
            pass_id=pass_10pack.id,
            remaining_credits=8,
            purchased_at=now - timedelta(days=10),
            expires_at=now + timedelta(days=80),
        )
        db.session.add(user_pass1)

        # 8. Bookings (Includes upcoming booking and a completed past booking with review)
        print("Seeding Bookings...")
        booking_upcoming = Booking(
            user_id=client1.id,
            class_id=class1.id,
            booked_at=now - timedelta(days=1),
            attended=False,
        )
        booking_past = Booking(
            user_id=client1.id,
            class_id=class3.id,
            booked_at=now - timedelta(days=5),
            attended=True,
            rating=5,
            review_text="Maya is an incredible instructor! Great cueing and music.",
        )
        db.session.add_all([booking_upcoming, booking_past])

        # Save all changes
        db.session.commit()
        print(" Database successfully seeded!")

if __name__ == "__main__":
    seed_database()
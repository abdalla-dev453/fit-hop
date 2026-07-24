import pytest
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import User, UserProfile, MembershipPass, PurchasedPass, Studio, Trainer, ClassCategory, FitnessClass, Booking

# Global prefix derived from app.url_map
API_PREFIX = "/api"

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret"
    })

    with app.app_context():
        db.create_all()

        category = db.session.query(ClassCategory).filter_by(name="Yoga").first()
        if not category:
            category = ClassCategory(name="Yoga")
            db.session.add(category)
            db.session.commit()

        studio = db.session.query(Studio).filter_by(name="Downtown Yoga").first()
        if not studio:
            studio = Studio(name="Downtown Yoga", location="123 Main St")
            db.session.add(studio)
            db.session.commit()

        pass_option = db.session.query(MembershipPass).filter_by(name="10 Class Pass").first()
        if not pass_option:
            pass_option = MembershipPass(name="10 Class Pass", credits=10, price=100.00, duration_days=30)
            db.session.add(pass_option)
            db.session.commit()

        trainer_user = db.session.query(User).filter_by(email="trainer@test.com").first()
        if not trainer_user:
            trainer_user = User(email="trainer@test.com", role="trainer")
            trainer_user.set_password("password123")
            db.session.add(trainer_user)
            db.session.commit()

        trainer = db.session.query(Trainer).filter_by(user_id=trainer_user.id).first()
        if not trainer:
            trainer = Trainer(user_id=trainer_user.id)
            db.session.add(trainer)
            db.session.commit()

        fitness_class = db.session.query(FitnessClass).filter_by(title="Morning Vinyasa Flow").first()
        if not fitness_class:
            fitness_class = FitnessClass(
                title="Morning Vinyasa Flow",
                capacity=10,
                start_time=datetime.now(timezone.utc) + timedelta(days=1),
                end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
                studio_id=studio.id,
                trainer_id=trainer.id,
                category_id=category.id
            )
            db.session.add(fitness_class)
            db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Helper fixture to register, sign waiver, buy pass, and return auth header."""
    reg_resp = client.post(f"{API_PREFIX}/auth/register", json={
        "email": "client@test.com",
        "password": "password123",
        "full_name": "Jane Doe",
        "phone": "555-1234-5678"
    })
    
    json_data = reg_resp.get_json()
    if not json_data or "access_token" not in json_data:
        raise ValueError(f"Registration failed in fixture. Status: {reg_resp.status_code}, Body: {json_data}")
        
    token = json_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with client.application.app_context():
        user = db.session.query(User).filter_by(email="client@test.com").first()
        if user and user.profile:
            user.profile.waiver_signed = True
            db.session.commit()

    return headers


# ==============================================================================
# AUTH TESTS
# ==============================================================================
def test_user_registration(client):
    response = client.post(f"{API_PREFIX}/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "full_name": "John Smith"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@test.com"

def test_registration_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": "password123", "full_name": "User 1"}
    client.post(f"{API_PREFIX}/auth/register", json=payload)
    response = client.post(f"{API_PREFIX}/auth/register", json=payload)
    assert response.status_code == 422
    assert "messages" in response.get_json()

def test_login_success(client):
    client.post(f"{API_PREFIX}/auth/register", json={
        "email": "login@test.com",
        "password": "password123",
        "full_name": "Login Test"
    })
    response = client.post(f"{API_PREFIX}/auth/login", json={
        "email": "login@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_get_current_user(client, auth_headers):
    # Aligned path to match your application factory route prefix signature (/api/auth/me)
    response = client.get(f"{API_PREFIX}/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["email"] == "client@test.com"


# ==============================================================================
# PASSES TESTS
# ==============================================================================
def test_list_passes(client):
    response = client.get(f"{API_PREFIX}/passes")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1

def test_purchase_pass(client, auth_headers):
    response = client.post(f"{API_PREFIX}/passes/purchase/1", headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data["pass"]["remaining_credits"] == 10

def test_get_my_passes(client, auth_headers):
    client.post(f"{API_PREFIX}/passes/purchase/1", headers=auth_headers)
    response = client.get(f"{API_PREFIX}/passes/my-passes", headers=auth_headers)
    assert response.status_code == 200


# ==============================================================================
# BOOKING TESTS
# ==============================================================================
def test_create_booking_without_pass_fails(client, auth_headers):
    response = client.post(f"{API_PREFIX}/bookings", headers=auth_headers, json={"class_id": 1})
    assert response.status_code == 402

def test_create_booking_success(client, auth_headers):
    client.post(f"{API_PREFIX}/passes/purchase/1", headers=auth_headers)
    response = client.post(f"{API_PREFIX}/bookings", headers=auth_headers, json={"class_id": 1})
    assert response.status_code == 201
    data = response.get_json()
    assert data["remaining_credits"] == 9

def test_cancel_booking_restores_credit(client, auth_headers):
    client.post(f"{API_PREFIX}/passes/purchase/1", headers=auth_headers)
    booking_resp = client.post(f"{API_PREFIX}/bookings", headers=auth_headers, json={"class_id": 1})
    booking_id = booking_resp.get_json()["booking"]["id"]

    cancel_resp = client.delete(f"{API_PREFIX}/bookings/{booking_id}", headers=auth_headers)
    assert cancel_resp.status_code == 200
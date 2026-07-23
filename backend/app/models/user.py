from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client") # "client", "trainer", "admin"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    purchased_passes = db.relationship("PurchasedPass", back_populates="user")
    bookings = db.relationship("Booking", back_populates="user")
    trainer = db.relationship("Trainer", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fitness_classes = db.relationship("FitnessClass", uselist=False, back_populates="user", lazy="dynamic")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
from datetime import datetime
from app.extensions import db

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("fitness_classes.id"), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Combined attendance & review fields
    attended = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Integer) # 1-5 rating scale
    review_text = db.Column(db.Text)

    # Relationships
    fitness_class = db.relationship("FitnessClass", back_populates="bookings")
    user = db.relationship("User", back_populates="bookings")

    def __repr__(self):
        return f"<Booking {self.id}>"
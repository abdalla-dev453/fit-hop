from app.extensions import db

class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    waiver_signed = db.Column(db.Boolean, default=False, nullable=False)
    waiver_signed_at = db.Column(db.DateTime)
    medical_clearance_notes = db.Column(db.Text)

    user = db.relationship("User", back_populates="profile")

    
    def __repr__(self):
        return f"<UserProfile {self.full_name}>"
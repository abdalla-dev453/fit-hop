from app.extensions import db

class MembershipPass(db.Model):
    __tablename__ = "membership_passes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False) # e.g. "10-Class Pack", "Monthly Unlimited"
    credits = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False) # valid for X days

    # Relationships
    purchased_passes = db.relationship("PurchasedPass", back_populates="pass")

    def __repr__(self):
        return f"<MembershipPass {self.name}>"
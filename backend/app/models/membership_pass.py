from app.extensions import db

class MembershipPass(db.Model):
    __tablename__ = "membership_passes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    purchased_instances = db.relationship("PurchasedPass", back_populates="membership_pass", lazy="dynamic")

    
    def __repr__(self):
        return f"<MembershipPass {self.name}>"
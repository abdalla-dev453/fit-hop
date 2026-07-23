from datetime import datetime
from app.extensions import db

class PurchasedPass(db.Model):
    __tablename__ = "purchased_passes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pass_id = db.Column(db.Integer, db.ForeignKey("membership_passes.id"), nullable=False)

    remaining_credits = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="purchased_passes")
    membership_pass = db.relationship("MembershipPass", back_populates="purchased_instances")

    
    def __repr__(self):
        return f"<PurchasedPass id={self.id} user_id={self.user_id} pass_id={self.pass_id} remaining_credits={self.remaining_credits} expires_at={self.expires_at}>"
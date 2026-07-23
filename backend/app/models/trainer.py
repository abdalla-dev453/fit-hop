from app.extensions import db

class Trainer(db.Model):
    __tablename__ = "trainers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True)
    bio = db.Column(db.Text)
    specialties = db.Column(db.String(255))

    user = db.relationship("User", back_populates="trainer_profile")
    classes = db.relationship("FitnessClass", back_populates="trainer", lazy="dynamic")

    
    def __repr__(self):
        return f"<Trainer {self.id}>"
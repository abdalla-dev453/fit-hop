from app.extensions import db

class FitnessClass(db.Model):
    __tablename__ = "fitness_classes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    studio_id = db.Column(db.Integer, db.ForeignKey("studios.id"), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainers.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("class_categories.id"), nullable=False)

    bookings = db.relationship("Booking", back_populates="fitness_class", lazy="dynamic")
    studio = db.relationship("Studio", back_populates="classes")
    trainer = db.relationship("Trainer", back_populates="classes")
    category = db.relationship("ClassCategory", back_populates="classes")
    user = db.relationship("User", back_populates="fitness_classes")

    def __repr__(self):
        return f"<FitnessClass {self.title}>"
from app.extensions import db

class ClassCategory(db.Model):
    __tablename__ = "class_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # e.g., Yoga, HIIT, Boxing
    
    classes = db.relationship("FitnessClass", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<ClassCategory {self.name}>"
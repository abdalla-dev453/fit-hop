import re
from marshmallow import fields, validate, validates, validates_schema, ValidationError
from app.extensions import ma, db  # Import db from extensions cleanly
from app.models import (
    User,
    UserProfile,
    Studio,
    Trainer,
    ClassCategory,
    FitnessClass,
    MembershipPass,
    PurchasedPass,
    Booking,
)

# ----- User & Profile Schemas -----
class UserProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile
        load_instance = True
        include_fk = True

    full_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.String(validate=validate.Length(min=10, max=20))

class UserRegistrationSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8, max=100))
    role = fields.String(validate=validate.OneOf(["client", "trainer", "admin"]), load_default="client")
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    phone = fields.String(validate=validate.Length(min=10, max=20))

    @validates("email")
    def validate_email_unique(self, value, **kwargs):
        # Query via the session directly to be safer with application contexts
        user_exists = db.session.query(User).filter(User.email == value).first()
        if user_exists:
            raise ValidationError("Email already registered.")


class UserLoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class UserResponseSchema(ma.SQLAlchemyAutoSchema):
    profile = fields.Nested(UserProfileSchema, dump_only=True)
    class Meta:
        model = User
        load_instance = True
        exclude = ("password_hash",)


# ----- Studios & Trainer Schemas -----
class StudioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Studio
        load_instance = True

    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    location = fields.String(required=True, validate=validate.Length(min=5, max=255))

class TrainerSchema(ma.SQLAlchemyAutoSchema):
    user_name = fields.Method("get_user_name", dump_only=True)

    class Meta:
        model = Trainer
        load_instance = True
        include_fk = True

    def get_user_name(self, obj):
        if obj.user and obj.user.profile:
            return obj.user.profile.full_name
        return "Unknown Trainer"


# ----- Fitness Class & Category Schemas -----
class ClassCategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ClassCategory
        load_instance = True


class FitnessClassSchema(ma.SQLAlchemyAutoSchema):
    studio_name = fields.String(attribute="studio.name", dump_only=True)
    trainer_name = fields.String(attribute="trainer.user.profile.full_name", dump_only=True)
    category_name = fields.String(attribute="category.name", dump_only=True)

    class Meta:
        model = FitnessClass
        load_instance = True
        include_fk = True

    title = fields.String(required=True, validate=validate.Length(min=2, max=100))
    capacity = fields.Integer(required=True, validate=validate.Range(min=1))

    # Ensuring start time is before end time
    @validates_schema
    def validate_times(self, data, **kwargs):
        start = data.get("start_time")
        end = data.get("end_time")
        if start and end and end <= start:
            raise ValidationError({"end_time": "End time must be after start time."})


# ----- Pass Schemas -----
class MembershipPassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MembershipPass
        load_instance = True

    name = fields.String(required=True, validate=validate.Length(min=2, max=80))
    credits = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    duration_days = fields.Integer(required=True, validate=validate.Range(min=1))

class PurchasedPassSchema(ma.SQLAlchemyAutoSchema):
    pass_name = fields.String(attribute="membership_pass.name", dump_only=True)
    class Meta:
        model = PurchasedPass
        load_instance = True
        include_fk = True


# ----- Booking Schemas -----
class BookingCreateSchema(ma.Schema):
    class_id = fields.Integer(required=True)

    @validates("class_id")
    def validate_class_exists(self, value, **kwargs):
        fitness_class = FitnessClass.query.get(value)
        if not fitness_class:
            raise ValidationError("Class not found.")
        current_bookings_count = db.session.query(Booking).filter(Booking.class_id == value).count()
        if current_bookings_count >= fitness_class.capacity:
            raise ValidationError("Class is fully booked.")
        return value


class BookingReviewSchema(ma.Schema):
    rating = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    review_text = fields.String(validate=validate.Length(max=1000))


class BookingResponseSchema(ma.SQLAlchemyAutoSchema):
    class_title = fields.String(attribute="fitness_class.title", dump_only=True)
    start_time = fields.DateTime(attribute="fitness_class.start_time", dump_only=True)
    studio_name = fields.String(attribute="fitness_class.studio.name", dump_only=True)

    class Meta:
        model = Booking
        load_instance = True
        include_fk = True
from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.app.models import fitness_class
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Booking, FitnessClass, PurchasedPass, UserProfile
from app.schemas import BookingCreateSchema, BookingReviewSchema, BookingResponseSchema

bookings_bp = Blueprint("bookings", __name__)

booking_schema = BookingResponseSchema()
bookings_schema = BookingResponseSchema(many=True)
create_schema = BookingCreateSchema()
review_schema = BookingReviewSchema()


# Handles booking creation, cancellation, and review submission

# --------endpoint to create a new booking-----------
@bookings_bp.route("", methods=["POST"])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    json_data = request.get_json() or {}
    data = create_schema.load(json_data)

    class_id = data["class_id"]
    fitness_class = FitnessClass.query.get_or_404(class_id)

    # check if a user has already booked the class
    existing_booking = Booking.query.filter_by(user_id=user_id, class_id=class_id).first()
    if existing_booking:
        return jsonify({"error": "You have already booked this class"}), 400

    # check signed waiver requirements
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.waiver_signed:
        return jsonify({"error": "You must sign the liability waiver to book a class"}), 403

    # find an active pass with remaining credits
    now = datetime.utcnow()
    active_pass = PurchasedPass.query.filter(
        PurchasedPass.user_id == user_id,
        PurchasedPass.remaining_credits > 0,
        PurchasedPass.expires_at > now,
    ).order_by(PurchasedPass.expires_at.asc()).first()

    if not active_pass:
        return jsonify({"error": "No valid pass with available credits found. PLease purchase a pass to book a class"}), 402

    # Deduct credit & record booking
    active_pass.remaining_credits -= 1
    booking = Booking(user_id=user_id, class_id=class_id)

    db.session.add(booking)
    db.session.commit()
    return jsonify({
        "message": "Class booked successfully",
        "booking": booking_schema.dump(booking)
        "remaining_credits": active_pass.remaining_credits
    }), 201



# --------endpoint to get a user's bookings-----------
@bookings_bp.route("", methods=["GET"])
@jwt_required()
def get_user_bookings():
    user_id = get_jwt_identity()
    user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booked_at.desc()).all()
    return jsonify(bookings_schema.dump(user_bookings)), 200


# --------endpoint to cancel a booking-----------
@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def cancel_booking(booking_id):
    user_id  = get_jwt_identity()
    booking =  Booking.query.filter_by(id=booking_id, user_id=user_id).first_or_404()

    # REfund 1 credit if class hasn't started yet
    if booking.fitness_class.start_time > datetime.utcnow():
        active_pass = PurchasedPass.query.filter_by(user_id=user_id).order_by(PurchasedPass.expires_at.desc()).first()
        if active_pass:
            active_pass.remaining_credits += 1

    db.session.delete(booking)
    db.session.commit()
    return jsonify({"message": "Booking cancelled successfully and credits restored"}), 200



# --------endpoint to submit a review for a booking-----------
@bookings_bp.route("/<int:booking_id>/review", methods=["POST"])
@jwt_required()
def review_booking(booking_id):
    user_id = get_jwt_identity()
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first_or_404()

    if booking.fitness_class.start_time > datetime.utcnow():
        return jsonify({"error": "Class has not started yet"}), 400

    json_data = request.get_json() or {}
    data = review_schema.load(json_data)

    booking.rating = data["rating"]
    booking.review_text = data.get("review_text")
    booking.attended = True

    db.session.commit()
    return jsonify({
        "message": "Review submitted successfully",
        "booking": booking_schema.dump(booking)
        }), 200
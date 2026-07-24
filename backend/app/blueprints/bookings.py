from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models import Booking, FitnessClass, PurchasedPass, UserProfile
from app.schemas import BookingCreateSchema, BookingReviewSchema, BookingResponseSchema

bookings_bp = Blueprint("bookings", __name__)

booking_schema = BookingResponseSchema()
bookings_schema = BookingResponseSchema(many=True)
create_schema = BookingCreateSchema()  
review_schema = BookingReviewSchema()


# ==========================================
# 1. CREATE A NEW BOOKING
# ==========================================
@bookings_bp.route("", methods=["POST"])
@jwt_required()
def create_booking():
    user_id = int(get_jwt_identity())
    json_data = request.get_json() or {}
    
    # Gracefully capture malformed payload inputs
    try:
        data = create_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 422

    class_id = data["class_id"]
    # get fitness class
    fitness_class = db.session.get(FitnessClass, class_id)
    if not fitness_class:
        return jsonify({"error": "Fitness class not found"}), 404

    # Check if user has already booked this exact class profile
    existing_booking = db.session.query(Booking).filter_by(user_id=user_id, class_id=class_id).first()
    if existing_booking:
        return jsonify({"error": "You have already booked this class"}), 400

    # Verify matching tracking profiles for liability release requirements
    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    if not profile or not getattr(profile, 'waiver_signed', False):
        return jsonify({"error": "You must sign the liability waiver to book a class"}), 403

    # Safely query active pass availability
    now = datetime.now(timezone.utc)
    active_pass = db.session.query(PurchasedPass).filter(
        PurchasedPass.user_id == user_id,
        PurchasedPass.remaining_credits > 0,
        PurchasedPass.expires_at > now
    ).order_by(PurchasedPass.expires_at.asc()).first()

    if not active_pass:
        return jsonify({"error": "No valid pass with available credits found. Please purchase a pass to book a class"}), 402

    try:
        # Atomically alter data frames and records inside one single block
        active_pass.remaining_credits -= 1
        booking = Booking(user_id=user_id, class_id=class_id)

        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            "message": "Class booked successfully",
            "booking": booking_schema.dump(booking),
            "remaining_credits": active_pass.remaining_credits
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal system failure interrupted your booking process."}), 500


# ==========================================
# 2. GET CURRENT USER BOOKINGS
# ==========================================
@bookings_bp.route("", methods=["GET"])
@jwt_required()
def get_user_bookings():
    user_id = int(get_jwt_identity())
    user_bookings = db.session.query(Booking).filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    return jsonify(bookings_schema.dump(user_bookings)), 200


# ==========================================
# 3. CANCEL A BOOKING
# ==========================================
@bookings_bp.route("/<int:booking_id>", methods=["DELETE"])
@jwt_required()
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())
    
    booking = db.session.query(Booking).filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        return jsonify({"error": "Booking resource not found"}), 404

    try:
        # Safely refund 1 credit if session hasn't started yet
        # Ensuring models compare naive datetimes accurately or use uniform UTC layers
        if booking.fitness_class.start_time.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            active_pass = db.session.query(PurchasedPass).filter_by(user_id=user_id).order_by(PurchasedPass.expires_at.desc()).first()
            if active_pass:
                active_pass.remaining_credits += 1

        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking cancelled successfully and credits restored"}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An issue occurred while canceling the booking."}), 500


# ==========================================
# 4. SUBMIT A CLASS REVIEW
# ==========================================
@bookings_bp.route("/<int:booking_id>/review", methods=["POST"])
@jwt_required()
def review_booking(booking_id):
    user_id = int(get_jwt_identity())
    
    booking = db.session.query(Booking).filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        return jsonify({"error": "Booking resource not found"}), 404

    if booking.fitness_class.start_time.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
        return jsonify({"error": "Class has not started yet. You cannot evaluate a future session."}), 400

    json_data = request.get_json() or {}
    try:
        data = review_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 422

    try:
        booking.rating = data["rating"]
        booking.review_text = data.get("review_text")
        booking.attended = True

        db.session.commit()
        return jsonify({
            "message": "Review submitted successfully",
            "booking": booking_schema.dump(booking)
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An issue occurred while processing your review details."}), 500
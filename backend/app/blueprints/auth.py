from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models import User, UserProfile
from app.schemas import UserResponseSchema, UserProfileSchema, UserRegistrationSchema, UserLoginSchema

auth_bp = Blueprint("auth", __name__)

# Instantiated schemas
user_schema = UserResponseSchema()
register_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()
profile_schema = UserProfileSchema()

# ==========================================
# 1. USER REGISTRATION
# ==========================================
@auth_bp.route("/register", methods=["POST"])
def register():
    json_data = request.get_json() or {}
    
    try:
        data = register_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 422

    try:
        user = User(email=data["email"], role=data.get("role", "client"))
        user.set_password(data["password"])

        db.session.add(user)
        db.session.flush()  # Allocates user.id sequentially without completing transaction

        #  profile payload securely
        profile = UserProfile(
            user_id=user.id,
            full_name=data["full_name"],
            phone=data.get("phone", None)
        )
        db.session.add(profile)
        db.session.commit()

        # JWT token payload 
        token = create_access_token(identity=str(user.id))
        return jsonify({
            "message": "User registered successfully",
            "access_token": token,
            "user": user_schema.dump(user)
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal error occurred while setting up your account."}), 500


# ==========================================
# 2. USER LOGIN
# ==========================================
@auth_bp.route("/login", methods=["POST"])
def login():
    json_data = request.get_json() or {}
    
    # Intercept bad login payloads (e.g. completely missing password field)
    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": "Validation failed", "messages": err.messages}), 422

    # Query target user records via session filters
    user = db.session.query(User).filter_by(email=data["email"]).first()
    
    # Generic messaging wrapper to prevent email enumeration attacks
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "message": "User logged in successfully",
        "user": user_schema.dump(user)
    }), 200


# ==========================================
# 3. GET PROFILE DATA
# ==========================================
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id))
    if not user:
        return jsonify({"error": "User account no longer exists."}), 404
        
    return jsonify(user_schema.dump(user)), 200
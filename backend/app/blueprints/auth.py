from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models import User, UserProfile
from app.schemas import UserResponseSchema, UserProfileSchema, UserRegistrationSchema, UserLoginSchema

auth_bp = Blueprint("auth", __name__)

# schemas
user_schema = UserResponseSchema()
register_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()
profile_schema = UserProfileSchema()

# Handles user registration, login, and profile management

# Register a new user
@auth_bp.route("/register", methods=["POST"])
def register():
    json_data = request.get_json() or {}
    data = register_schema.load(json_data)

    user = User(email=data["email"], role=data.get["role", "client"])
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()

    profile = UserProfile(
        user_id=user.id,
        full_name=data["full_name"],
        phone=data.get("phone", None)
    )
    db.session.add(profile)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "User registered successfully",
        "access_token": token,
        "user": user_schema.dump(user)
    }), 201


# LOgin a user
# TODO: Add email verification
@auth_bp.route("/login", methods=["POST"])
def login():
    json_data = request.get_json() or {}
    data = login_schema.load(json_data)

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": token,
        "user": user_schema.dump(user)
    }), 200


# Get user profile
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(user_schema.dump(user)), 200
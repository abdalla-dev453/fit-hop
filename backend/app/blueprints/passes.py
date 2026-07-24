from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from backend.app.models import membership_pass, purchased_pass
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import MembershipPass, PurchasedPass
from app.schemas import MembershipPassSchema, PurchasedPassSchema
from app.extensions import db

passes_bp = Blueprint("passes", __name__)

pass_schema = MembershipPassSchema()
passes_schema = MembershipPassSchema(many=True)
purchased_pass_schema = PurchasedPassSchema()
purchased_passes_schema = PurchasedPassSchema(many=True)

# Handles browsing available pass options, purchasing passes, and inspecting the user's active pass balances

# endpoint to get all available passes
@passes_bp.route("/", methods=["GET"])
def list_available_passes():
    """
    Lists all available passes
    """
    passes = MembershipPass.query.all()
    return jsonify(passes_schema.dump(passes)), 200

# endpoint to get a pass
@passes_bp.route("/my-passes", methods=["GET"])
@jwt_required()
def get_my_passes():
    """LIst active and expired passes for the logged-in user"""
    user_id = get_jwt_identity()
    passes = PurchasedPass.query.filter_by(user_id=user_id).order_by(PurchasedPass.purchased_at.desc()).all()
    return jsonify(purchased_passes_schema.dump(passes)), 200

# endpoint to purchase a pass
@passes_bp.route("/purchase/<int:pass_id>", methods=["POST"])
@jwt_required()
def purchase_pass(pass_id):
    """Purchase a membership pass package"""
    user_id = get_jwt_identity()
    membership_pass = MembershipPass.query.get_or_404(pass_id)  

    expire_at = datetime.utcnow() + timedelta(days=membership_pass.duration_days)

    purchased = PurchasedPass(
        user_id=user_id,
        pass_id=membership_pass.id,
        remaining_credits=membership_pass.credits,
        expires_at=expire_at,
    )

    db.session.add(purchased)
    db.session.commit()
    return jsonify({
    "message": f"Successfully purchased {membership_pass.name}",
    "pass": purchased_pass_schema.dump(purchased)
    }), 201

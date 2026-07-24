from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import MembershipPass, PurchasedPass
from app.schemas import MembershipPassSchema, PurchasedPassSchema

passes_bp = Blueprint("passes", __name__)

pass_schema = MembershipPassSchema()
passes_schema = MembershipPassSchema(many=True)
purchased_pass_schema = PurchasedPassSchema()
purchased_passes_schema = PurchasedPassSchema(many=True)

# ==========================================
# 1. LIST ALL AVAILABLE MEMBERSHIP PASSES
# ==========================================
@passes_bp.route("", methods=["GET"])
def list_available_passes():
    """List all available pass options for purchase."""
    passes = db.session.query(MembershipPass).all()
    return jsonify(passes_schema.dump(passes)), 200


# ==========================================
# 2. GET CURRENT LOGGED-IN USER'S PASSES
# ==========================================
@passes_bp.route("/my-passes", methods=["GET"])
@jwt_required()
def get_my_passes():
    """List active and expired passes for the logged-in user."""
    user_id = int(get_jwt_identity())
    
    passes = db.session.query(PurchasedPass).filter_by(user_id=user_id).order_by(PurchasedPass.purchased_at.desc()).all()
    return jsonify(purchased_passes_schema.dump(passes)), 200


# ==========================================
# 3. PURCHASE A PASS PACKAGE
# ==========================================
@passes_bp.route("/purchase/<int:pass_id>", methods=["POST"])
@jwt_required()
def purchase_pass(pass_id):
    """Purchase a membership pass package."""
    user_id = int(get_jwt_identity())
    
    membership_pass = db.session.get(MembershipPass, pass_id)
    if not membership_pass:
        return jsonify({"error": "Membership pass option not found"}), 404

    expires_at = datetime.now(timezone.utc) + timedelta(days=membership_pass.duration_days)

    try:
        purchased = PurchasedPass(
            user_id=user_id,
            pass_id=membership_pass.id,
            remaining_credits=membership_pass.credits,
            expires_at=expires_at
        )

        db.session.add(purchased)
        db.session.commit()

        return jsonify({
            "message": f"Successfully purchased {membership_pass.name}",
            "pass": purchased_pass_schema.dump(purchased)
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "An error occurred while processing your pass purchase transaction."}), 500
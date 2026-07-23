from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/health", methods=["GET"])
def health_check():
    return {"status": "auth blueprint active"}, 200
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from app.extensions import db
from app.models import User

# ==========================================
# 1. OPTIMIZED ADMIN REQUIRED DECORATOR
# ==========================================
def admin_required():
    """Optimized admin validation that reads custom claims directly from the 
    cryptographic JWT payload, avoiding redundant database lookups.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure JWT is valid and present
            verify_jwt_in_request()
            
            # Fetch custom claims payload directly out of the incoming JWT token
            claims = get_jwt()
            
            # Look for a pre-embedded role verification statement
            if claims.get("role") == "admin":
                return fn(*args, **kwargs)
                
            # Database fallback ONLY if custom claims aren't fully configured yet
            from flask_jwt_extended import get_jwt_identity
            current_user_id = get_jwt_identity()
            user = db.session.get(User, int(current_user_id))
            
            if not user or user.role != "admin":
                return jsonify({"error": "Admin privileges required. Access denied."}), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ==========================================
# 2. SCHEMA-AWARE PAGINATION UTILITY
# ==========================================
def paginate(query, schema=None, page_param="page", per_page_param="per_page"):
    """Paginates an active SQLAlchemy query object safely, utilizing 
    Marshmallow schemas for uniform production serialization.
    """
    # Dynamically extract tracking variables safely out of request query arguments
    try:
        page = int(request.args.get(page_param, 1))
        per_page = int(request.args.get(per_page_param, 10))
    except ValueError:
        page, per_page = 1, 10

    # Execute safe ORM data slicing boundaries
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Process items serialization via schema engine or native fallbacks
    if schema:
        serialized_items = schema.dump(paginated.items)
    else:
        serialized_items = [
            item.to_dict() if hasattr(item, "to_dict") else item 
            for item in paginated.items
        ]

    return {
        "items": serialized_items,
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "per_page": paginated.per_page,
    }
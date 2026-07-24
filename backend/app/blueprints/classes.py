from operator import or_

from flask import Blueprint, request, jsonify
from datetime import datetime
from sqlalchemy import or_
from app.models import FitnessClass, ClassCategory
from app.schemas import FitnessClassSchema, ClassCategorySchema

classes_bp = Blueprint("classes", __name__)

class_detail_schema = FitnessClassSchema()
classes_detail_schema = FitnessClassSchema(many=True)
categories_schema = ClassCategorySchema()


@classes_bp.route("", methods=["GET"])
def get_classes():
    """Search and filter fitness classes. Query parameters:- studio_id: int
    - category_id: int
    - trainer_id: int
    - start_date: ISO date string (YYYY-MM-DD)
    - end_date: ISO date string (YYYY-MM-DD)
    - q: string (searches in class title or description)
    - available_only: true/false (only classes with open spots)
      """
    query = FitnessClass.query

    # Date range filtering (defaults to upcoming classes from now)
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    if start_date_str:
        try:
            start_date = datetime.fromisoformat(start_date_str)
            query = query.filter(FitnessClass.start_time >= start_date)
        except ValueError:
            return jsonify({"error": "Invalid start date format, Use YYYY-MM-DD"}), 400
    else:
        # Default: show future classes by default
        query = query.filter(FitnessClass.start_time >= datetime.now())

    if end_date_str:
        try:
            end_date = datetime.fromisoformat(end_date_str)
            query = query.filter(FitnessClass.start_time <= end_date)
        except ValueError:
            return jsonify({"error": "Invalid end date format, Use YYYY-MM-DD"}), 400

    # Studio filtering
    studio_id = request.args.get("studio_id", type=int)
    if studio_id:
        query = query.filter(FitnessClass.studio_id == studio_id)

    # Category filtering
    category_id = request.args.get("category_id", type=int)
    if category_id:
        query = query.filter(FitnessClass.category_id == category_id)

    # trainer filtering
    trainer_id = request.args.get("trainer_id", type=int)
    if trainer_id:
        query = query.filter(FitnessClass.trainer_id == trainer_id)

    # Search filtering
    search_query = request.args.get("q", type=str)
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            or_(
                FitnessClass.title.ilike(search),
                FitnessClass.description.ilike(search),
            )
        )

    # order by nearest class first
    classes = query.order_by(FitnessClass.start_time.asc()).all()

    # Available only filtering
    available_only = request.args.get("available_only", "").lower() == "true"
    if available_only:
        classes = [c for c in classes if c.capacity - c.bookings.count() > 0]
    return jsonify(
        classes_detail_schema.dump(classes)
    ), 200


@classes_bp.route("/<int:class_id>", methods=["GET"])
def get_class_details(class_id):
    """Get details for a single fitness class with remaining spots."""
    fitness_class = FitnessClass.query.get_or_404(class_id)
    return jsonify(class_detail_schema.dump(fitness_class)), 200


@classes_bp.route("/categories", methods=["GET"])
def get_categories():
    """List all fitness class categories (Yoga, HIIT, Cycling, etc.)."""
    categories = ClassCategory.query.all()
    return jsonify(categories_schema.dump(categories)), 200
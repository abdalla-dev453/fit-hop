from app.blueprints.auth import auth_bp
from app.blueprints.studios import studios_bp
from app.blueprints.trainers import trainers_bp
from app.blueprints.classes import classes_bp
from app.blueprints.passes import passes_bp
from app.blueprints.bookings import bookings_bp
from app.blueprints.admin import admin_bp

def register_blueprints(flask_app):
    flask_app.register_blueprint(auth_bp, url_prefix="/api/auth")
    flask_app.register_blueprint(studios_bp, url_prefix="/api/studios")
    flask_app.register_blueprint(trainers_bp, url_prefix="/api/trainers")
    flask_app.register_blueprint(classes_bp, url_prefix="/api/classes")
    flask_app.register_blueprint(passes_bp, url_prefix="/api/passes")
    flask_app.register_blueprint(bookings_bp, url_prefix="/api/bookings")
    flask_app.register_blueprint(admin_bp, url_prefix="/api/admin")
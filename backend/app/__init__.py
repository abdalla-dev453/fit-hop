from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, jwt, cors, migrate, ma
from marshmallow import ValidationError

# the create_app function is a factory function that returns a Flask application instance 
def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    cors.init_app(flask_app)
    migrate.init_app(flask_app, db)
    ma.init_app(flask_app)

    # Import models so SQLAlchemy metadata picks them up
    import app.models  # noqa: F401

    # Register Blueprints
    from app.blueprints import register_blueprints
    register_blueprints(flask_app)

    # Error handlers
    @flask_app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify({
            "error": "Validation failed",
            "message": err.messages
        }), 400

    return flask_app

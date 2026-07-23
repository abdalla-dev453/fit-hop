from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors, migrate

def create_app(config_class=Config):
    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    cors.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Import models so SQLAlchemy metadata picks them up
    import app.models  # noqa: F401

    # Register Blueprints
    from app.blueprints import register_blueprints
    register_blueprints(flask_app)

    return flask_app
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-fallback")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-key-fallback")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI", "sqlite:///fitpass.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
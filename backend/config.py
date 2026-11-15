import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# Load .env from root or backend directory
load_dotenv(os.path.join(basedir, "..", ".env"))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "eldercare-super-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "eldercare-jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "120")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")))

    # Database resolution: handle Neon/Render postgresql prefix
    raw_db_url = os.environ.get("DATABASE_URL")
    if raw_db_url and raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = raw_db_url or f"sqlite:///{os.path.join(basedir, 'eldercare.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Resend Email API
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
    MAIL_FROM = os.environ.get("MAIL_FROM", "ElderCare Alerts <onboarding@resend.dev>")

    # URLs
    FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5000")

    # Scheduler & Reminders
    SCHEDULER_API_ENABLED = os.environ.get("SCHEDULER_API_ENABLED", "true").lower() == "true"
    ENABLE_BACKGROUND_SCHEDULER = os.environ.get("ENABLE_BACKGROUND_SCHEDULER", "true").lower() == "true"
    CHECK_DOSE_INTERVAL_SECONDS = int(os.environ.get("CHECK_DOSE_INTERVAL_SECONDS", "60"))
    MISSED_DOSE_THRESHOLD_MINUTES = int(os.environ.get("MISSED_DOSE_THRESHOLD_MINUTES", "30"))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    ENABLE_BACKGROUND_SCHEDULER = False
    RESEND_API_KEY = ""

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

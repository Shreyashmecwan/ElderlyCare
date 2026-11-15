from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

try:
    from flask_migrate import Migrate
    migrate = Migrate()
except ImportError:
    class DummyMigrate:
        def init_app(self, app, db):
            pass
    migrate = DummyMigrate()

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
background_scheduler = BackgroundScheduler(daemon=True)

import os
from flask import Flask, jsonify
from app.config import config_by_name
from app.extensions import db, jwt, cors, migrate
from app.routes.auth_routes import auth_bp
from app.routes.profile_routes import profile_bp
from app.routes.medication_routes import medication_bp
from app.routes.adherence_routes import adherence_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.notification_routes import notification_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.swagger_routes import swagger_bp
from app.services.scheduler_service import init_scheduler

def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Validate secret keys only when running in production mode
    if app.config.get("ENV") == "production" or os.getenv("FLASK_ENV") == "production":
        default_secret = "eldercare-super-secret-key-change-in-production"
        default_jwt = "eldercare-jwt-secret-key-change-in-production"
        if app.config.get("SECRET_KEY") == default_secret or app.config.get("JWT_SECRET_KEY") == default_jwt:
            raise RuntimeError(
                "Production secret keys are not set. Please configure SECRET_KEY and JWT_SECRET_KEY."
            )
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("FRONTEND_URL", "http://localhost:5173")}}, supports_credentials=True)


    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(medication_bp)
    app.register_blueprint(adherence_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(swagger_bp)

    # JWT Error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": {"code": "TOKEN_EXPIRED", "message": "The token has expired"}}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"success": False, "error": {"code": "INVALID_TOKEN", "message": "Signature verification failed"}}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"success": False, "error": {"code": "AUTHORIZATION_REQUIRED", "message": "Request does not contain an access token"}}), 401

    # Generic HTTP Error handlers
    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({"success": False, "error": {"code": "NOT_FOUND", "message": "Resource not found"}}), 404

    @app.errorhandler(405)
    def method_not_allowed_handler(e):
        return jsonify({"success": False, "error": {"code": "METHOD_NOT_ALLOWED", "message": "Method not allowed for this endpoint"}}), 405

    @app.errorhandler(500)
    def internal_error_handler(e):
        return jsonify({"success": False, "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An internal server error occurred"}}), 500

    # Auto-create tables for development / SQLite
    with app.app_context():
        db.create_all()

    # Start APScheduler if enabled and not in testing mode
    if not app.config.get("TESTING", False):
        init_scheduler(app)

    return app

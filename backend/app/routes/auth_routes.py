from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile
from app.models.notification import NotificationPreference
from app.utils.validators import is_valid_email, api_response, api_error
from app.utils.decorators import get_current_user

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    role = data.get("role", UserRole.ELDERLY).upper()
    phone = data.get("phone_number", "").strip()
    timezone = data.get("timezone", "UTC")

    if not email or not is_valid_email(email):
        return api_error("Valid email is required", "INVALID_EMAIL", 400)
    if not password or len(password) < 6:
        return api_error("Password must be at least 6 characters long", "INVALID_PASSWORD", 400)
    if not full_name:
        return api_error("Full name is required", "MISSING_NAME", 400)
    if role not in UserRole.ALL:
        return api_error(f"Invalid role. Choose from: {', '.join(UserRole.ALL)}", "INVALID_ROLE", 400)

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return api_error("An account with this email already exists", "EMAIL_EXISTS", 409)

    # Create user
    user = User(
        email=email,
        full_name=full_name,
        role=role,
        phone_number=phone,
        timezone=timezone
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    # Create default notification preference
    pref = NotificationPreference(user_id=user.id)
    db.session.add(pref)

    # If registering as an ELDERLY user, automatically initialize their healthcare profile
    profile = None
    if role == UserRole.ELDERLY:
        profile = ElderlyProfile(
            user_id=user.id,
            full_name=full_name,
            timezone=timezone
        )
        db.session.add(profile)

    db.session.commit()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    user_data = user.to_dict()
    if profile:
        user_data["profile_id"] = profile.id
        user_data["has_profile"] = True

    return api_response({
        "user": user_data,
        "access_token": access_token,
        "refresh_token": refresh_token
    }, "Registration successful", 201)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return api_error("Email and password are required", "MISSING_CREDENTIALS", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return api_error("Invalid email or password", "INVALID_CREDENTIALS", 401)

    if not user.is_active:
        return api_error("Your account has been deactivated. Please contact support.", "ACCOUNT_INACTIVE", 403)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return api_response({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }, "Login successful")

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user or not user.is_active:
        return api_error("User not found or inactive", "UNAUTHORIZED", 401)

    new_access_token = create_access_token(identity=user.id)
    return api_response({"access_token": new_access_token}, "Token refreshed")

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user = get_current_user()
    if not user or not user.is_active:
        return api_error("User not found or inactive", "UNAUTHORIZED", 401)

    user_dict = user.to_dict()

    # Include membership profiles for Family and Caretaker
    connected_profiles = []
    if user.role in [UserRole.FAMILY, UserRole.CARETAKER]:
        for m in user.memberships:
            if m.status == "ACTIVE" and m.profile:
                connected_profiles.append({
                    "membership_id": m.id,
                    "profile_id": m.profile.id,
                    "profile_name": m.profile.full_name,
                    "relationship_title": m.relationship_title,
                    "permission": m.permission,
                    "created_at": m.created_at.isoformat()
                })
    user_dict["connected_profiles"] = connected_profiles

    return api_response(user_dict)

@auth_bp.route("/reset-password-request", methods=["POST"])
def reset_password_request():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    if not email:
        return api_error("Email is required", "MISSING_EMAIL", 400)

    user = User.query.filter_by(email=email).first()
    # For security reasons, do not leak whether the email exists
    return api_response(None, "If an account exists with this email, password reset instructions have been sent.")

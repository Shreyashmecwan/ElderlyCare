from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile, ProfileMembership, MembershipPermission, MembershipStatus

def get_current_user():
    """Returns the authenticated User object from the current JWT token identity."""
    identity = get_jwt_identity()
    if not identity:
        return None
    from app.extensions import db
    return db.session.get(User, identity)

def role_required(*allowed_roles):
    """Decorator to enforce that the authenticated user possesses one of the allowed system roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "User inactive or not found"}}), 401
            
            if user.role not in allowed_roles:
                return jsonify({
                    "success": False, 
                    "error": {
                        "code": "FORBIDDEN", 
                        "message": f"Access denied. Requires one of roles: {', '.join(allowed_roles)}"
                    }
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def check_profile_access(user: User, profile_id: str, required_permission: str = None) -> tuple[bool, str, ElderlyProfile | None]:
    """
    Checks if a user has access to a specific elderly healthcare profile.
    Returns (has_access: bool, error_message: str, profile: ElderlyProfile | None)
    """
    if not user:
        return False, "Authentication required", None

    from app.extensions import db
    profile = db.session.get(ElderlyProfile, profile_id)
    if not profile:
        return False, "Healthcare profile not found", None

    # 1. If user is the elderly owner of this profile
    if profile.user_id == user.id:
        return True, "", profile

    # 2. Check ProfileMembership for Family / Caretaker
    membership = ProfileMembership.query.filter_by(
        profile_id=profile_id,
        user_id=user.id,
        status=MembershipStatus.ACTIVE
    ).first()

    if not membership:
        return False, "You do not have authorized access to this elderly healthcare profile", None

    # Check permission level if required
    if required_permission == MembershipPermission.FULL_ACCESS:
        if membership.permission != MembershipPermission.FULL_ACCESS:
            return False, "Full access permission is required for this action", profile

    return True, "", profile

def profile_access_required(permission: str = None):
    """Decorator to protect routes that operate on a specific profile_id."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_active:
                return jsonify({"success": False, "error": {"code": "UNAUTHORIZED", "message": "User inactive or not found"}}), 401

            profile_id = kwargs.get("profile_id")
            if not profile_id:
                profile_id = request.view_args.get("profile_id") if request.view_args else None
            if not profile_id and request.is_json:
                profile_id = request.get_json(silent=True, default={}).get("profile_id")

            if not profile_id:
                return jsonify({"success": False, "error": {"code": "BAD_REQUEST", "message": "Missing profile_id"}}), 400

            has_access, error_msg, profile = check_profile_access(user, profile_id, permission)
            if not has_access:
                return jsonify({"success": False, "error": {"code": "FORBIDDEN", "message": error_msg}}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

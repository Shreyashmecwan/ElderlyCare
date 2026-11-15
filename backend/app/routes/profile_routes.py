from datetime import datetime, timedelta, timezone
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile, ProfileMembership, Invitation, MembershipPermission, MembershipStatus, InvitationStatus
from app.utils.validators import api_response, api_error, parse_date
from app.utils.decorators import get_current_user, check_profile_access
from app.services.audit_service import log_audit_event

profile_bp = Blueprint("profiles", __name__, url_prefix="/api/profiles")

@profile_bp.route("", methods=["GET"])
@jwt_required()
def list_my_profiles():
    """Lists healthcare profiles accessible to current user."""
    user = get_current_user()
    if not user:
        return api_error("Unauthorized", "UNAUTHORIZED", 401)

    results = []

    # 1. Profile owned by user (if elderly)
    if user.elderly_profile:
        p_dict = user.elderly_profile.to_dict()
        p_dict["user_relationship"] = "OWNER"
        p_dict["permission"] = MembershipPermission.FULL_ACCESS
        results.append(p_dict)

    # 2. Profiles user has authorized membership for (as family or caretaker)
    memberships = ProfileMembership.query.filter_by(user_id=user.id, status=MembershipStatus.ACTIVE).all()
    for m in memberships:
        if m.profile and (not user.elderly_profile or m.profile.id != user.elderly_profile.id):
            p_dict = m.profile.to_dict()
            p_dict["user_relationship"] = m.relationship_title or m.role
            p_dict["permission"] = m.permission
            p_dict["membership_id"] = m.id
            results.append(p_dict)

    return api_response(results)

@profile_bp.route("", methods=["POST"])
@jwt_required()
def create_profile():
    """Creates a new elderly healthcare profile (by elderly user or by family/caretaker on their behalf)."""
    user = get_current_user()
    data = request.get_json() or {}
    full_name = data.get("full_name", "").strip()

    if not full_name:
        return api_error("Full name is required", "MISSING_NAME", 400)

    # If user is ELDERLY and already has a profile, reject duplicate
    if user.role == UserRole.ELDERLY and user.elderly_profile:
        return api_error("You already have an active healthcare profile", "PROFILE_EXISTS", 409)

    profile = ElderlyProfile(
        user_id=user.id if user.role == UserRole.ELDERLY else None,
        full_name=full_name,
        date_of_birth=parse_date(data.get("date_of_birth")),
        gender=data.get("gender"),
        blood_group=data.get("blood_group"),
        emergency_contact_name=data.get("emergency_contact_name"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        emergency_contact_relation=data.get("emergency_contact_relation"),
        medical_notes=data.get("medical_notes"),
        allergies=data.get("allergies"),
        address=data.get("address"),
        timezone=data.get("timezone", user.timezone or "UTC")
    )
    db.session.add(profile)
    db.session.flush()

    # If created by family or caretaker, automatically grant them FULL_ACCESS membership
    if user.role in [UserRole.FAMILY, UserRole.CARETAKER]:
        membership = ProfileMembership(
            profile_id=profile.id,
            user_id=user.id,
            role=user.role,
            relationship_title=data.get("relationship_title", "Primary Caregiver"),
            permission=MembershipPermission.FULL_ACCESS
        )
        db.session.add(membership)

    db.session.commit()

    log_audit_event(user.id, "CREATE_PROFILE", "ElderlyProfile", profile.id, {"full_name": full_name})
    return api_response(profile.to_dict(), "Healthcare profile created successfully", 201)

@profile_bp.route("/<profile_id>", methods=["GET"])
@jwt_required()
def get_profile(profile_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    return api_response(profile.to_dict())

@profile_bp.route("/<profile_id>", methods=["PUT"])
@jwt_required()
def update_profile(profile_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    data = request.get_json() or {}
    if "full_name" in data and data["full_name"].strip():
        profile.full_name = data["full_name"].strip()
    if "date_of_birth" in data:
        profile.date_of_birth = parse_date(data["date_of_birth"])
    if "gender" in data:
        profile.gender = data["gender"]
    if "blood_group" in data:
        profile.blood_group = data["blood_group"]
    if "emergency_contact_name" in data:
        profile.emergency_contact_name = data["emergency_contact_name"]
    if "emergency_contact_phone" in data:
        profile.emergency_contact_phone = data["emergency_contact_phone"]
    if "emergency_contact_relation" in data:
        profile.emergency_contact_relation = data["emergency_contact_relation"]
    if "medical_notes" in data:
        profile.medical_notes = data["medical_notes"]
    if "allergies" in data:
        profile.allergies = data["allergies"]
    if "address" in data:
        profile.address = data["address"]
    if "timezone" in data:
        profile.timezone = data["timezone"]

    db.session.commit()
    log_audit_event(user.id, "UPDATE_PROFILE", "ElderlyProfile", profile.id)
    return api_response(profile.to_dict(), "Profile updated successfully")

# --- Profile Passcode & Invitation System ---

@profile_bp.route("/<profile_id>/invitations", methods=["POST"])
@jwt_required()
def create_invitation(profile_id):
    """Generates a secure passcode / invite token to share access with family or caretakers."""
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    data = request.get_json() or {}
    target_role = data.get("role", UserRole.FAMILY).upper()
    permission = data.get("permission", MembershipPermission.FULL_ACCESS).upper()
    relationship_title = data.get("relationship_title", "").strip()
    recipient_email = data.get("recipient_email", "").strip().lower()
    expires_in_days = int(data.get("expires_in_days", 7))

    if target_role not in [UserRole.FAMILY, UserRole.CARETAKER]:
        return api_error("Role must be FAMILY or CARETAKER", "INVALID_ROLE", 400)
    if permission not in MembershipPermission.ALL:
        return api_error("Invalid permission level", "INVALID_PERMISSION", 400)

    passcode = Invitation.generate_passcode(prefix="CARE" if target_role == UserRole.CARETAKER else "FAM")
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    invite = Invitation(
        profile_id=profile.id,
        invited_by_user_id=user.id,
        passcode=passcode,
        recipient_email=recipient_email if recipient_email else None,
        role=target_role,
        relationship_title=relationship_title or ("Caretaker" if target_role == UserRole.CARETAKER else "Family Member"),
        permission=permission,
        expires_at=expires_at,
        status=InvitationStatus.PENDING
    )
    db.session.add(invite)
    db.session.commit()

    log_audit_event(user.id, "CREATE_INVITATION", "Invitation", invite.id, {"passcode": passcode, "role": target_role})
    return api_response(invite.to_dict(), f"Passcode generated: {passcode}", 201)

@profile_bp.route("/<profile_id>/invitations", methods=["GET"])
@jwt_required()
def list_invitations(profile_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    invites = Invitation.query.filter_by(profile_id=profile_id).order_by(Invitation.created_at.desc()).all()
    return api_response([i.to_dict() for i in invites])

@profile_bp.route("/<profile_id>/invitations/<invitation_id>", methods=["DELETE"])
@jwt_required()
def revoke_invitation(profile_id, invitation_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    invite = Invitation.query.filter_by(id=invitation_id, profile_id=profile_id).first()
    if not invite:
        return api_error("Invitation not found", "NOT_FOUND", 404)

    invite.status = InvitationStatus.REVOKED
    db.session.commit()
    log_audit_event(user.id, "REVOKE_INVITATION", "Invitation", invite.id)
    return api_response(None, "Invitation revoked")

@profile_bp.route("/join", methods=["POST"])
@jwt_required()
def join_via_passcode():
    """Redeems an invitation passcode to link the authenticated user to an elderly profile."""
    user = get_current_user()
    data = request.get_json() or {}
    passcode = data.get("passcode", "").strip().upper()

    if not passcode:
        return api_error("Passcode is required", "MISSING_PASSCODE", 400)

    invite = Invitation.query.filter_by(passcode=passcode).first()
    if not invite:
        return api_error("Invalid or unrecognized passcode", "INVALID_PASSCODE", 404)

    if invite.status != InvitationStatus.PENDING or invite.is_expired:
        return api_error("This passcode has expired or already been redeemed", "PASSCODE_EXPIRED", 400)

    # Check if already a member
    existing_member = ProfileMembership.query.filter_by(profile_id=invite.profile_id, user_id=user.id).first()
    if existing_member:
        if existing_member.status == MembershipStatus.ACTIVE:
            return api_error("You are already an authorized member of this profile", "ALREADY_MEMBER", 409)
        else:
            # Reactivate
            existing_member.status = MembershipStatus.ACTIVE
            existing_member.permission = invite.permission
            existing_member.role = invite.role
            existing_member.relationship_title = invite.relationship_title
    else:
        # Create membership
        membership = ProfileMembership(
            profile_id=invite.profile_id,
            user_id=user.id,
            role=invite.role,
            relationship_title=invite.relationship_title,
            permission=invite.permission,
            status=MembershipStatus.ACTIVE
        )
        db.session.add(membership)

    # Mark invitation as accepted
    invite.status = InvitationStatus.ACCEPTED
    invite.accepted_by_user_id = user.id
    invite.accepted_at = datetime.now(timezone.utc)
    db.session.commit()

    log_audit_event(user.id, "REDEEM_PASSCODE", "ElderlyProfile", invite.profile_id, {"passcode": passcode})
    return api_response(invite.profile.to_dict(), f"Successfully connected to {invite.profile.full_name}'s healthcare profile!")

@profile_bp.route("/<profile_id>/members", methods=["GET"])
@jwt_required()
def list_profile_members(profile_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    members = ProfileMembership.query.filter_by(profile_id=profile_id, status=MembershipStatus.ACTIVE).all()
    return api_response([m.to_dict() for m in members])

@profile_bp.route("/<profile_id>/members/<membership_id>", methods=["DELETE"])
@jwt_required()
def revoke_profile_member(profile_id, membership_id):
    user = get_current_user()
    has_access, err, profile = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    membership = ProfileMembership.query.filter_by(id=membership_id, profile_id=profile_id).first()
    if not membership:
        return api_error("Membership not found", "NOT_FOUND", 404)

    membership.status = MembershipStatus.REVOKED
    db.session.commit()
    log_audit_event(user.id, "REVOKE_MEMBER", "ProfileMembership", membership.id)
    return api_response(None, "Caregiver access has been revoked")

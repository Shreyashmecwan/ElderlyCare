from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.adherence import MedicationLog, AdherenceStatus
from app.models.medication import Medication
from app.models.audit import AuditLog
from app.models.profile import MembershipPermission
from app.utils.validators import api_response, api_error, parse_date
from app.utils.decorators import get_current_user, check_profile_access
from app.services.adherence_service import (
    ensure_daily_logs_for_profile,
    update_dose_status,
    calculate_profile_adherence
)

adherence_bp = Blueprint("adherence", __name__, url_prefix="/api/adherence")

@adherence_bp.route("/daily", methods=["GET"])
@jwt_required()
def get_daily_adherence():
    """Retrieves all scheduled medication doses for a profile on a given date (default today)."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")
    date_str = request.args.get("date")

    if not profile_id:
        return api_error("profile_id query parameter is required", "MISSING_PARAM", 400)

    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    target_date = parse_date(date_str) if date_str else date.today()
    if not target_date:
        return api_error("Invalid date format. Expected YYYY-MM-DD", "INVALID_DATE", 400)

    logs = ensure_daily_logs_for_profile(profile_id, target_date)
    return api_response([l.to_dict() for l in logs])

@adherence_bp.route("/<log_id>/status", methods=["POST"])
@jwt_required()
def change_dose_status(log_id):
    """
    Marks a scheduled dose as TAKEN, SKIPPED, or MISSED.
    Permitted for Elderly user, Caretakers, and Family with FULL_ACCESS.
    """
    user = get_current_user()
    log = db.session.get(MedicationLog, log_id)
    if not log:
        return api_error("Scheduled dose record not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, log.medication.profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    data = request.get_json() or {}
    new_status = data.get("status", "").upper()
    notes = data.get("notes")

    success, msg, updated_log = update_dose_status(log, new_status, user, notes)
    if not success:
        return api_error(msg, "INVALID_STATUS", 400)

    return api_response(updated_log.to_dict(), msg)

@adherence_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_adherence_statistics():
    """Computes real adherence compliance score and daily history over past N days."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")
    days = int(request.args.get("days", 7))

    if not profile_id:
        return api_error("profile_id query parameter is required", "MISSING_PARAM", 400)

    has_access, err, _ = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    stats = calculate_profile_adherence(profile_id, days)
    return api_response(stats)

@adherence_bp.route("/audit-trail", methods=["GET"])
@jwt_required()
def get_audit_trail():
    """Returns the immutable audit trail for adherence events."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")

    if not profile_id:
        return api_error("profile_id is required", "MISSING_PARAM", 400)

    has_access, err, _ = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    # Limit audit logs to the requesting profile's medication records only
    medication_ids = db.session.query(Medication.id).filter(Medication.profile_id == profile_id).subquery()
    logs = (
        AuditLog.query
        .filter(
            AuditLog.entity_type == "MedicationLog",
            AuditLog.entity_id.in_(medication_ids)
        )
        .order_by(AuditLog.created_at.desc())
        .limit(50)
        .all()
    )
    return api_response([l.to_dict() for l in logs])

from datetime import date, datetime, timedelta, timezone
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile, ProfileMembership, MembershipStatus
from app.models.medication import Medication
from app.models.adherence import MedicationLog, AdherenceStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationType
from app.utils.validators import api_response, api_error, parse_date
from app.utils.decorators import get_current_user, check_profile_access
from app.services.adherence_service import ensure_daily_logs_for_profile, calculate_profile_adherence

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/elderly", methods=["GET"])
@jwt_required()
def get_elderly_dashboard():
    """Returns data tailored for the Elderly User's simplified, accessible dashboard."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")

    # If user is ELDERLY, default to their own profile
    if not profile_id and user.elderly_profile:
        profile_id = user.elderly_profile.id

    if not profile_id:
        return api_error("No healthcare profile found for this user", "NO_PROFILE", 404)

    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    today = date.today()
    logs = ensure_daily_logs_for_profile(profile.id, today)

    # Compute daily progress
    total_today = len(logs)
    taken_today = sum(1 for l in logs if l.status == AdherenceStatus.TAKEN)
    remaining_today = sum(1 for l in logs if l.status == AdherenceStatus.UPCOMING)
    missed_today = sum(1 for l in logs if l.status == AdherenceStatus.MISSED)

    # Find next upcoming dose
    upcoming_doses = [l for l in logs if l.status == AdherenceStatus.UPCOMING]
    next_dose = upcoming_doses[0].to_dict() if upcoming_doses else None

    # Next upcoming appointment
    next_appt = Appointment.query.filter(
        Appointment.profile_id == profile.id,
        Appointment.appointment_date >= today,
        Appointment.status == AppointmentStatus.SCHEDULED
    ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).first()

    # 7-day adherence rate
    stats = calculate_profile_adherence(profile.id, days=7)

    return api_response({
        "profile": profile.to_dict(),
        "today": today.isoformat(),
        "summary": {
            "total_today": total_today,
            "taken_today": taken_today,
            "remaining_today": remaining_today,
            "missed_today": missed_today,
            "completion_percentage": round((taken_today / total_today * 100), 1) if total_today > 0 else 100.0,
            "adherence_rate_7d": stats["adherence_rate"]
        },
        "next_dose": next_dose,
        "today_doses": [l.to_dict() for l in logs],
        "next_appointment": next_appt.to_dict() if next_appt else None,
        "emergency_contact": {
            "name": profile.emergency_contact_name,
            "phone": profile.emergency_contact_phone,
            "relation": profile.emergency_contact_relation
        }
    })

@dashboard_bp.route("/family", methods=["GET"])
@jwt_required()
def get_family_dashboard():
    """Returns overview for Family Members monitoring one or more loved ones."""
    user = get_current_user()
    today = date.today()

    # Find all connected profiles for this family member
    memberships = ProfileMembership.query.filter_by(
        user_id=user.id,
        status=MembershipStatus.ACTIVE
    ).all()

    monitored_profiles = []
    all_profile_ids = []

    for m in memberships:
        p = m.profile
        if not p:
            continue
        all_profile_ids.append(p.id)
        stats = calculate_profile_adherence(p.id, days=7)
        logs = ensure_daily_logs_for_profile(p.id, today)

        monitored_profiles.append({
            "profile_id": p.id,
            "full_name": p.full_name,
            "relationship": m.relationship_title,
            "permission": m.permission,
            "today_total": len(logs),
            "today_taken": sum(1 for l in logs if l.status == AdherenceStatus.TAKEN),
            "today_missed": sum(1 for l in logs if l.status == AdherenceStatus.MISSED),
            "adherence_rate_7d": stats["adherence_rate"]
        })

    # Recent missed alerts for these profiles
    missed_alerts = []
    if all_profile_ids:
        recent_missed = MedicationLog.query.join(Medication).filter(
            Medication.profile_id.in_(all_profile_ids),
            MedicationLog.status == AdherenceStatus.MISSED,
            MedicationLog.scheduled_date >= (today - timedelta(days=3))
        ).order_by(MedicationLog.scheduled_date.desc(), MedicationLog.scheduled_time.desc()).limit(10).all()
        missed_alerts = [m.to_dict() for m in recent_missed]

    # Upcoming appointments across all connected seniors
    upcoming_appts = []
    if all_profile_ids:
        appts = Appointment.query.filter(
            Appointment.profile_id.in_(all_profile_ids),
            Appointment.appointment_date >= today,
            Appointment.status == AppointmentStatus.SCHEDULED
        ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).limit(5).all()
        upcoming_appts = [a.to_dict() for a in appts]

    return api_response({
        "family_user": {"id": user.id, "name": user.full_name},
        "monitored_profiles": monitored_profiles,
        "missed_alerts": missed_alerts,
        "upcoming_appointments": upcoming_appts
    })

@dashboard_bp.route("/caretaker", methods=["GET"])
@jwt_required()
def get_caretaker_dashboard():
    """Returns overview for Professional Caretakers managing multiple patients."""
    user = get_current_user()
    today = date.today()

    memberships = ProfileMembership.query.filter_by(
        user_id=user.id,
        status=MembershipStatus.ACTIVE
    ).all()

    assigned_patients = []
    all_today_doses = []
    profile_ids = []

    for m in memberships:
        p = m.profile
        if not p:
            continue
        profile_ids.append(p.id)
        logs = ensure_daily_logs_for_profile(p.id, today)
        for l in logs:
            l_dict = l.to_dict()
            l_dict["patient_name"] = p.full_name
            l_dict["patient_id"] = p.id
            all_today_doses.append(l_dict)

        assigned_patients.append({
            "profile_id": p.id,
            "full_name": p.full_name,
            "relationship_title": m.relationship_title,
            "permission": m.permission,
            "total_today": len(logs),
            "pending_today": sum(1 for l in logs if l.status == AdherenceStatus.UPCOMING),
            "taken_today": sum(1 for l in logs if l.status == AdherenceStatus.TAKEN),
            "missed_today": sum(1 for l in logs if l.status == AdherenceStatus.MISSED)
        })

    # Sort all doses by scheduled time for master administration timeline
    all_today_doses.sort(key=lambda x: x["scheduled_time"])

    # Upcoming clinic visits for assigned patients
    upcoming_appts = []
    if profile_ids:
        appts = Appointment.query.filter(
            Appointment.profile_id.in_(profile_ids),
            Appointment.appointment_date >= today,
            Appointment.status == AppointmentStatus.SCHEDULED
        ).order_by(Appointment.appointment_date.asc()).limit(5).all()
        upcoming_appts = [a.to_dict() for a in appts]

    return api_response({
        "caretaker_user": {"id": user.id, "name": user.full_name},
        "assigned_patients": assigned_patients,
        "master_daily_doses": all_today_doses,
        "upcoming_appointments": upcoming_appts
    })

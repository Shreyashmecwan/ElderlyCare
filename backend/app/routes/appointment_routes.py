from datetime import date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.profile import MembershipPermission
from app.utils.validators import api_response, api_error, parse_date, is_valid_time
from app.utils.decorators import get_current_user, check_profile_access
from app.services.audit_service import log_audit_event

appointment_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")

@appointment_bp.route("", methods=["GET"])
@jwt_required()
def list_appointments():
    """Lists appointments for a profile, sorted by date and time."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")
    filter_type = request.args.get("filter", "upcoming").lower()  # "upcoming", "past", "all"

    if not profile_id:
        return api_error("profile_id query parameter is required", "MISSING_PARAM", 400)

    has_access, err, _ = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    today = date.today()
    query = Appointment.query.filter_by(profile_id=profile_id)

    if filter_type == "upcoming":
        query = query.filter(Appointment.appointment_date >= today, Appointment.status != AppointmentStatus.CANCELLED)
        query = query.order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc())
    elif filter_type == "past":
        query = query.filter(Appointment.appointment_date < today)
        query = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.desc())
    else:
        query = query.order_by(Appointment.appointment_date.desc())

    appts = query.all()
    return api_response([a.to_dict() for a in appts])

@appointment_bp.route("", methods=["POST"])
@jwt_required()
def create_appointment():
    """Creates a new doctor or clinic appointment."""
    user = get_current_user()
    data = request.get_json() or {}
    profile_id = data.get("profile_id")

    if not profile_id:
        return api_error("profile_id is required", "MISSING_PARAM", 400)

    has_access, err, _ = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    doctor_name = data.get("doctor_name", "").strip()
    appt_date = parse_date(data.get("appointment_date"))
    appt_time = data.get("appointment_time", "").strip()

    if not doctor_name or not appt_date or not is_valid_time(appt_time):
        return api_error("Doctor name, valid date, and time (HH:MM) are required", "MISSING_FIELDS", 400)

    appt = Appointment(
        profile_id=profile_id,
        created_by_user_id=user.id,
        doctor_name=doctor_name,
        specialty=data.get("specialty"),
        hospital_clinic=data.get("hospital_clinic"),
        location=data.get("location"),
        appointment_date=appt_date,
        appointment_time=appt_time,
        appointment_type=data.get("appointment_type", AppointmentType.IN_PERSON),
        notes=data.get("notes"),
        status=AppointmentStatus.SCHEDULED
    )
    db.session.add(appt)
    db.session.commit()

    log_audit_event(user.id, "CREATE_APPOINTMENT", "Appointment", appt.id, {"doctor": doctor_name, "date": appt_date.isoformat()})
    return api_response(appt.to_dict(), "Appointment booked successfully", 201)

@appointment_bp.route("/<appt_id>", methods=["GET"])
@jwt_required()
def get_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if not appt:
        return api_error("Appointment not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, appt.profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    return api_response(appt.to_dict())

@appointment_bp.route("/<appt_id>", methods=["PUT"])
@jwt_required()
def update_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if not appt:
        return api_error("Appointment not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, appt.profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    data = request.get_json() or {}
    if "doctor_name" in data and data["doctor_name"].strip():
        appt.doctor_name = data["doctor_name"].strip()
    if "specialty" in data:
        appt.specialty = data["specialty"]
    if "hospital_clinic" in data:
        appt.hospital_clinic = data["hospital_clinic"]
    if "location" in data:
        appt.location = data["location"]
    if "appointment_date" in data:
        appt.appointment_date = parse_date(data["appointment_date"])
    if "appointment_time" in data and is_valid_time(data["appointment_time"]):
        appt.appointment_time = data["appointment_time"].strip()
    if "appointment_type" in data:
        appt.appointment_type = data["appointment_type"]
    if "notes" in data:
        appt.notes = data["notes"]
    if "status" in data and data["status"] in AppointmentStatus.ALL:
        appt.status = data["status"]

    db.session.commit()
    log_audit_event(user.id, "UPDATE_APPOINTMENT", "Appointment", appt.id)
    return api_response(appt.to_dict(), "Appointment updated successfully")

@appointment_bp.route("/<appt_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if not appt:
        return api_error("Appointment not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, appt.profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    appt.status = AppointmentStatus.CANCELLED
    db.session.commit()
    log_audit_event(user.id, "CANCEL_APPOINTMENT", "Appointment", appt.id)
    return api_response(appt.to_dict(), "Appointment cancelled")

@appointment_bp.route("/<appt_id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if not appt:
        return api_error("Appointment not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, appt.profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    db.session.delete(appt)
    db.session.commit()
    log_audit_event(user.id, "DELETE_APPOINTMENT", "Appointment", appt_id)
    return api_response(None, "Appointment deleted")

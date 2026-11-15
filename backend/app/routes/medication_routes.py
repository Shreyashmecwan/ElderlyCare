from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.medication import Medication, MedicationSchedule, FrequencyType
from app.models.profile import MembershipPermission
from app.utils.validators import api_response, api_error, parse_date, is_valid_time
from app.utils.decorators import get_current_user, check_profile_access
from app.services.audit_service import log_audit_event

medication_bp = Blueprint("medications", __name__, url_prefix="/api/medications")

@medication_bp.route("", methods=["GET"])
@jwt_required()
def list_medications():
    """Lists medications for a specific profile_id."""
    user = get_current_user()
    profile_id = request.args.get("profile_id")
    status_filter = request.args.get("status", "active").lower()  # "active", "inactive", "all"

    if not profile_id:
        return api_error("profile_id query parameter is required", "MISSING_PARAM", 400)

    has_access, err, profile = check_profile_access(user, profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    query = Medication.query.filter_by(profile_id=profile_id)
    if status_filter == "active":
        query = query.filter_by(is_active=True)
    elif status_filter == "inactive":
        query = query.filter_by(is_active=False)

    meds = query.order_by(Medication.created_at.desc()).all()
    return api_response([m.to_dict() for m in meds])

@medication_bp.route("", methods=["POST"])
@jwt_required()
def add_medication():
    """Adds a new medication with one or more scheduled administration times."""
    user = get_current_user()
    data = request.get_json() or {}
    profile_id = data.get("profile_id")

    if not profile_id:
        return api_error("profile_id is required", "MISSING_PARAM", 400)

    has_access, err, profile = check_profile_access(user, profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    name = data.get("name", "").strip()
    dosage = data.get("dosage", "").strip()
    unit = data.get("unit", "mg").strip()
    start_date = parse_date(data.get("start_date"))

    if not name or not dosage or not start_date:
        return api_error("Medication name, dosage, and start date are required", "MISSING_FIELDS", 400)

    med = Medication(
        profile_id=profile_id,
        name=name,
        dosage=dosage,
        unit=unit,
        instructions=data.get("instructions"),
        prescribing_doctor=data.get("prescribing_doctor"),
        notes=data.get("notes"),
        frequency_type=data.get("frequency_type", FrequencyType.DAILY),
        current_inventory=int(data.get("current_inventory", 30)),
        refill_alert_threshold=int(data.get("refill_alert_threshold", 7)),
        start_date=start_date,
        end_date=parse_date(data.get("end_date")),
        is_active=True
    )
    db.session.add(med)
    db.session.flush()

    # Process schedules
    schedules_data = data.get("schedules", [])
    if not schedules_data:
        # Default single morning schedule
        schedules_data = [{"time_of_day": "08:00", "label": "Morning", "days_of_week": "DAILY"}]

    for s in schedules_data:
        time_str = s.get("time_of_day", "").strip()
        if not is_valid_time(time_str):
            continue
        schedule = MedicationSchedule(
            medication_id=med.id,
            time_of_day=time_str,
            label=s.get("label", "Dose"),
            days_of_week=s.get("days_of_week", "DAILY"),
            dose_quantity=s.get("dose_quantity", "1 dose"),
            reminder_enabled=s.get("reminder_enabled", True)
        )
        db.session.add(schedule)

    db.session.commit()
    log_audit_event(user.id, "CREATE_MEDICATION", "Medication", med.id, {"name": name, "dosage": dosage})
    return api_response(med.to_dict(), "Medication added successfully", 201)

@medication_bp.route("/<med_id>", methods=["GET"])
@jwt_required()
def get_medication(med_id):
    user = get_current_user()
    med = db.session.get(Medication, med_id)
    if not med:
        return api_error("Medication not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, med.profile_id)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    return api_response(med.to_dict())

@medication_bp.route("/<med_id>", methods=["PUT"])
@jwt_required()
def update_medication(med_id):
    user = get_current_user()
    med = db.session.get(Medication, med_id)
    if not med:
        return api_error("Medication not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, med.profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    data = request.get_json() or {}
    if "name" in data and data["name"].strip():
        med.name = data["name"].strip()
    if "dosage" in data:
        med.dosage = str(data["dosage"]).strip()
    if "unit" in data:
        med.unit = data["unit"].strip()
    if "instructions" in data:
        med.instructions = data["instructions"]
    if "prescribing_doctor" in data:
        med.prescribing_doctor = data["prescribing_doctor"]
    if "notes" in data:
        med.notes = data["notes"]
    if "frequency_type" in data:
        med.frequency_type = data["frequency_type"]
    if "current_inventory" in data:
        med.current_inventory = int(data["current_inventory"])
    if "refill_alert_threshold" in data:
        med.refill_alert_threshold = int(data["refill_alert_threshold"])
    if "start_date" in data:
        med.start_date = parse_date(data["start_date"])
    if "end_date" in data:
        med.end_date = parse_date(data["end_date"])
    if "is_active" in data:
        med.is_active = bool(data["is_active"])

    # If new schedules are provided in update, update them cleanly
    if "schedules" in data and isinstance(data["schedules"], list):
        # Remove old schedules and add new
        MedicationSchedule.query.filter_by(medication_id=med.id).delete()
        for s in data["schedules"]:
            t_str = s.get("time_of_day", "").strip()
            if is_valid_time(t_str):
                ns = MedicationSchedule(
                    medication_id=med.id,
                    time_of_day=t_str,
                    label=s.get("label", "Dose"),
                    days_of_week=s.get("days_of_week", "DAILY"),
                    dose_quantity=s.get("dose_quantity", "1 dose"),
                    reminder_enabled=s.get("reminder_enabled", True)
                )
                db.session.add(ns)

    db.session.commit()
    log_audit_event(user.id, "UPDATE_MEDICATION", "Medication", med.id)
    return api_response(med.to_dict(), "Medication updated successfully")

@medication_bp.route("/<med_id>", methods=["DELETE"])
@jwt_required()
def delete_medication(med_id):
    """Discontinues (soft-deactivates) medication to maintain history and adherence records."""
    user = get_current_user()
    med = db.session.get(Medication, med_id)
    if not med:
        return api_error("Medication not found", "NOT_FOUND", 404)

    has_access, err, _ = check_profile_access(user, med.profile_id, required_permission=MembershipPermission.FULL_ACCESS)
    if not has_access:
        return api_error(err, "FORBIDDEN", 403)

    med.is_active = False
    db.session.commit()
    log_audit_event(user.id, "DISCONTINUE_MEDICATION", "Medication", med.id)
    return api_response(None, "Medication discontinued successfully")

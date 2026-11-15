from datetime import datetime, date, timedelta, timezone
from app.extensions import db
from app.models.medication import Medication, MedicationSchedule, FrequencyType
from app.models.adherence import MedicationLog, AdherenceStatus
from app.models.user import User
from app.models.profile import ElderlyProfile
from app.services.audit_service import log_audit_event

def is_schedule_active_on_date(schedule: MedicationSchedule, target_date: date) -> bool:
    """Checks if a schedule's recurrence rule matches the given target_date."""
    med = schedule.medication
    if not med.is_active:
        return False
    if med.start_date and med.start_date > target_date:
        return False
    if med.end_date and med.end_date < target_date:
        return False

    if schedule.days_of_week == "DAILY":
        return True

    # e.g., "MON,WED,FRI"
    target_weekday = target_date.strftime("%a").upper()  # e.g., 'MON', 'TUE'
    days = [d.strip().upper() for d in schedule.days_of_week.split(",")]
    return target_weekday in days or "DAILY" in days

def ensure_daily_logs_for_profile(profile_id: str, target_date: date) -> list[MedicationLog]:
    """
    Ensures that an individual MedicationLog record exists for every active schedule
    on target_date. Prevents duplicates via unique constraint / check.
    """
    profile = db.session.get(ElderlyProfile, profile_id)
    if not profile:
        return []

    # Find all active medications for this profile
    active_meds = Medication.query.filter(
        Medication.profile_id == profile_id,
        Medication.is_active == True,
        Medication.start_date <= target_date,
        db.or_(Medication.end_date == None, Medication.end_date >= target_date)
    ).all()

    created_any = False
    for med in active_meds:
        for sched in med.schedules:
            if is_schedule_active_on_date(sched, target_date):
                existing = MedicationLog.query.filter_by(
                    schedule_id=sched.id,
                    scheduled_date=target_date
                ).first()
                if not existing:
                    new_log = MedicationLog(
                        medication_id=med.id,
                        schedule_id=sched.id,
                        scheduled_date=target_date,
                        scheduled_time=sched.time_of_day,
                        status=AdherenceStatus.UPCOMING
                    )
                    db.session.add(new_log)
                    created_any = True

    if created_any:
        db.session.commit()

    # Query all logs for this date, sorted by scheduled_time
    logs = MedicationLog.query.join(Medication).filter(
        Medication.profile_id == profile_id,
        MedicationLog.scheduled_date == target_date
    ).order_by(MedicationLog.scheduled_time.asc()).all()

    return logs

def update_dose_status(log: MedicationLog, new_status: str, user: User, notes: str = None) -> tuple[bool, str, MedicationLog]:
    """
    Marks a scheduled dose with a new status (TAKEN, SKIPPED, MISSED).
    Maintains audit logs and updates medication inventory on TAKEN.
    """
    if new_status not in AdherenceStatus.ALL:
        return False, f"Invalid status. Must be one of: {', '.join(AdherenceStatus.ALL)}", log

    old_status = log.status
    log.status = new_status
    log.recorded_by_user_id = user.id if user else None
    if notes:
        log.notes = notes

    if new_status == AdherenceStatus.TAKEN:
        log.taken_at = datetime.now(timezone.utc)
        # Decrement inventory by 1 if not previously taken
        if old_status != AdherenceStatus.TAKEN and log.medication.current_inventory > 0:
            log.medication.current_inventory -= 1
    elif new_status in [AdherenceStatus.SKIPPED, AdherenceStatus.MISSED]:
        # If it was previously marked TAKEN and now corrected to SKIPPED/MISSED, restore 1 to inventory
        if old_status == AdherenceStatus.TAKEN:
            log.medication.current_inventory += 1
        log.taken_at = None

    db.session.commit()

    # Log audit event
    log_audit_event(
        user_id=user.id if user else None,
        action="UPDATE_DOSE_STATUS",
        entity_type="MedicationLog",
        entity_id=log.id,
        details_dict={
            "medication_id": log.medication_id,
            "medication_name": log.medication.name,
            "scheduled_date": log.scheduled_date.isoformat(),
            "scheduled_time": log.scheduled_time,
            "old_status": old_status,
            "new_status": new_status,
            "notes": notes
        }
    )

    return True, "Dose status updated successfully", log

def calculate_profile_adherence(profile_id: str, days: int = 7) -> dict:
    """
    Computes real adherence statistics over the past N days from the database.
    Returns overall adherence score (%), count taken, missed, skipped, upcoming,
    and a daily trend array.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    logs = MedicationLog.query.join(Medication).filter(
        Medication.profile_id == profile_id,
        MedicationLog.scheduled_date >= start_date,
        MedicationLog.scheduled_date <= end_date
    ).all()

    total_doses = len(logs)
    taken_count = sum(1 for l in logs if l.status == AdherenceStatus.TAKEN)
    missed_count = sum(1 for l in logs if l.status == AdherenceStatus.MISSED)
    skipped_count = sum(1 for l in logs if l.status == AdherenceStatus.SKIPPED)
    upcoming_count = sum(1 for l in logs if l.status == AdherenceStatus.UPCOMING)

    # Completed scheduled doses that are not pending
    past_due_total = taken_count + missed_count + skipped_count
    adherence_percentage = round((taken_count / past_due_total * 100), 1) if past_due_total > 0 else 100.0

    # Daily trend grouping
    daily_stats = {}
    curr = start_date
    while curr <= end_date:
        d_str = curr.isoformat()
        daily_stats[d_str] = {"date": d_str, "day_name": curr.strftime("%a"), "total": 0, "taken": 0, "missed": 0, "skipped": 0}
        curr += timedelta(days=1)

    for l in logs:
        d_key = l.scheduled_date.isoformat()
        if d_key in daily_stats:
            daily_stats[d_key]["total"] += 1
            if l.status == AdherenceStatus.TAKEN:
                daily_stats[d_key]["taken"] += 1
            elif l.status == AdherenceStatus.MISSED:
                daily_stats[d_key]["missed"] += 1
            elif l.status == AdherenceStatus.SKIPPED:
                daily_stats[d_key]["skipped"] += 1

    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_scheduled": total_doses,
        "taken": taken_count,
        "missed": missed_count,
        "skipped": skipped_count,
        "upcoming": upcoming_count,
        "adherence_rate": adherence_percentage,
        "daily_breakdown": list(daily_stats.values())
    }

from datetime import datetime, date, timedelta, timezone
from app.extensions import db, background_scheduler
from app.models.profile import ElderlyProfile
from app.models.medication import Medication
from app.models.adherence import MedicationLog, AdherenceStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationType
from app.utils.timezone_utils import get_today_in_tz, get_current_time_in_tz, parse_time_hh_mm, is_time_passed_by_minutes
from app.services.adherence_service import ensure_daily_logs_for_profile
from app.services.notification_service import (
    notify_upcoming_dose, 
    notify_missed_dose_alert, 
    notify_low_inventory, 
    notify_appointment_reminder
)

def process_due_medications_job(app):
    """
    Periodic job that:
    1. Ensures daily logs are generated for all active profiles in their respective timezones.
    2. Sends reminders for doses due now.
    3. Detects doses overdue by > MISSED_DOSE_THRESHOLD_MINUTES (default 30m) and marks them MISSED.
    """
    with app.app_context():
        try:
            threshold_minutes = app.config.get("MISSED_DOSE_THRESHOLD_MINUTES", 30)
            profiles = ElderlyProfile.query.all()

            for profile in profiles:
                tz_name = profile.timezone or "UTC"
                today_tz = get_today_in_tz(tz_name)
                now_tz = get_current_time_in_tz(tz_name)
                now_time_str = now_tz.strftime("%H:%M")

                # Ensure today's logs exist
                logs = ensure_daily_logs_for_profile(profile.id, today_tz)

                for log in logs:
                    if log.status == AdherenceStatus.UPCOMING:
                        # 1. Check if overdue by threshold
                        if is_time_passed_by_minutes(log.scheduled_time, log.scheduled_date, tz_name, threshold_minutes):
                            log.status = AdherenceStatus.MISSED
                            db.session.commit()
                            # Dispatch missed dose alert
                            notify_missed_dose_alert(log)

                        # 2. Check if due within upcoming 15 minutes window
                        elif log.scheduled_time == now_time_str and log.schedule and log.schedule.reminder_enabled:
                            # Verify if a reminder was already sent for this log today
                            already_sent = Notification.query.filter(
                                Notification.profile_id == profile.id,
                                Notification.type == NotificationType.MED_REMINDER,
                                Notification.title.like(f"%{log.medication.name}%"),
                                db.func.date(Notification.created_at) == today_tz
                            ).first()

                            if not already_sent:
                                notify_upcoming_dose(log)

        except Exception as e:
            app.logger.error(f"Error in process_due_medications_job: {e}")

def process_appointments_job(app):
    """Checks for upcoming appointments and sends 1-day or day-of advance reminders."""
    with app.app_context():
        try:
            today = date.today()
            tomorrow = today + timedelta(days=1)

            # 1. Appointments tomorrow (1-day reminder)
            appts_tomorrow = Appointment.query.filter(
                Appointment.appointment_date == tomorrow,
                Appointment.status == AppointmentStatus.SCHEDULED,
                Appointment.reminder_1day_sent == False
            ).all()

            for appt in appts_tomorrow:
                notify_appointment_reminder(appt, is_day_of=False)
                appt.reminder_1day_sent = True

            # 2. Appointments today (Day-of reminder)
            appts_today = Appointment.query.filter(
                Appointment.appointment_date == today,
                Appointment.status == AppointmentStatus.SCHEDULED,
                Appointment.reminder_dayof_sent == False
            ).all()

            for appt in appts_today:
                notify_appointment_reminder(appt, is_day_of=True)
                appt.reminder_dayof_sent = True

            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error in process_appointments_job: {e}")

def process_low_inventory_job(app):
    """Checks for low inventory medications and triggers alerts."""
    with app.app_context():
        try:
            low_meds = Medication.query.filter(
                Medication.is_active == True,
                Medication.current_inventory <= Medication.refill_alert_threshold
            ).all()

            today = date.today()
            for med in low_meds:
                # Check if alert was sent in last 24h to prevent spam
                already_sent = Notification.query.filter(
                    Notification.profile_id == med.profile_id,
                    Notification.type == NotificationType.LOW_INVENTORY,
                    Notification.title.like(f"%{med.name}%"),
                    db.func.date(Notification.created_at) == today
                ).first()

                if not already_sent:
                    notify_low_inventory(med)
        except Exception as e:
            app.logger.error(f"Error in process_low_inventory_job: {e}")

def init_scheduler(app):
    """Registers periodic jobs and starts the background scheduler."""
    if not app.config.get("ENABLE_BACKGROUND_SCHEDULER", True):
        app.logger.info("Background scheduler disabled in configuration.")
        return

    interval_sec = app.config.get("CHECK_DOSE_INTERVAL_SECONDS", 60)

    # Job 1: Check due doses & missed doses
    background_scheduler.add_job(
        id="check_due_medications",
        func=process_due_medications_job,
        args=[app],
        trigger="interval",
        seconds=interval_sec,
        replace_existing=True
    )

    # Job 2: Check upcoming appointments (every 10 minutes)
    background_scheduler.add_job(
        id="check_appointments",
        func=process_appointments_job,
        args=[app],
        trigger="interval",
        minutes=10,
        replace_existing=True
    )

    # Job 3: Check low inventory (once every hour)
    background_scheduler.add_job(
        id="check_low_inventory",
        func=process_low_inventory_job,
        args=[app],
        trigger="interval",
        hours=1,
        replace_existing=True
    )

    if not background_scheduler.running:
        background_scheduler.start()
        app.logger.info("APScheduler started successfully with periodic jobs.")

from datetime import datetime, date, timezone
from app.extensions import db
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationPreference
from app.models.profile import ElderlyProfile, ProfileMembership, MembershipStatus
from app.models.medication import Medication, MedicationSchedule
from app.models.adherence import MedicationLog
from app.models.appointment import Appointment
from app.services.email_service import send_resend_email, render_email_template

def notify_upcoming_dose(log: MedicationLog):
    """Sends a reminder to the elderly user and subscribed caregivers for an upcoming dose."""
    med = log.medication
    profile = med.profile
    elderly_user = profile.user

    # Determine recipient users
    recipients = []
    if elderly_user and elderly_user.email:
        pref = NotificationPreference.query.filter_by(user_id=elderly_user.id).first()
        if not pref or pref.email_medication_reminders:
            recipients.append((elderly_user, "Elderly"))

    # Also notify active family members who subscribed
    memberships = ProfileMembership.query.filter_by(profile_id=profile.id, status=MembershipStatus.ACTIVE).all()
    for m in memberships:
        u = m.user
        if u and u.email:
            pref = NotificationPreference.query.filter_by(user_id=u.id).first()
            if not pref or pref.email_medication_reminders:
                recipients.append((u, m.role))

    for user, relation in recipients:
        subject = f"Medication Reminder: {med.name} at {log.scheduled_time}"
        content = f"""
        <p>This is a friendly reminder for <strong>{profile.full_name}</strong>'s scheduled medication:</p>
        <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; margin: 16px 0; border-radius: 4px;">
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #1e3a8a;">{med.name} ({med.dosage} {med.unit})</p>
            <p style="margin: 6px 0 0 0; color: #1e40af;">Scheduled Time: <strong>{log.scheduled_time}</strong></p>
            {f'<p style="margin: 6px 0 0 0; color: #475569;">Instructions: <em>{med.instructions}</em></p>' if med.instructions else ''}
        </div>
        <p>Please remember to mark this dose as taken in your ElderCare app once administered.</p>
        """
        html = render_email_template(
            header_title="Medication Reminder",
            greeting=f"Hello {user.full_name},",
            main_content_html=content,
            action_button_text="Open ElderCare Dashboard",
            action_button_url="http://localhost:5173/dashboard"
        )
        send_resend_email(
            to_email=user.email,
            subject=subject,
            html_body=html,
            notification_type=NotificationType.MED_REMINDER,
            user_id=user.id,
            profile_id=profile.id
        )

def notify_missed_dose_alert(log: MedicationLog):
    """Sends an urgent escalation email to family and caretakers when a dose is overdue and marked missed."""
    med = log.medication
    profile = med.profile

    # Find all active caregivers and family members
    memberships = ProfileMembership.query.filter_by(profile_id=profile.id, status=MembershipStatus.ACTIVE).all()
    recipients = []
    for m in memberships:
        u = m.user
        if u and u.email:
            pref = NotificationPreference.query.filter_by(user_id=u.id).first()
            if not pref or pref.email_missed_dose_alerts:
                recipients.append(u)

    # Also notify senior user if active
    if profile.user and profile.user.email:
        recipients.append(profile.user)

    for user in recipients:
        subject = f"ElderCare Alert: Missed Dose for {profile.full_name}"
        content = f"""
        <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; margin: 16px 0; border-radius: 4px;">
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #991b1b;">Missed Medication Alert</p>
            <p style="margin: 8px 0 0 0; color: #7f1d1d;">
                <strong>{profile.full_name}</strong>'s scheduled dose of <strong>{med.name} ({med.dosage} {med.unit})</strong> 
                scheduled for <strong>{log.scheduled_time}</strong> on <strong>{log.scheduled_date.isoformat()}</strong> 
                has not been confirmed.
            </p>
        </div>
        <p>Please check in with {profile.full_name} to ensure their well-being and confirm if the dose was administered.</p>
        """
        html = render_email_template(
            header_title="Missed Medication Alert",
            greeting=f"Hello {user.full_name},",
            main_content_html=content,
            action_button_text="View Care Dashboard",
            action_button_url="http://localhost:5173/dashboard"
        )
        send_resend_email(
            to_email=user.email,
            subject=subject,
            html_body=html,
            notification_type=NotificationType.MISSED_DOSE,
            user_id=user.id,
            profile_id=profile.id
        )

def notify_low_inventory(med: Medication):
    """Sends a refill reminder when medication stock dips to or below threshold."""
    profile = med.profile
    memberships = ProfileMembership.query.filter_by(profile_id=profile.id, status=MembershipStatus.ACTIVE).all()
    recipients = [m.user for m in memberships if m.user and m.user.email]
    if profile.user and profile.user.email:
        recipients.append(profile.user)

    for user in recipients:
        subject = f"Refill Reminder: {med.name} is running low"
        content = f"""
        <p>The medication stock for <strong>{profile.full_name}</strong> is running low:</p>
        <div style="background-color: #fffbeb; border-left: 4px solid #f59e0b; padding: 16px; margin: 16px 0; border-radius: 4px;">
            <p style="margin: 0; font-weight: bold; color: #92400e; font-size: 16px;">{med.name} ({med.dosage} {med.unit})</p>
            <p style="margin: 6px 0 0 0; color: #b45309;">Current Stock: <strong>{med.current_inventory} doses remaining</strong> (Alert threshold: {med.refill_alert_threshold})</p>
        </div>
        <p>Please arrange a pharmacy refill soon to prevent disruption in care.</p>
        """
        html = render_email_template(
            header_title="Refill Alert",
            greeting=f"Hello {user.full_name},",
            main_content_html=content,
            action_button_text="Manage Medications",
            action_button_url="http://localhost:5173/medications"
        )
        send_resend_email(
            to_email=user.email,
            subject=subject,
            html_body=html,
            notification_type=NotificationType.LOW_INVENTORY,
            user_id=user.id,
            profile_id=profile.id
        )

def notify_appointment_reminder(appt: Appointment, is_day_of: bool = False):
    """Sends 24-hour advance or day-of appointment reminder."""
    profile = appt.profile
    recipients = []
    if profile.user and profile.user.email:
        recipients.append(profile.user)

    memberships = ProfileMembership.query.filter_by(profile_id=profile.id, status=MembershipStatus.ACTIVE).all()
    for m in memberships:
        if m.user and m.user.email:
            recipients.append(m.user)

    timing_label = "Today" if is_day_of else f"Tomorrow ({appt.appointment_date.isoformat()})"
    subject = f"Appointment Reminder: Dr. {appt.doctor_name} ({timing_label})"

    for user in recipients:
        content = f"""
        <p>Upcoming medical appointment for <strong>{profile.full_name}</strong>:</p>
        <div style="background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 16px; margin: 16px 0; border-radius: 4px;">
            <p style="margin: 0; font-weight: bold; color: #166534; font-size: 18px;">Dr. {appt.doctor_name} - {appt.specialty or 'Consultation'}</p>
            <p style="margin: 6px 0 0 0; color: #15803d;">Date & Time: <strong>{appt.appointment_date.isoformat()} at {appt.appointment_time}</strong></p>
            <p style="margin: 6px 0 0 0; color: #15803d;">Location / Clinic: <strong>{appt.hospital_clinic or ''} ({appt.location or 'In-person'})</strong></p>
            {f'<p style="margin: 6px 0 0 0; color: #475569;">Notes: <em>{appt.notes}</em></p>' if appt.notes else ''}
        </div>
        """
        html = render_email_template(
            header_title="Appointment Reminder",
            greeting=f"Hello {user.full_name},",
            main_content_html=content,
            action_button_text="View Appointments",
            action_button_url="http://localhost:5173/appointments"
        )
        send_resend_email(
            to_email=user.email,
            subject=subject,
            html_body=html,
            notification_type=NotificationType.APPT_REMINDER_DAYOF if is_day_of else NotificationType.APPT_REMINDER_1DAY,
            user_id=user.id,
            profile_id=profile.id
        )

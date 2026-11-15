from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.notification import Notification, NotificationPreference, NotificationType
from app.utils.validators import api_response, api_error
from app.utils.decorators import get_current_user
from app.services.email_service import send_resend_email, render_email_template

notification_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notification_bp.route("", methods=["GET"])
@jwt_required()
def list_notifications():
    """Lists notifications and email dispatch logs for current user."""
    user = get_current_user()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(50).all()
    
    # Return email provider status for UI transparency
    resend_key = current_app.config.get("RESEND_API_KEY", "")
    is_configured = bool(resend_key and resend_key.startswith("re_") and resend_key != "re_your_api_key_here")

    return api_response({
        "email_service_status": {
            "provider": "Resend API",
            "is_configured": is_configured,
            "mail_from": current_app.config.get("MAIL_FROM")
        },
        "notifications": [n.to_dict() for n in notifications]
    })

@notification_bp.route("/<notification_id>/read", methods=["PATCH"])
@jwt_required()
def mark_read(notification_id):
    user = get_current_user()
    notif = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notif:
        return api_error("Notification not found", "NOT_FOUND", 404)

    notif.is_read = True
    db.session.commit()
    return api_response(notif.to_dict(), "Notification marked as read")

@notification_bp.route("/preferences", methods=["GET"])
@jwt_required()
def get_preferences():
    user = get_current_user()
    pref = NotificationPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.session.add(pref)
        db.session.commit()
    return api_response(pref.to_dict())

@notification_bp.route("/preferences", methods=["PUT"])
@jwt_required()
def update_preferences():
    user = get_current_user()
    pref = NotificationPreference.query.filter_by(user_id=user.id).first()
    if not pref:
        pref = NotificationPreference(user_id=user.id)
        db.session.add(pref)

    data = request.get_json() or {}
    if "email_medication_reminders" in data:
        pref.email_medication_reminders = bool(data["email_medication_reminders"])
    if "email_missed_dose_alerts" in data:
        pref.email_missed_dose_alerts = bool(data["email_missed_dose_alerts"])
    if "email_appointment_reminders" in data:
        pref.email_appointment_reminders = bool(data["email_appointment_reminders"])
    if "email_daily_summary" in data:
        pref.email_daily_summary = bool(data["email_daily_summary"])

    db.session.commit()
    return api_response(pref.to_dict(), "Notification preferences updated")

@notification_bp.route("/test-email", methods=["POST"])
@jwt_required()
def send_test_email():
    """Triggers a test email via Resend and reports actual delivery status."""
    user = get_current_user()
    data = request.get_json() or {}
    target_email = user.email

    subject = "ElderCare Notification Test"
    content = f"""
    <p>This is a test notification from your <strong>ElderCare</strong> healthcare platform.</p>
    <p>Your notification settings and email dispatch pipeline are active and functioning correctly.</p>
    <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 12px; border-radius: 6px; margin: 16px 0;">
        <span style="color: #166534; font-weight: bold;">System Status: Operational</span>
    </div>
    """
    html = render_email_template(
        header_title="System Test",
        greeting=f"Hello {user.full_name},",
        main_content_html=content,
        action_button_text="Go to Dashboard",
        action_button_url="http://localhost:5173/dashboard"
    )

    notif = send_resend_email(
        to_email=target_email,
        subject=subject,
        html_body=html,
        notification_type="SYSTEM_TEST",
        user_id=user.id
    )

    return api_response(notif.to_dict(), f"Test notification recorded with status: {notif.status}")

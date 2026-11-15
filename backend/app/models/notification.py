import uuid
from datetime import datetime, timezone
from app.extensions import db

class NotificationType:
    MED_REMINDER = "MED_REMINDER"
    MISSED_DOSE = "MISSED_DOSE"
    DAILY_SUMMARY = "DAILY_SUMMARY"
    APPT_REMINDER_1DAY = "APPT_REMINDER_1DAY"
    APPT_REMINDER_DAYOF = "APPT_REMINDER_DAYOF"
    INVITATION = "INVITATION"
    LOW_INVENTORY = "LOW_INVENTORY"
    ALL = [MED_REMINDER, MISSED_DOSE, DAILY_SUMMARY, APPT_REMINDER_1DAY, APPT_REMINDER_DAYOF, INVITATION, LOW_INVENTORY]

class NotificationChannel:
    EMAIL = "EMAIL"
    IN_APP = "IN_APP"

class NotificationStatus:
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"
    SIMULATED_NOT_CONFIGURED = "SIMULATED_NOT_CONFIGURED"

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    profile_id = db.Column(db.String(36), db.ForeignKey("elderly_profiles.id", ondelete="SET NULL"), nullable=True)
    type = db.Column(db.String(30), nullable=False)
    channel = db.Column(db.String(20), nullable=False, default=NotificationChannel.EMAIL)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    recipient_email = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), nullable=False, default=NotificationStatus.QUEUED, index=True)
    error_message = db.Column(db.Text, nullable=True)
    delivery_attempts = db.Column(db.Integer, nullable=False, default=0)
    sent_at = db.Column(db.DateTime, nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "profile_id": self.profile_id,
            "type": self.type,
            "channel": self.channel,
            "title": self.title,
            "message": self.message,
            "recipient_email": self.recipient_email,
            "status": self.status,
            "error_message": self.error_message,
            "delivery_attempts": self.delivery_attempts,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class NotificationPreference(db.Model):
    __tablename__ = "notification_preferences"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    email_medication_reminders = db.Column(db.Boolean, default=True, nullable=False)
    email_missed_dose_alerts = db.Column(db.Boolean, default=True, nullable=False)
    email_appointment_reminders = db.Column(db.Boolean, default=True, nullable=False)
    email_daily_summary = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_medication_reminders": self.email_medication_reminders,
            "email_missed_dose_alerts": self.email_missed_dose_alerts,
            "email_appointment_reminders": self.email_appointment_reminders,
            "email_daily_summary": self.email_daily_summary,
        }

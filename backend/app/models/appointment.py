import uuid
from datetime import datetime, timezone
from app.extensions import db

class AppointmentStatus:
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    ALL = [SCHEDULED, COMPLETED, CANCELLED]

class AppointmentType:
    IN_PERSON = "IN_PERSON"
    VIRTUAL = "VIRTUAL"
    HOME_VISIT = "HOME_VISIT"
    ALL = [IN_PERSON, VIRTUAL, HOME_VISIT]

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey("elderly_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    doctor_name = db.Column(db.String(120), nullable=False)
    specialty = db.Column(db.String(100), nullable=True)  # e.g., Cardiologist, Geriatrician
    hospital_clinic = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(255), nullable=True)  # Physical address or Telehealth URL
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    appointment_time = db.Column(db.String(10), nullable=False)  # HH:MM
    appointment_type = db.Column(db.String(30), nullable=False, default=AppointmentType.IN_PERSON)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=AppointmentStatus.SCHEDULED, index=True)
    reminder_1day_sent = db.Column(db.Boolean, default=False, nullable=False)
    reminder_dayof_sent = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "created_by_user_id": self.created_by_user_id,
            "created_by_name": self.created_by.full_name if self.created_by else None,
            "doctor_name": self.doctor_name,
            "specialty": self.specialty,
            "hospital_clinic": self.hospital_clinic,
            "location": self.location,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "appointment_time": self.appointment_time,
            "appointment_type": self.appointment_type,
            "notes": self.notes,
            "status": self.status,
            "reminder_1day_sent": self.reminder_1day_sent,
            "reminder_dayof_sent": self.reminder_dayof_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

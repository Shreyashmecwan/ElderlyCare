import uuid
from datetime import datetime, timezone
from app.extensions import db

class FrequencyType:
    DAILY = "DAILY"
    SPECIFIC_DAYS = "SPECIFIC_DAYS"
    AS_NEEDED = "AS_NEEDED"
    ALL = [DAILY, SPECIFIC_DAYS, AS_NEEDED]

class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey("elderly_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    dosage = db.Column(db.String(50), nullable=False)  # e.g., "500", "1"
    unit = db.Column(db.String(30), nullable=False, default="mg")  # e.g., mg, ml, tablet, capsule
    instructions = db.Column(db.Text, nullable=True)  # e.g., "Take with food"
    prescribing_doctor = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    frequency_type = db.Column(db.String(30), nullable=False, default=FrequencyType.DAILY)
    current_inventory = db.Column(db.Integer, nullable=False, default=30)
    refill_alert_threshold = db.Column(db.Integer, nullable=False, default=7)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    schedules = db.relationship("MedicationSchedule", backref="medication", cascade="all, delete-orphan", lazy="selectin")
    logs = db.relationship("MedicationLog", backref="medication", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self, include_schedules=True):
        data = {
            "id": self.id,
            "profile_id": self.profile_id,
            "name": self.name,
            "dosage": self.dosage,
            "unit": self.unit,
            "strength": f"{self.dosage} {self.unit}".strip(),
            "instructions": self.instructions,
            "prescribing_doctor": self.prescribing_doctor,
            "notes": self.notes,
            "frequency_type": self.frequency_type,
            "current_inventory": self.current_inventory,
            "refill_alert_threshold": self.refill_alert_threshold,
            "needs_refill": self.current_inventory <= self.refill_alert_threshold,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_schedules:
            data["schedules"] = [s.to_dict() for s in self.schedules]
        return data

class MedicationSchedule(db.Model):
    __tablename__ = "medication_schedules"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medication_id = db.Column(db.String(36), db.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    time_of_day = db.Column(db.String(10), nullable=False)  # HH:MM format, e.g., "08:00"
    label = db.Column(db.String(50), nullable=True)  # e.g., "Morning", "Breakfast", "Evening"
    days_of_week = db.Column(db.String(50), nullable=False, default="DAILY")  # "DAILY" or "MON,TUE,WED"
    dose_quantity = db.Column(db.String(30), nullable=False, default="1 dose")
    reminder_enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    logs = db.relationship("MedicationLog", backref="schedule", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "time_of_day": self.time_of_day,
            "label": self.label,
            "days_of_week": self.days_of_week,
            "dose_quantity": self.dose_quantity,
            "reminder_enabled": self.reminder_enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

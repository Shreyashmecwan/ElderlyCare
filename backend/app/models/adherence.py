import uuid
from datetime import datetime, timezone
from app.extensions import db

class AdherenceStatus:
    UPCOMING = "UPCOMING"
    TAKEN = "TAKEN"
    SKIPPED = "SKIPPED"
    MISSED = "MISSED"
    ALL = [UPCOMING, TAKEN, SKIPPED, MISSED]

class MedicationLog(db.Model):
    __tablename__ = "medication_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medication_id = db.Column(db.String(36), db.ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = db.Column(db.String(36), db.ForeignKey("medication_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    scheduled_time = db.Column(db.String(10), nullable=False)  # HH:MM
    status = db.Column(db.String(20), nullable=False, default=AdherenceStatus.UPCOMING, index=True)
    taken_at = db.Column(db.DateTime, nullable=True)
    recorded_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    recorded_by = db.relationship("User", foreign_keys=[recorded_by_user_id])

    __table_args__ = (
        db.UniqueConstraint("schedule_id", "scheduled_date", name="uq_schedule_date_log"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "medication_name": self.medication.name if self.medication else None,
            "dosage": self.medication.dosage if self.medication else None,
            "unit": self.medication.unit if self.medication else None,
            "instructions": self.medication.instructions if self.medication else None,
            "schedule_id": self.schedule_id,
            "label": self.schedule.label if self.schedule else None,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "scheduled_time": self.scheduled_time,
            "status": self.status,
            "taken_at": self.taken_at.isoformat() if self.taken_at else None,
            "recorded_by_user_id": self.recorded_by_user_id,
            "recorded_by_name": self.recorded_by.full_name if self.recorded_by else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

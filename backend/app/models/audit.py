import uuid
from datetime import datetime, timezone
from app.extensions import db

class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False)  # e.g., "RECORD_DOSE", "CORRECT_ADHERENCE", "CREATE_MEDICATION"
    entity_type = db.Column(db.String(50), nullable=False)  # e.g., "MedicationLog", "Medication", "Appointment"
    entity_id = db.Column(db.String(36), nullable=False)
    details = db.Column(db.Text, nullable=True)  # JSON or text description of old vs new state
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else "System",
            "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

import uuid
import secrets
from datetime import datetime, timezone, timedelta
from app.extensions import db

class MembershipPermission:
    FULL_ACCESS = "FULL_ACCESS"
    VIEW_ONLY = "VIEW_ONLY"
    ALL = [FULL_ACCESS, VIEW_ONLY]

class MembershipStatus:
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

class InvitationStatus:
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

class ElderlyProfile(db.Model):
    __tablename__ = "elderly_profiles"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    emergency_contact_name = db.Column(db.String(120), nullable=True)
    emergency_contact_phone = db.Column(db.String(30), nullable=True)
    emergency_contact_relation = db.Column(db.String(50), nullable=True)
    medical_notes = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    timezone = db.Column(db.String(50), nullable=False, default="UTC")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    memberships = db.relationship("ProfileMembership", backref="profile", cascade="all, delete-orphan", lazy="dynamic")
    invitations = db.relationship("Invitation", backref="profile", cascade="all, delete-orphan", lazy="dynamic")
    medications = db.relationship("Medication", backref="profile", cascade="all, delete-orphan", lazy="dynamic")
    appointments = db.relationship("Appointment", backref="profile", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_name": self.full_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "emergency_contact_relation": self.emergency_contact_relation,
            "medical_notes": self.medical_notes,
            "allergies": self.allergies,
            "address": self.address,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

class ProfileMembership(db.Model):
    __tablename__ = "profile_memberships"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey("elderly_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # FAMILY or CARETAKER
    relationship_title = db.Column(db.String(50), nullable=True)  # e.g., Daughter, Son, Nurse
    permission = db.Column(db.String(20), nullable=False, default=MembershipPermission.FULL_ACCESS)
    status = db.Column(db.String(20), nullable=False, default=MembershipStatus.ACTIVE)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("profile_id", "user_id", name="uq_profile_user_membership"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "user_id": self.user_id,
            "user_name": self.user.full_name if self.user else None,
            "user_email": self.user.email if self.user else None,
            "role": self.role,
            "relationship_title": self.relationship_title,
            "permission": self.permission,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Invitation(db.Model):
    __tablename__ = "invitations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(36), db.ForeignKey("elderly_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    passcode = db.Column(db.String(16), unique=True, nullable=False, index=True)  # e.g. ELDER-9281
    recipient_email = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), nullable=False)  # FAMILY or CARETAKER
    relationship_title = db.Column(db.String(50), nullable=True)
    permission = db.Column(db.String(20), nullable=False, default=MembershipPermission.FULL_ACCESS)
    status = db.Column(db.String(20), nullable=False, default=InvitationStatus.PENDING)
    expires_at = db.Column(db.DateTime, nullable=False)
    accepted_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @staticmethod
    def generate_passcode(prefix="CARE"):
        suffix = "".join(secrets.choice("23456789ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6))
        return f"{prefix}-{suffix}"

    @property
    def is_expired(self):
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "passcode": self.passcode,
            "recipient_email": self.recipient_email,
            "role": self.role,
            "relationship_title": self.relationship_title,
            "permission": self.permission,
            "status": "EXPIRED" if self.is_expired and self.status == InvitationStatus.PENDING else self.status,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

import uuid
from datetime import datetime, timezone
import bcrypt
from app.extensions import db

class UserRole:
    ELDERLY = "ELDERLY"
    FAMILY = "FAMILY"
    CARETAKER = "CARETAKER"
    ALL = [ELDERLY, FAMILY, CARETAKER]

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(30), nullable=True)
    role = db.Column(db.String(20), nullable=False, default=UserRole.ELDERLY)
    timezone = db.Column(db.String(50), nullable=False, default="UTC")
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    elderly_profile = db.relationship("ElderlyProfile", backref="user", uselist=False, foreign_keys="ElderlyProfile.user_id", cascade="all, delete-orphan")
    memberships = db.relationship("ProfileMembership", backref="user", foreign_keys="ProfileMembership.user_id", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", foreign_keys="Notification.user_id", cascade="all, delete-orphan")
    notification_preferences = db.relationship("NotificationPreference", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password: str):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "role": self.role,
            "timezone": self.timezone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "has_profile": self.elderly_profile is not None,
            "profile_id": self.elderly_profile.id if self.elderly_profile else None
        }

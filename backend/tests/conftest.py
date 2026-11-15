import os
import sys
import pytest

# Ensure backend root is on sys.path
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile, ProfileMembership, MembershipPermission, MembershipStatus
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def elderly_user(app):
    with app.app_context():
        user = User(
            email="test.elderly@example.com",
            full_name="Grandma Betty",
            role=UserRole.ELDERLY,
            timezone="UTC"
        )
        user.set_password("TestPass123!")
        db.session.add(user)
        db.session.flush()

        profile = ElderlyProfile(
            user_id=user.id,
            full_name="Grandma Betty",
            emergency_contact_name="Bob Betty",
            emergency_contact_phone="1234567890",
            emergency_contact_relation="Son"
        )
        db.session.add(profile)
        db.session.commit()
        return {"id": user.id, "email": user.email, "profile_id": profile.id}

@pytest.fixture
def family_user(app):
    with app.app_context():
        user = User(
            email="test.family@example.com",
            full_name="Bob Betty",
            role=UserRole.FAMILY,
            timezone="UTC"
        )
        user.set_password("TestPass123!")
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "email": user.email}

@pytest.fixture
def caretaker_user(app):
    with app.app_context():
        user = User(
            email="test.nurse@example.com",
            full_name="Nurse Alex",
            role=UserRole.CARETAKER,
            timezone="UTC"
        )
        user.set_password("TestPass123!")
        db.session.add(user)
        db.session.commit()
        return {"id": user.id, "email": user.email}

@pytest.fixture
def elderly_auth_headers(app, elderly_user):
    with app.app_context():
        token = create_access_token(identity=elderly_user["id"])
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@pytest.fixture
def family_auth_headers(app, family_user):
    with app.app_context():
        token = create_access_token(identity=family_user["id"])
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@pytest.fixture
def caretaker_auth_headers(app, caretaker_user):
    with app.app_context():
        token = create_access_token(identity=caretaker_user["id"])
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

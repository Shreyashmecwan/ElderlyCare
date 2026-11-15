import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from datetime import date, datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models.user import User, UserRole
from app.models.profile import ElderlyProfile, ProfileMembership, Invitation, MembershipPermission, MembershipStatus, InvitationStatus
from app.models.medication import Medication, MedicationSchedule, FrequencyType
from app.models.adherence import MedicationLog, AdherenceStatus
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.notification import Notification, NotificationType, NotificationStatus, NotificationPreference

def seed_database():
    app = create_app("development")
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Creating synthetic demo users...")
        # 1. Elderly User
        eleanor = User(
            email="eleanor.vance@example.com",
            full_name="Eleanor Vance",
            phone_number="+1-555-0142",
            role=UserRole.ELDERLY,
            timezone="America/New_York"
        )
        eleanor.set_password("Password123!")
        db.session.add(eleanor)
        db.session.flush()

        db.session.add(NotificationPreference(user_id=eleanor.id))

        # Elderly Profile
        profile = ElderlyProfile(
            user_id=eleanor.id,
            full_name="Eleanor Vance",
            date_of_birth=date(1948, 6, 12),
            gender="Female",
            blood_group="O+",
            emergency_contact_name="Sarah Vance (Daughter)",
            emergency_contact_phone="+1-555-0199",
            emergency_contact_relation="Daughter",
            medical_notes="Managed hypertension, Type 2 diabetes, mild osteoarthritis in left knee.",
            allergies="Penicillin, Sulfa medications",
            address="742 Evergreen Terrace, Springfield, MA",
            timezone="America/New_York"
        )
        db.session.add(profile)
        db.session.flush()

        # 2. Family Member User
        sarah = User(
            email="sarah.vance@example.com",
            full_name="Sarah Vance",
            phone_number="+1-555-0199",
            role=UserRole.FAMILY,
            timezone="America/New_York"
        )
        sarah.set_password("Password123!")
        db.session.add(sarah)
        db.session.flush()
        db.session.add(NotificationPreference(user_id=sarah.id))

        # 3. Professional Caretaker User
        david = User(
            email="david.chen@example.com",
            full_name="Nurse David Chen",
            phone_number="+1-555-0231",
            role=UserRole.CARETAKER,
            timezone="America/New_York"
        )
        david.set_password("Password123!")
        db.session.add(david)
        db.session.flush()
        db.session.add(NotificationPreference(user_id=david.id))

        print("Linking profile memberships...")
        # Link Sarah as Family Member
        m_sarah = ProfileMembership(
            profile_id=profile.id,
            user_id=sarah.id,
            role=UserRole.FAMILY,
            relationship_title="Daughter",
            permission=MembershipPermission.FULL_ACCESS,
            status=MembershipStatus.ACTIVE
        )
        db.session.add(m_sarah)

        # Link David as Caretaker
        m_david = ProfileMembership(
            profile_id=profile.id,
            user_id=david.id,
            role=UserRole.CARETAKER,
            relationship_title="Home Health Nurse",
            permission=MembershipPermission.FULL_ACCESS,
            status=MembershipStatus.ACTIVE
        )
        db.session.add(m_david)

        print("Creating active invitation passcodes...")
        invite_fam = Invitation(
            profile_id=profile.id,
            invited_by_user_id=eleanor.id,
            passcode="FAM-4310",
            recipient_email="relative@example.com",
            role=UserRole.FAMILY,
            relationship_title="Family Member",
            permission=MembershipPermission.FULL_ACCESS,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(days=14)
        )
        invite_care = Invitation(
            profile_id=profile.id,
            invited_by_user_id=eleanor.id,
            passcode="CARE-7892",
            recipient_email="nurse2@example.com",
            role=UserRole.CARETAKER,
            relationship_title="Relief Nurse",
            permission=MembershipPermission.FULL_ACCESS,
            status=InvitationStatus.PENDING,
            expires_at=datetime.now(timezone.utc) + timedelta(days=14)
        )
        db.session.add_all([invite_fam, invite_care])

        print("Creating medications and schedules...")
        # Med 1: Metformin 500mg
        med_metformin = Medication(
            profile_id=profile.id,
            name="Metformin",
            dosage="500",
            unit="mg",
            instructions="Take with meals to prevent stomach upset.",
            prescribing_doctor="Dr. Anthony Fauci",
            notes="For Type 2 Diabetes maintenance",
            frequency_type=FrequencyType.DAILY,
            current_inventory=52,
            refill_alert_threshold=14,
            start_date=date.today() - timedelta(days=60),
            is_active=True
        )
        db.session.add(med_metformin)
        db.session.flush()

        s1_met = MedicationSchedule(
            medication_id=med_metformin.id,
            time_of_day="08:00",
            label="Breakfast",
            days_of_week="DAILY",
            dose_quantity="1 tablet",
            reminder_enabled=True
        )
        s2_met = MedicationSchedule(
            medication_id=med_metformin.id,
            time_of_day="19:30",
            label="Dinner",
            days_of_week="DAILY",
            dose_quantity="1 tablet",
            reminder_enabled=True
        )
        db.session.add_all([s1_met, s2_met])

        # Med 2: Lisinopril 10mg
        med_lisinopril = Medication(
            profile_id=profile.id,
            name="Lisinopril",
            dosage="10",
            unit="mg",
            instructions="Take every morning with a full glass of water.",
            prescribing_doctor="Dr. Robert Hayes",
            notes="Blood pressure management",
            frequency_type=FrequencyType.DAILY,
            current_inventory=21,
            refill_alert_threshold=7,
            start_date=date.today() - timedelta(days=45),
            is_active=True
        )
        db.session.add(med_lisinopril)
        db.session.flush()

        s_lis = MedicationSchedule(
            medication_id=med_lisinopril.id,
            time_of_day="08:00",
            label="Morning",
            days_of_week="DAILY",
            dose_quantity="1 tablet",
            reminder_enabled=True
        )
        db.session.add(s_lis)

        # Med 3: Atorvastatin 20mg
        med_ator = Medication(
            profile_id=profile.id,
            name="Atorvastatin",
            dosage="20",
            unit="mg",
            instructions="Take at bedtime.",
            prescribing_doctor="Dr. Robert Hayes",
            notes="Cholesterol control",
            frequency_type=FrequencyType.DAILY,
            current_inventory=8,  # Triggers low refill alert!
            refill_alert_threshold=10,
            start_date=date.today() - timedelta(days=30),
            is_active=True
        )
        db.session.add(med_ator)
        db.session.flush()

        s_ator = MedicationSchedule(
            medication_id=med_ator.id,
            time_of_day="21:00",
            label="Night / Bedtime",
            days_of_week="DAILY",
            dose_quantity="1 tablet",
            reminder_enabled=True
        )
        db.session.add(s_ator)

        # Med 4: Vitamin D3 2000 IU
        med_vitd = Medication(
            profile_id=profile.id,
            name="Vitamin D3",
            dosage="2000",
            unit="IU",
            instructions="Take once daily after morning meal.",
            prescribing_doctor="Dr. Anthony Fauci",
            notes="Bone and joint health supplement",
            frequency_type=FrequencyType.DAILY,
            current_inventory=80,
            refill_alert_threshold=15,
            start_date=date.today() - timedelta(days=90),
            is_active=True
        )
        db.session.add(med_vitd)
        db.session.flush()

        s_vitd = MedicationSchedule(
            medication_id=med_vitd.id,
            time_of_day="09:00",
            label="Post-Breakfast",
            days_of_week="DAILY",
            dose_quantity="1 capsule",
            reminder_enabled=True
        )
        db.session.add(s_vitd)

        db.session.commit()

        print("Generating historical adherence logs for realistic analytics...")
        all_schedules = [
            (med_metformin, s1_met),
            (med_metformin, s2_met),
            (med_lisinopril, s_lis),
            (med_ator, s_ator),
            (med_vitd, s_vitd)
        ]

        today = date.today()
        # Seed 7 days of historical logs
        for i in range(7, 0, -1):
            past_date = today - timedelta(days=i)
            for med, sched in all_schedules:
                # Realistic distribution: mostly taken, 1 skipped on day -3, 1 missed on day -5
                if i == 3 and sched.time_of_day == "21:00":
                    status = AdherenceStatus.SKIPPED
                    taken_time = None
                    notes = "Doctor advised pausing for fasting blood test"
                elif i == 5 and sched.time_of_day == "19:30":
                    status = AdherenceStatus.MISSED
                    taken_time = None
                    notes = "Missed due to evening family outing"
                else:
                    status = AdherenceStatus.TAKEN
                    taken_time = datetime.combine(past_date, datetime.strptime(sched.time_of_day, "%H:%M").time())
                    notes = "Administered on time"

                log = MedicationLog(
                    medication_id=med.id,
                    schedule_id=sched.id,
                    scheduled_date=past_date,
                    scheduled_time=sched.time_of_day,
                    status=status,
                    taken_at=taken_time,
                    recorded_by_user_id=eleanor.id if i % 2 == 0 else david.id,
                    notes=notes
                )
                db.session.add(log)

        # Seed today's logs: morning doses TAKEN, evening doses UPCOMING
        for med, sched in all_schedules:
            if sched.time_of_day in ["08:00", "09:00"]:
                status = AdherenceStatus.TAKEN
                taken_time = datetime.now(timezone.utc)
                notes = "Taken with breakfast"
            else:
                status = AdherenceStatus.UPCOMING
                taken_time = None
                notes = None

            log = MedicationLog(
                medication_id=med.id,
                schedule_id=sched.id,
                scheduled_date=today,
                scheduled_time=sched.time_of_day,
                status=status,
                taken_at=taken_time,
                recorded_by_user_id=eleanor.id if status == AdherenceStatus.TAKEN else None,
                notes=notes
            )
            db.session.add(log)

        print("Creating doctor appointments...")
        # 1. Upcoming Cardiology appointment in 4 days
        appt1 = Appointment(
            profile_id=profile.id,
            created_by_user_id=sarah.id,
            doctor_name="Robert Hayes",
            specialty="Cardiologist",
            hospital_clinic="Springfield Memorial Heart Institute",
            location="Suite 400, 100 Medical Center Way",
            appointment_date=today + timedelta(days=4),
            appointment_time="10:30",
            appointment_type=AppointmentType.IN_PERSON,
            notes="6-month blood pressure review and EKG follow-up. Bring recent BP logs.",
            status=AppointmentStatus.SCHEDULED
        )

        # 2. Upcoming Laboratory Blood Test in 12 days
        appt2 = Appointment(
            profile_id=profile.id,
            created_by_user_id=david.id,
            doctor_name="Diagnostic Services",
            specialty="Phlebotomy / Lab Work",
            hospital_clinic="Quest Diagnostics Labs",
            location="55 River Street, Springfield",
            appointment_date=today + timedelta(days=12),
            appointment_time="08:15",
            appointment_type=AppointmentType.IN_PERSON,
            notes="Fasting HbA1c, lipid panel, and kidney function tests. Fasting for 10 hours required.",
            status=AppointmentStatus.SCHEDULED
        )

        # 3. Past Ophthalmology Checkup
        appt3 = Appointment(
            profile_id=profile.id,
            created_by_user_id=sarah.id,
            doctor_name="Elena Rostova",
            specialty="Ophthalmologist",
            hospital_clinic="Springfield Eye Center",
            location="120 Main Street",
            appointment_date=today - timedelta(days=14),
            appointment_time="14:00",
            appointment_type=AppointmentType.IN_PERSON,
            notes="Annual diabetic retinal evaluation. No signs of retinopathy.",
            status=AppointmentStatus.COMPLETED
        )
        db.session.add_all([appt1, appt2, appt3])

        print("Creating sample notifications for audit and review...")
        notif1 = Notification(
            user_id=sarah.id,
            profile_id=profile.id,
            type=NotificationType.MISSED_DOSE,
            title="ElderCare Alert: Missed Dose for Eleanor Vance",
            message="Evening dose of Metformin was unconfirmed.",
            recipient_email=sarah.email,
            status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc) - timedelta(days=5),
            delivery_attempts=1
        )
        notif2 = Notification(
            user_id=eleanor.id,
            profile_id=profile.id,
            type=NotificationType.MED_REMINDER,
            title="Medication Reminder: Lisinopril at 08:00",
            message="Morning dose reminder sent.",
            recipient_email=eleanor.email,
            status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc) - timedelta(hours=2),
            delivery_attempts=1
        )
        notif3 = Notification(
            user_id=david.id,
            profile_id=profile.id,
            type=NotificationType.LOW_INVENTORY,
            title="Refill Reminder: Atorvastatin is running low",
            message="8 doses remaining. Refill threshold is 10.",
            recipient_email=david.email,
            status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc) - timedelta(days=1),
            delivery_attempts=1
        )
        db.session.add_all([notif1, notif2, notif3])

        db.session.commit()
        print("\n=== Database successfully seeded with realistic healthcare data! ===")
        print("Demo Accounts:")
        print("1. Elderly User:    eleanor.vance@example.com / Password123!")
        print("2. Family Member:   sarah.vance@example.com   / Password123!")
        print("3. Caretaker User:  david.chen@example.com    / Password123!")
        print("Active Passcodes:   FAM-4310 (Family), CARE-7892 (Caretaker)")

if __name__ == "__main__":
    seed_database()

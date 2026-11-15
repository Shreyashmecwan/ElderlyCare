import json
from datetime import date, timedelta

def test_appointment_lifecycle(client, elderly_auth_headers, elderly_user):
    future_date = (date.today() + timedelta(days=5)).isoformat()

    # 1. Create appointment
    create_res = client.post("/api/appointments", headers=elderly_auth_headers, json={
        "profile_id": elderly_user["profile_id"],
        "doctor_name": "Dr. Angela Watson",
        "specialty": "Neurology",
        "hospital_clinic": "Central Memorial Hospital",
        "location": "Room 204",
        "appointment_date": future_date,
        "appointment_time": "14:30",
        "notes": "Follow-up memory test"
    })
    assert create_res.status_code == 201
    appt = create_res.get_json()["data"]
    assert appt["doctor_name"] == "Dr. Angela Watson"
    assert appt["status"] == "SCHEDULED"

    appt_id = appt["id"]

    # 2. List upcoming appointments
    list_res = client.get(f"/api/appointments?profile_id={elderly_user['profile_id']}&filter=upcoming", headers=elderly_auth_headers)
    assert list_res.status_code == 200
    appts = list_res.get_json()["data"]
    assert len(appts) >= 1

    # 3. Cancel appointment
    cancel_res = client.patch(f"/api/appointments/{appt_id}/cancel", headers=elderly_auth_headers)
    assert cancel_res.status_code == 200
    assert cancel_res.get_json()["data"]["status"] == "CANCELLED"

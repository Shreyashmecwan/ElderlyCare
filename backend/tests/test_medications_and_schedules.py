import json

def test_add_and_list_medication(client, elderly_auth_headers, elderly_user):
    payload = {
        "profile_id": elderly_user["profile_id"],
        "name": "Metformin",
        "dosage": "500",
        "unit": "mg",
        "instructions": "Take with breakfast",
        "current_inventory": 30,
        "refill_alert_threshold": 5,
        "start_date": "2026-11-01",
        "schedules": [
            {"time_of_day": "08:00", "label": "Breakfast", "days_of_week": "DAILY"},
            {"time_of_day": "20:00", "label": "Dinner", "days_of_week": "DAILY"}
        ]
    }
    create_res = client.post("/api/medications", headers=elderly_auth_headers, json=payload)
    assert create_res.status_code == 201
    med_data = create_res.get_json()["data"]
    assert med_data["name"] == "Metformin"
    assert len(med_data["schedules"]) == 2

    # List medications
    list_res = client.get(f"/api/medications?profile_id={elderly_user['profile_id']}", headers=elderly_auth_headers)
    assert list_res.status_code == 200
    meds = list_res.get_json()["data"]
    assert len(meds) == 1

def test_discontinue_medication(client, elderly_auth_headers, elderly_user):
    # Add med
    payload = {
        "profile_id": elderly_user["profile_id"],
        "name": "Aspirin",
        "dosage": "81",
        "unit": "mg",
        "start_date": "2026-11-01"
    }
    create_res = client.post("/api/medications", headers=elderly_auth_headers, json=payload)
    med_id = create_res.get_json()["data"]["id"]

    # Delete (soft-discontinue)
    del_res = client.delete(f"/api/medications/{med_id}", headers=elderly_auth_headers)
    assert del_res.status_code == 200

    # Active list should now be empty
    list_res = client.get(f"/api/medications?profile_id={elderly_user['profile_id']}&status=active", headers=elderly_auth_headers)
    assert len(list_res.get_json()["data"]) == 0

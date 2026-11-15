import json

def test_elderly_dashboard(client, elderly_auth_headers, elderly_user):
    res = client.get(f"/api/dashboard/elderly?profile_id={elderly_user['profile_id']}", headers=elderly_auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "summary" in data
    assert "today_doses" in data
    assert "emergency_contact" in data
    assert data["emergency_contact"]["name"] == "Bob Betty"

def test_family_dashboard(client, family_auth_headers):
    res = client.get("/api/dashboard/family", headers=family_auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "monitored_profiles" in data
    assert "missed_alerts" in data

def test_caretaker_dashboard(client, caretaker_auth_headers):
    res = client.get("/api/dashboard/caretaker", headers=caretaker_auth_headers)
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "assigned_patients" in data
    assert "master_daily_doses" in data

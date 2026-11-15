import os
import sys
import json

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app

def probe_system():
    print("=== Testing ElderCare Live API Endpoints ===")
    app = create_app("development")
    client = app.test_client()

    # 1. Check Swagger OpenAPI endpoint
    res_docs = client.get("/api/openapi.json")
    assert res_docs.status_code == 200
    print("✓ OpenAPI / Swagger 3.0 specification available at /api/docs & /api/openapi.json")

    # 2. Login as Eleanor Vance (Elderly)
    res_login = client.post("/api/auth/login", json={
        "email": "eleanor.vance@example.com",
        "password": "Password123!"
    })
    assert res_login.status_code == 200
    eleanor_data = res_login.get_json()["data"]
    token = eleanor_data["access_token"]
    profile_id = eleanor_data["user"]["profile_id"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✓ Senior Authentication successful: Eleanor Vance (Profile ID: {profile_id})")

    # 3. Retrieve Senior Dashboard
    res_dash = client.get(f"/api/dashboard/elderly?profile_id={profile_id}", headers=headers)
    assert res_dash.status_code == 200
    dash_data = res_dash.get_json()["data"]
    print(f"✓ Elderly Dashboard retrieved: {len(dash_data['today_doses'])} doses scheduled today, 7-day adherence: {dash_data['summary']['adherence_rate_7d']}%")

    # 4. Login as Sarah Vance (Family)
    res_fam_login = client.post("/api/auth/login", json={
        "email": "sarah.vance@example.com",
        "password": "Password123!"
    })
    assert res_fam_login.status_code == 200
    fam_token = res_fam_login.get_json()["data"]["access_token"]
    fam_headers = {"Authorization": f"Bearer {fam_token}"}
    print("✓ Family Authentication successful: Sarah Vance")

    # 5. Retrieve Family Dashboard
    res_fam_dash = client.get("/api/dashboard/family", headers=fam_headers)
    assert res_fam_dash.status_code == 200
    fam_dash = res_fam_dash.get_json()["data"]
    print(f"✓ Family Dashboard retrieved: {len(fam_dash['monitored_profiles'])} monitored loved ones, {len(fam_dash['missed_alerts'])} missed alerts tracked")

    # 6. Login as Nurse David Chen (Caretaker)
    res_care_login = client.post("/api/auth/login", json={
        "email": "david.chen@example.com",
        "password": "Password123!"
    })
    assert res_care_login.status_code == 200
    care_token = res_care_login.get_json()["data"]["access_token"]
    care_headers = {"Authorization": f"Bearer {care_token}"}
    print("✓ Caretaker Authentication successful: Nurse David Chen")

    # 7. Retrieve Caretaker Clinical Station
    res_care_dash = client.get("/api/dashboard/caretaker", headers=care_headers)
    assert res_care_dash.status_code == 200
    care_dash = res_care_dash.get_json()["data"]
    print(f"✓ Caretaker Station retrieved: {len(care_dash['assigned_patients'])} assigned patients, {len(care_dash['master_daily_doses'])} master timeline doses")

    # 8. Check Notifications & Email Provider Transparency
    res_notifs = client.get("/api/notifications", headers=headers)
    assert res_notifs.status_code == 200
    notif_data = res_notifs.get_json()["data"]
    print(f"✓ Notification System verified: Provider: {notif_data['email_service_status']['provider']}, Total Audit Records: {len(notif_data['notifications'])}")

    print("\n=== ALL SYSTEMS OPERATIONAL & VERIFIED! ===")

if __name__ == "__main__":
    probe_system()

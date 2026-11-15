import json

def test_daily_adherence_generation_and_status_update(client, elderly_auth_headers, elderly_user):
    # 1. Create a medication with 2 daily schedules
    client.post("/api/medications", headers=elderly_auth_headers, json={
        "profile_id": elderly_user["profile_id"],
        "name": "Glipizide",
        "dosage": "5",
        "unit": "mg",
        "current_inventory": 20,
        "refill_alert_threshold": 5,
        "start_date": "2026-11-01",
        "schedules": [
            {"time_of_day": "08:00", "label": "Morning", "days_of_week": "DAILY"},
            {"time_of_day": "18:00", "label": "Evening", "days_of_week": "DAILY"}
        ]
    })

    # 2. Fetch daily adherence for today
    res = client.get(f"/api/adherence/daily?profile_id={elderly_user['profile_id']}", headers=elderly_auth_headers)
    assert res.status_code == 200
    logs = res.get_json()["data"]
    assert len(logs) == 2
    assert logs[0]["status"] == "UPCOMING"

    # 3. Prevent duplicate logs: calling again must return exact same 2 records
    res_repeat = client.get(f"/api/adherence/daily?profile_id={elderly_user['profile_id']}", headers=elderly_auth_headers)
    assert len(res_repeat.get_json()["data"]) == 2

    # 4. Mark first dose as TAKEN
    first_log_id = logs[0]["id"]
    mark_res = client.post(
        f"/api/adherence/{first_log_id}/status",
        headers=elderly_auth_headers,
        json={"status": "TAKEN", "notes": "Taken with water"}
    )
    assert mark_res.status_code == 200
    updated_log = mark_res.get_json()["data"]
    assert updated_log["status"] == "TAKEN"
    assert updated_log["taken_at"] is not None

    # 5. Check adherence statistics
    stats_res = client.get(f"/api/adherence/stats?profile_id={elderly_user['profile_id']}&days=7", headers=elderly_auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.get_json()["data"]
    assert stats["taken"] >= 1
    assert "adherence_rate" in stats

import json

def test_unauthorized_user_blocked_from_profile(client, family_auth_headers, elderly_user):
    # Family user has not joined Grandma Betty's profile yet
    res = client.get(f"/api/profiles/{elderly_user['profile_id']}", headers=family_auth_headers)
    assert res.status_code == 403
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN"

def test_generate_passcode_and_redeem(client, elderly_auth_headers, family_auth_headers, elderly_user):
    # 1. Elderly generates invitation passcode for Family
    invite_res = client.post(
        f"/api/profiles/{elderly_user['profile_id']}/invitations",
        headers=elderly_auth_headers,
        json={
            "role": "FAMILY",
            "permission": "FULL_ACCESS",
            "relationship_title": "Son"
        }
    )
    assert invite_res.status_code == 201
    invite_data = invite_res.get_json()["data"]
    passcode = invite_data["passcode"]
    assert passcode.startswith("FAM-")

    # 2. Family user redeems passcode
    join_res = client.post(
        "/api/profiles/join",
        headers=family_auth_headers,
        json={"passcode": passcode}
    )
    assert join_res.status_code == 200
    assert join_res.get_json()["success"] is True

    # 3. Now Family user has authorized access to the profile!
    access_res = client.get(f"/api/profiles/{elderly_user['profile_id']}", headers=family_auth_headers)
    assert access_res.status_code == 200
    assert access_res.get_json()["data"]["id"] == elderly_user["profile_id"]

def test_redeem_invalid_passcode(client, family_auth_headers):
    res = client.post("/api/profiles/join", headers=family_auth_headers, json={"passcode": "INVALID-1234"})
    assert res.status_code == 404
    assert res.get_json()["error"]["code"] == "INVALID_PASSCODE"

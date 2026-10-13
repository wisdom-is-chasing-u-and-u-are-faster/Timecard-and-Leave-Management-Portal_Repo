

def test_sso_login_and_token_generation(client):
    """
    [ARCH-2663-AC1] Users can successfully log in via the SSO page.
    """
    # Employee login
    resp = client.post("/api/v1/auth/login", json={"email": "erin.employee@enterprise.com", "role": "EMPLOYEE"})
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["user"]["role"] == "EMPLOYEE"
    assert data["user"]["email"] == "erin.employee@enterprise.com"

    # Supervisor login
    resp_sup = client.post("/api/v1/auth/login", json={"email": "sarah.manager@enterprise.com", "role": "SUPERVISOR"})
    assert resp_sup.status_code == 200
    sup_data = resp_sup.json()
    assert sup_data["user"]["role"] == "SUPERVISOR"


def test_auth_me_profile_resolution(client):
    """
    [ARCH-2663-AC1] Retrieve authenticated session profile with role claims.
    """
    login_resp = client.post("/api/v1/auth/login", json={"role": "EMPLOYEE"})
    token = login_resp.json()["token"]

    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    me = resp.json()
    assert me["role"] == "EMPLOYEE"
    assert "name" in me

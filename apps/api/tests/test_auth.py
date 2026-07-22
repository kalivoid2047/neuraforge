API = "/api/v1"

CREDS = {"email": "dev.chen@example.com", "password": "a-long-passphrase-42"}


async def _register_and_verify(client) -> None:
    r = await client.post(f"{API}/auth/register", json={
        **CREDS, "display_name": "Chen", "tz": "Asia/Shanghai",
    })
    assert r.status_code == 201
    token = r.json()["dev_verification_token"]
    assert token
    r = await client.get(f"{API}/auth/verify-email", params={"token": token})
    assert r.status_code == 200


async def _login(client) -> str:
    r = await client.post(f"{API}/auth/login", json=CREDS)
    assert r.status_code == 200
    return r.json()["access_token"]


def _csrf_headers(client) -> dict:
    return {"X-CSRF-Token": client.cookies.get("nf_csrf")}


async def test_register_verify_login_me(client):
    await _register_and_verify(client)
    access = await _login(client)

    r = await client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == CREDS["email"]
    assert body["email_verified"] is True
    # refresh cookie set, path-scoped
    assert client.cookies.get("nf_refresh")


async def test_login_before_verification_blocked(client):
    r = await client.post(f"{API}/auth/register", json={
        "email": "unverified@example.com", "password": "passphrase-of-length",
        "display_name": "Nova",
    })
    assert r.status_code == 201
    r = await client.post(f"{API}/auth/login", json={
        "email": "unverified@example.com", "password": "passphrase-of-length",
    })
    assert r.status_code == 401
    assert "not verified" in r.json()["detail"]


async def test_wrong_password_uniform_error(client):
    await _register_and_verify(client)
    r = await client.post(f"{API}/auth/login", json={**CREDS, "password": "wrong-wrong-wrong"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid email or password."


async def test_duplicate_registration_conflict(client):
    await _register_and_verify(client)
    r = await client.post(f"{API}/auth/register", json={
        **CREDS, "display_name": "Imposter",
    })
    assert r.status_code == 409


async def test_refresh_rotates_and_reuse_revokes_family(client):
    await _register_and_verify(client)
    await _login(client)
    old_refresh = client.cookies.get("nf_refresh")

    # rotate
    r = await client.post(f"{API}/auth/refresh", headers=_csrf_headers(client))
    assert r.status_code == 200
    new_refresh = client.cookies.get("nf_refresh")
    assert new_refresh != old_refresh

    # replay the OLD (rotated) token → reuse detection → family revoked
    client.cookies.set("nf_refresh", old_refresh, path="/api/v1/auth")
    r = await client.post(f"{API}/auth/refresh", headers=_csrf_headers(client))
    assert r.status_code == 401
    assert "invalidated" in r.json()["detail"]

    # even the NEW token is now dead (whole family revoked)
    client.cookies.set("nf_refresh", new_refresh, path="/api/v1/auth")
    r = await client.post(f"{API}/auth/refresh", headers=_csrf_headers(client))
    assert r.status_code == 401


async def test_refresh_requires_csrf(client):
    await _register_and_verify(client)
    await _login(client)
    r = await client.post(f"{API}/auth/refresh")  # no X-CSRF-Token header
    assert r.status_code == 401
    assert "CSRF" in r.json()["detail"]


async def test_logout_revokes_and_clears(client):
    await _register_and_verify(client)
    access = await _login(client)
    refresh_before = client.cookies.get("nf_refresh")

    r = await client.post(f"{API}/auth/logout", headers=_csrf_headers(client))
    assert r.status_code == 204

    # revoked refresh can no longer rotate
    client.cookies.set("nf_refresh", refresh_before, path="/api/v1/auth")
    client.cookies.set("nf_csrf", "x", path="/api/v1/auth")
    r = await client.post(f"{API}/auth/refresh", headers={"X-CSRF-Token": "x"})
    assert r.status_code == 401

    # access token still valid until expiry (15-min lag is the documented trade-off)
    r = await client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200


async def test_sessions_list_and_revoke(client):
    await _register_and_verify(client)
    access = await _login(client)
    auth = {"Authorization": f"Bearer {access}"}

    r = await client.get(f"{API}/auth/sessions", headers=auth)
    assert r.status_code == 200
    sessions = r.json()
    assert len(sessions) == 1 and sessions[0]["current"] is True

    r = await client.delete(f"{API}/auth/sessions/{sessions[0]['family_id']}", headers=auth)
    assert r.status_code == 204
    r = await client.get(f"{API}/auth/sessions", headers=auth)
    assert r.json() == []


async def test_garbage_bearer_rejected(client):
    r = await client.get(f"{API}/auth/me", headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401

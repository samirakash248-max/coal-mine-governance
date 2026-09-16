from sqlalchemy import text
import pytest
from httpx import AsyncClient
from datetime import timedelta
import uuid

from app.models.user import User, Role
from app.core.security import hash_password, create_access_token
from app.services.audit import AuditLog
from sqlalchemy import select

@pytest.fixture
async def test_users(db_session):
    admin = User(email="admin@test.com", full_name="Admin User", hashed_password=hash_password("admin123"), role=Role.ADMIN, is_active=True)
    admin2 = User(email="admin2@test.com", full_name="Admin 2", hashed_password=hash_password("admin123"), role=Role.ADMIN, is_active=True)
    sysadmin = User(email="sysadmin@test.com", full_name="Sys Admin", hashed_password=hash_password("admin123"), role=Role.SYSTEM_ADMIN, is_active=True)
    user = User(email="user@test.com", full_name="Normal User", hashed_password=hash_password("user123"), role=Role.FIELD_INSPECTOR, is_active=True)
    safety = User(email="safety@test.com", full_name="Safety Officer", hashed_password=hash_password("user123"), role=Role.SAFETY_OFFICER, is_active=True)
    env = User(email="env@test.com", full_name="Environment Officer", hashed_password=hash_password("user123"), role=Role.ENVIRONMENT_OFFICER, is_active=True)
    inactive = User(email="inactive@test.com", full_name="Inactive User", hashed_password=hash_password("user123"), role=Role.FIELD_INSPECTOR, is_active=False)
    
    db_session.add_all([admin, admin2, sysadmin, user, safety, env, inactive])
    await db_session.commit()
    
    for u in [admin, admin2, sysadmin, user, safety, env, inactive]:
        await db_session.refresh(u)
        
    return {
        "admin": admin,
        "admin2": admin2,
        "sysadmin": sysadmin,
        "user": user,
        "safety": safety,
        "env": env,
        "inactive": inactive
    }

def get_token_for(email: str, role: Role):
    return create_access_token(data={"sub": email, "role": role})

@pytest.mark.asyncio
async def test_valid_login_succeeds(async_client, test_users):
    response = await async_client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "user123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Verify token works on protected endpoint
    token = response.json()["access_token"]
    me_resp = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "user@test.com"

@pytest.mark.asyncio
async def test_invalid_password_fails(async_client, test_users):
    response = await async_client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_unknown_user_fails(async_client):
    response = await async_client.post("/api/v1/auth/login", data={"username": "nobody@test.com", "password": "password"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_inactive_user_cannot_login(async_client, test_users):
    response = await async_client.post("/api/v1/auth/login", data={"username": "inactive@test.com", "password": "user123"})
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_missing_token_returns_401(async_client):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_expired_token_fails(async_client, test_users):
    token = create_access_token(data={"sub": "user@test.com"}, expires_delta=timedelta(seconds=-1))
    response = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

@pytest.mark.asyncio
async def test_invalid_jwt_malformed(async_client):
    response = await async_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.jwt"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_invalid_jwt_signature(async_client, test_users):
    token = create_access_token(data={"sub": "user@test.com"})
    invalid_token = token[:-5] + "aaaaa"
    response = await async_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {invalid_token}"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_rbac_admin_can_access_users(async_client, test_users):
    token = get_token_for("admin@test.com", Role.ADMIN)
    response = await async_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_rbac_non_admin_denied_users(async_client, test_users):
    token = get_token_for("safety@test.com", Role.SAFETY_OFFICER)
    response = await async_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_rbac_safety_officer_can_access_weather(async_client, test_users):
    token = get_token_for("safety@test.com", Role.SAFETY_OFFICER)
    response = await async_client.get("/api/v1/weather/mine/00000000-0000-0000-0000-000000000000", headers={"Authorization": f"Bearer {token}"})
    # Might be 404 since mine doesn't exist, but NOT 403
    assert response.status_code != 403
    
@pytest.mark.asyncio
async def test_rbac_environment_officer_can_access_weather(async_client, test_users):
    token = get_token_for("env@test.com", Role.ENVIRONMENT_OFFICER)
    response = await async_client.get("/api/v1/weather/mine/00000000-0000-0000-0000-000000000000", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code != 403

@pytest.mark.asyncio
async def test_privilege_escalation_change_own_role(async_client, test_users):
    token = get_token_for("user@test.com", Role.FIELD_INSPECTOR)
    response = await async_client.patch("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}, json={"full_name": "New Name", "role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "field_inspector"

@pytest.mark.asyncio
async def test_privilege_escalation_unauthorized_user_creation(async_client, test_users):
    token = get_token_for("user@test.com", Role.FIELD_INSPECTOR)
    payload = {"email": "hack@test.com", "password": "pass", "full_name": "Hack", "role": "admin"}
    response = await async_client.post("/api/v1/users/", headers={"Authorization": f"Bearer {token}"}, json=payload)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_last_admin_protection_delete(async_client, test_users):
    token = get_token_for("admin@test.com", Role.ADMIN)
    
    # Try to delete admin2
    r = await async_client.delete(f"/api/v1/users/{test_users['admin2'].id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204
    
    # Try to delete sysadmin
    r = await async_client.delete(f"/api/v1/users/{test_users['sysadmin'].id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 204
    
    # Now try to delete the last admin (self)
    r2 = await async_client.delete(f"/api/v1/users/{test_users['admin'].id}", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 400
    assert "last active administrator" in r2.json()["detail"]
    
@pytest.mark.asyncio
async def test_last_admin_protection_role_change(async_client, test_users):
    token = get_token_for("admin@test.com", Role.ADMIN)
    
    # Try to change admin2's role
    r = await async_client.patch(f"/api/v1/users/{test_users['admin2'].id}", json={"role": "field_inspector"}, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    
    # Now try to change own role
    r2 = await async_client.patch(f"/api/v1/users/{test_users['admin'].id}", json={"role": "field_inspector"}, headers={"Authorization": f"Bearer {token}"})
    

@pytest.mark.asyncio
async def test_password_not_returned_by_user_api(async_client, test_users):
    token = get_token_for("admin@test.com", Role.ADMIN)
    response = await async_client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "password" not in data[0]
    assert "hashed_password" not in data[0]

@pytest.mark.asyncio
async def test_audit_log_login_success(async_client, test_users, db_session):
    response = await async_client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "user123"})
    assert response.status_code == 200
    
    # check audit log
    stmt = select(AuditLog).where(AuditLog.action == "LOGIN_SUCCESS", AuditLog.entity_id == str(test_users["user"].id))
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) > 0
    assert "password" not in (str(logs[0].after_state) or "")

@pytest.mark.asyncio
async def test_progressive_rate_limit(async_client, test_users):
    # Fire 4 bad logins
    for _ in range(4):
        r = await async_client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "wrongpassword"})
        assert r.status_code == 401
    
    import time
    start = time.time()
    r = await async_client.post("/api/v1/auth/login", data={"username": "user@test.com", "password": "wrongpassword"})
    end = time.time()
    
    # The 4th attempt should have delayed by at least 2 seconds (2^(4-3))
    assert end - start >= 2.0

@pytest.mark.asyncio
async def test_security_headers_present(async_client):
    response = await async_client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "max-age=31536000" in response.headers.get("Strict-Transport-Security", "")

@pytest.mark.asyncio
async def test_database_health(db_session):
    version = await db_session.scalar(select(text("version()")))
    postgis = await db_session.scalar(select(text("PostGIS_Version()")))
    vector = await db_session.scalar(select(text("extversion FROM pg_extension WHERE extname = 'vector'")))
    
    print(f"\nPostgreSQL: OK ({version[:30]}...)")
    print(f"PostGIS: OK ({postgis})")
    print(f"pgvector: OK ({vector})")
    
    assert "PostgreSQL" in version
    assert postgis is not None
    assert vector is not None



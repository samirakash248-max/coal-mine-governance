import pytest
from httpx import AsyncClient
from app.models.user import Role
import uuid

@pytest.mark.asyncio
async def test_tenant_read_isolation(async_client: AsyncClient, get_auth_token, db_session):
    # Log in as a mine manager for Mine A
    token = await get_auth_token("manager.raniganj@coalmine.gov.in", "demo123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Let's get their mine_id from /api/v1/auth/me (or assuming they have one)
    res = await async_client.get("/api/v1/users/me", headers=headers)
    assert res.status_code == 200
    me = res.json()
    my_mine_id = me.get("mine_id")
    assert my_mine_id is not None
    
    # 1. Test reading safety events. Should ONLY return events from my_mine_id
    res = await async_client.get("/api/v1/field/events", headers=headers)
    assert res.status_code == 200
    events = res.json()
    for ev in events:
        assert ev["mine_id"] == my_mine_id, f"Leaked event from another mine: {ev['mine_id']}"

@pytest.mark.asyncio
async def test_tenant_write_isolation(async_client: AsyncClient, get_auth_token):
    # Log in as a mine manager for Mine A
    token = await get_auth_token("manager.raniganj@coalmine.gov.in", "demo123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to create an inspection for a completely random (unauthorized) mine
    fake_mine_id = str(uuid.uuid4())
    payload = {
        "mine_id": fake_mine_id,
        "type": "ROUTINE",
        "status": "DRAFT",
        "notes": "Hacked inspection"
    }
    
    res = await async_client.post("/api/v1/inspections/", json=payload, headers=headers)
    # Our force_tenant_creation should override it to the current_user's mine_id, or throw 403.
    assert res.status_code in [200, 201, 403]
    if res.status_code in [200, 201]:
        # It was forced to the authorized mine
        assert res.json()["mine_id"] != fake_mine_id

@pytest.mark.asyncio
async def test_corporate_manager_multi_mine(async_client: AsyncClient, get_auth_token):
    token = await get_auth_token("corporate@coalmine.gov.in", "demo123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Corporate should be able to see multiple mines
    res = await async_client.get("/api/v1/hierarchy/mines", headers=headers)
    assert res.status_code == 200
    mines = res.json()
    assert len(mines) >= 3

@pytest.mark.asyncio
async def test_team_access_manager_isolation(async_client: AsyncClient, get_auth_token, db_session):
    token = await get_auth_token("manager.raniganj@coalmine.gov.in", "demo123")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all users returned to this mine manager
    res = await async_client.get("/api/v1/users/", headers=headers)
    assert res.status_code == 200
    users = res.json()
    
    # Get current user's mine_id
    me_res = await async_client.get("/api/v1/users/me", headers=headers)
    my_mine_id = me_res.json().get("mine_id")
    
    for u in users:
        # Some users might have no mine_id (corporate), but ideally a mine manager shouldn't see them either,
        # unless they are associated with the mine. Our apply_tenant_scope forces mine_id == my_mine_id.
        assert u["mine_id"] == my_mine_id or u["mine_id"] is None
        
    # Try to modify another user's role outside this mine.
    # We will pick a user that is not in my_mine_id.
    # Let's try to patch admin.
    # The admin might not be returned, so we'll just query the DB for the admin ID to hack it.
    from sqlalchemy import select
    from app.models.user import User
    admin = (await db_session.execute(select(User).where(User.email == "admin@coalmine.gov.in"))).scalar_one()
    
    res = await async_client.patch(f"/api/v1/users/{admin.id}", json={"role": "MINE_MANAGER"}, headers=headers)
    assert res.status_code == 403

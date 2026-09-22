import re

filepath = "backend/app/api/v1/field.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user, require_permission", "from app.api.deps import get_current_user, require_permission, apply_tenant_scope, force_tenant_creation")

# get_event_stats
target_stats = """    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)"""
replacement_stats = """    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)"""
content = content.replace(target_stats, replacement_stats)

# create_safety_event
target_create = """    if current_user.mine_id and event_data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create event for another mine")"""
replacement_create = """    event_data = force_tenant_creation(event_data, current_user)"""
content = content.replace(target_create, replacement_create)

# get_events
target_get = """    # Scope check
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)"""
replacement_get = """    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)"""
content = content.replace(target_get, replacement_get)

# get_event
target_get1 = """    stmt = select(SafetyEvent).where(SafetyEvent.id == id)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.mine_id and event.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Access denied")"""
replacement_get1 = """    stmt = select(SafetyEvent).where(SafetyEvent.id == id)
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")"""
content = content.replace(target_get1, replacement_get1)

# get_actions
target_act = """    if current_user.mine_id:
        stmt = stmt.where(CorrectiveAction.mine_id == current_user.mine_id)"""
replacement_act = """    stmt = apply_tenant_scope(stmt, CorrectiveAction, current_user)"""
content = content.replace(target_act, replacement_act)

# get_spatial_events
target_spat = """    if current_user.mine_id:
        if current_user.mine_id != mine_id:
            return []
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)"""
replacement_spat = """    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)"""
content = content.replace(target_spat, replacement_spat)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

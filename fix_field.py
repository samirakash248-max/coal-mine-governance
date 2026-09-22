import re

filepath = "backend/app/api/v1/field.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user, get_pagination, PaginationParams", "from app.api.deps import get_current_user, get_pagination, PaginationParams, apply_tenant_scope, force_tenant_creation")

target = """    stmt = select(
        SafetyEvent
    ).order_by(SafetyEvent.date.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()"""
replacement = """    stmt = select(SafetyEvent).order_by(SafetyEvent.date.desc()).offset(skip).limit(limit)
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)
    return (await db.execute(stmt)).scalars().all()"""
content = content.replace(target, replacement)

# get event
target2 = """    event = (await db.execute(select(SafetyEvent).where(SafetyEvent.id == event_id))).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Safety event not found")"""
replacement2 = """    stmt = select(SafetyEvent).where(SafetyEvent.id == event_id)
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Safety event not found")"""
content = content.replace(target2, replacement2)

# POST event
target3 = """    event_data = event_in.model_dump(exclude={"idempotency_key"})"""
replacement3 = """    event_data = event_in.model_dump(exclude={"idempotency_key"})
    event_data = force_tenant_creation(event_data, current_user)"""
content = content.replace(target3, replacement3)

# PUT event
target4 = """    stmt = select(SafetyEvent).where(SafetyEvent.id == id)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Safety event not found")"""
replacement4 = """    stmt = select(SafetyEvent).where(SafetyEvent.id == id)
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)
    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Safety event not found")"""
content = content.replace(target4, replacement4)

# GET actions
target5 = """    stmt = select(CorrectiveAction).order_by(CorrectiveAction.due_date.asc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()"""
replacement5 = """    stmt = select(CorrectiveAction).order_by(CorrectiveAction.due_date.asc()).offset(skip).limit(limit)
    stmt = apply_tenant_scope(stmt, CorrectiveAction, current_user)
    return (await db.execute(stmt)).scalars().all()"""
content = content.replace(target5, replacement5)

# GET map
target6 = """    stmt = select(SafetyEvent).where(SafetyEvent.location_geom.is_not(None))
    
    events = (await db.execute(stmt)).scalars().all()"""
replacement6 = """    stmt = select(SafetyEvent).where(SafetyEvent.location_geom.is_not(None))
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)
    events = (await db.execute(stmt)).scalars().all()"""
content = content.replace(target6, replacement6)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

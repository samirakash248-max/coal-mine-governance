import re

filepath = "backend/app/api/v1/inspections.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add isolation check to create_inspection
old_create = """    data = inspection_in.model_dump()
    inspection = Inspection(**data, inspector_id=current_user.id)"""
new_create = """    data = inspection_in.model_dump()
    if current_user.mine_id and data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create an inspection for another mine")
    inspection = Inspection(**data, inspector_id=current_user.id)"""
content = content.replace(old_create, new_create)

# Add isolation check to get_inspection
old_get = """    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')
    return inspection"""
new_get = """    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')
    if current_user.mine_id and inspection.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return inspection"""
content = content.replace(old_get, new_get)

# Add isolation check to get_findings and get_actions (need to check inspection's mine_id first)
old_get_findings = """async def get_findings(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.INSPECTION_READ))):
    stmt = select(SafetyEvent).where(SafetyEvent.inspection_id == id)
    return (await db.execute(stmt)).scalars().all()"""
new_get_findings = """async def get_findings(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.INSPECTION_READ))):
    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection or (current_user.mine_id and inspection.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail='Inspection not found')
    stmt = select(SafetyEvent).where(SafetyEvent.inspection_id == id)
    return (await db.execute(stmt)).scalars().all()"""
content = content.replace(old_get_findings, new_get_findings)

old_get_actions = """async def get_actions(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.INSPECTION_READ))):
    stmt = select(CorrectiveAction).where(CorrectiveAction.source_inspection_id == id)
    return (await db.execute(stmt)).scalars().all()"""
new_get_actions = """async def get_actions(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(require_permission(Permission.INSPECTION_READ))):
    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection or (current_user.mine_id and inspection.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail='Inspection not found')
    stmt = select(CorrectiveAction).where(CorrectiveAction.source_inspection_id == id)
    return (await db.execute(stmt)).scalars().all()"""
content = content.replace(old_get_actions, new_get_actions)


with open(filepath, 'w') as f:
    f.write(content)

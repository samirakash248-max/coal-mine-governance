import re

filepath = "backend/app/api/v1/inspections.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope, force_tenant_creation")

# GET inspections
target = """    stmt = select(Inspection).order_by(Inspection.date.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()"""
replacement = """    stmt = select(Inspection).order_by(Inspection.date.desc()).offset(skip).limit(limit)
    stmt = apply_tenant_scope(stmt, Inspection, current_user)
    return (await db.execute(stmt)).scalars().all()"""
content = content.replace(target, replacement)

# POST inspection (it already had an IDOR check, but let's force it)
target2 = """    data = inspection_in.model_dump()
    if current_user.mine_id and data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create an inspection for another mine")"""
replacement2 = """    data = inspection_in.model_dump()
    data = force_tenant_creation(data, current_user)"""
content = content.replace(target2, replacement2)

# GET inspection by ID
target3 = """    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")"""
replacement3 = """    stmt = select(Inspection).where(Inspection.id == id)
    stmt = apply_tenant_scope(stmt, Inspection, current_user)
    inspection = (await db.execute(stmt)).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")"""
content = content.replace(target3, replacement3)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

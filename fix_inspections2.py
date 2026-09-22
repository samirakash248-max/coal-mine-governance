import re

filepath = "backend/app/api/v1/inspections.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# get_stats
target_stats = """    if current_user.mine_id:
        stmt = stmt.where(Inspection.mine_id == current_user.mine_id)"""
replacement_stats = """    stmt = apply_tenant_scope(stmt, Inspection, current_user)"""
content = content.replace(target_stats, replacement_stats)

# list_inspections
target_list = """    stmt = select(Inspection).order_by(Inspection.date.desc()).offset(skip).limit(limit)
    if current_user.mine_id:
        stmt = stmt.where(Inspection.mine_id == current_user.mine_id)"""
replacement_list = """    stmt = select(Inspection).order_by(Inspection.date.desc()).offset(skip).limit(limit)
    stmt = apply_tenant_scope(stmt, Inspection, current_user)"""
content = content.replace(target_list, replacement_list)

# get_inspection
target_get = """    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')
    if current_user.mine_id and inspection.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Access denied")"""
replacement_get = """    stmt = select(Inspection).where(Inspection.id == id)
    stmt = apply_tenant_scope(stmt, Inspection, current_user)
    inspection = (await db.execute(stmt)).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')"""
content = content.replace(target_get, replacement_get)

# get_findings
target_find = """    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection or (current_user.mine_id and inspection.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail='Inspection not found')"""
replacement_find = """    stmt_insp = select(Inspection).where(Inspection.id == id)
    stmt_insp = apply_tenant_scope(stmt_insp, Inspection, current_user)
    inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')"""
content = content.replace(target_find, replacement_find)

# get_actions
target_act = """    inspection = (await db.execute(select(Inspection).where(Inspection.id == id))).scalar_one_or_none()
    if not inspection or (current_user.mine_id and inspection.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail='Inspection not found')"""
replacement_act = """    stmt_insp = select(Inspection).where(Inspection.id == id)
    stmt_insp = apply_tenant_scope(stmt_insp, Inspection, current_user)
    inspection = (await db.execute(stmt_insp)).scalar_one_or_none()
    if not inspection:
        raise HTTPException(status_code=404, detail='Inspection not found')"""
content = content.replace(target_act, replacement_act)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

import re

filepath = "backend/app/api/v1/grievances.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope, force_tenant_creation")

target_list = """    stmt = select(Grievance).where(Grievance.mine_id == current_user.mine_id).order_by(Grievance.created_at.desc())"""
replacement_list = """    stmt = select(Grievance).order_by(Grievance.created_at.desc())
    stmt = apply_tenant_scope(stmt, Grievance, current_user)"""
content = content.replace(target_list, replacement_list)

target_get = """    stmt = select(Grievance).where(Grievance.id == grievance_id, Grievance.mine_id == current_user.mine_id)"""
replacement_get = """    stmt = select(Grievance).where(Grievance.id == grievance_id)
    stmt = apply_tenant_scope(stmt, Grievance, current_user)"""
content = content.replace(target_get, replacement_get)

target_post = """    grievance = Grievance(
        mine_id=current_user.mine_id,"""
replacement_post = """    data = req.model_dump()
    data = force_tenant_creation(data, current_user)
    grievance = Grievance(
        mine_id=data.get("mine_id"),"""
content = content.replace(target_post, replacement_post)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

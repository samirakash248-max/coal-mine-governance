import re

filepath = "backend/app/api/v1/hierarchy.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope")

target1 = """    stmt = select(Mine)
    
    if current_user.mine_id:
        stmt = stmt.where(Mine.id == current_user.mine_id)
    elif current_user.region_id:
        stmt = stmt.where(Mine.region_id == current_user.region_id)
    elif current_user.subsidiary_id:
        stmt = stmt.where(Mine.region.has(subsidiary_id=current_user.subsidiary_id))"""

replacement1 = """    stmt = select(Mine)
    stmt = apply_tenant_scope(stmt, Mine, current_user)
    
    # We still keep region scoping if they have it, but apply_tenant_scope allows corporate users to see all.
    # Note: Our apply_tenant_scope allows multi_mine_roles to see all.
    if current_user.mine_id is None and current_user.region_id:
        stmt = stmt.where(Mine.region_id == current_user.region_id)
    elif current_user.mine_id is None and current_user.subsidiary_id:
        stmt = stmt.where(Mine.region.has(subsidiary_id=current_user.subsidiary_id))"""

if target1 in content:
    content = content.replace(target1, replacement1)
else:
    # Let's just blindly apply it to select(Mine)
    target1b = """    stmt = select(Mine)"""
    replacement1b = """    stmt = select(Mine)
    stmt = apply_tenant_scope(stmt, Mine, current_user)"""
    content = content.replace(target1b, replacement1b)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

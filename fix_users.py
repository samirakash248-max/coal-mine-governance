import re

filepath = "backend/app/api/v1/users.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace list_users select
content = content.replace("from app.api.deps import require_permission, require_role, get_current_user", "from app.api.deps import require_permission, require_role, get_current_user, apply_tenant_scope, validate_tenant_mutation, force_tenant_creation")

target = """    stmt = select(User).order_by(User.email).offset(pagination.skip).limit(pagination.limit)"""
replacement = """    stmt = select(User).order_by(User.email).offset(pagination.skip).limit(pagination.limit)
    stmt = apply_tenant_scope(stmt, User, current_user)"""
content = content.replace(target, replacement)

# Replace get_user
target_get = """    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")"""
replacement_get = """    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")"""
content = content.replace(target_get, replacement_get)

# Since update_user already has IDOR prevention (I added it recently), I'll leave it or replace it with validate_tenant_mutation.
# delete_user
target_delete = """    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")"""
replacement_delete = """    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")"""
content = content.replace(target_delete, replacement_delete)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

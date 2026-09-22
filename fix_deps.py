import re

filepath = "backend/app/api/deps.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_code = """
import uuid
from app.models.hierarchy import Mine

def apply_tenant_scope(stmt, entity, current_user: User):
    \"\"\"
    Central Authorization Mechanism for Tenant Isolation.
    Applies the authorized mine scope to the SQLAlchemy statement.
    \"\"\"
    multi_mine_roles = [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER, Role.REGULATORY_AUDITOR, Role.REGULATOR]
    if current_user.mine_id:
        return stmt.where(entity.mine_id == current_user.mine_id)
    if current_user.role in multi_mine_roles:
        return stmt
    return stmt.where(entity.mine_id == uuid.uuid4())

def validate_tenant_mutation(requested_mine_id, current_user: User):
    multi_mine_roles = [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER]
    if current_user.role in multi_mine_roles:
        return True
    if current_user.mine_id and str(current_user.mine_id) == str(requested_mine_id):
        return True
    from fastapi import HTTPException
    raise HTTPException(status_code=403, detail="Forbidden: Cannot mutate data for an unauthorized mine.")

def force_tenant_creation(data_dict: dict, current_user: User):
    multi_mine_roles = [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER]
    if current_user.role not in multi_mine_roles:
        if current_user.mine_id:
            data_dict["mine_id"] = current_user.mine_id
    return data_dict
"""

content += new_code
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

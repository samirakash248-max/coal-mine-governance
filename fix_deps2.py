import re

filepath = "backend/app/api/deps.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """    if current_user.mine_id:
        return stmt.where(entity.mine_id == current_user.mine_id)
    if current_user.role in multi_mine_roles:
        return stmt
    return stmt.where(entity.mine_id == uuid.uuid4())"""

replacement = """    mine_attr = getattr(entity, 'mine_id', None)
    if mine_attr is None:
        if hasattr(entity, 'id') and entity.__name__ == 'Mine':
            mine_attr = getattr(entity, 'id')
    
    if mine_attr is None:
        # For entities without mine scoping (like Regions), let it pass for multi_mine_roles
        if current_user.role in multi_mine_roles:
            return stmt
        from fastapi import HTTPException
        raise HTTPException(403, "Cannot scope this entity")

    if current_user.mine_id:
        return stmt.where(mine_attr == current_user.mine_id)
    if current_user.role in multi_mine_roles:
        return stmt
    return stmt.where(mine_attr == uuid.uuid4())"""

content = content.replace(target, replacement)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

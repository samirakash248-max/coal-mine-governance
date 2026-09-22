import re

filepath = "backend/app/api/v1/analytics.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user, get_pagination, PaginationParams", "from app.api.deps import get_current_user, get_pagination, PaginationParams, apply_tenant_scope")

target1 = """    stmt = select(SafetyEvent).where(SafetyEvent.created_at >= six_months_ago)
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)"""
replacement1 = """    stmt = select(SafetyEvent).where(SafetyEvent.created_at >= six_months_ago)
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)"""
content = content.replace(target1, replacement1)

target2 = """    stmt = select(SafetyEvent).where(SafetyEvent.risk_level.in_(["HIGH", "CRITICAL"]))
    if current_user.mine_id:
        stmt = stmt.where(SafetyEvent.mine_id == current_user.mine_id)"""
replacement2 = """    stmt = select(SafetyEvent).where(SafetyEvent.risk_level.in_(["HIGH", "CRITICAL"]))
    stmt = apply_tenant_scope(stmt, SafetyEvent, current_user)"""
content = content.replace(target2, replacement2)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

import re

filepath = "backend/app/api/v1/operations.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope")

target_contractor = """    stmt = select(Contractor).where(Contractor.mine_id == current_user.mine_id)"""
replacement_contractor = """    stmt = select(Contractor)
    stmt = apply_tenant_scope(stmt, Contractor, current_user)"""
content = content.replace(target_contractor, replacement_contractor)

target_env = """    stmt = select(EnvironmentReading).where(EnvironmentReading.mine_id == current_user.mine_id).order_by(EnvironmentReading.created_at.desc()).limit(20)"""
replacement_env = """    stmt = select(EnvironmentReading).order_by(EnvironmentReading.created_at.desc()).limit(20)
    stmt = apply_tenant_scope(stmt, EnvironmentReading, current_user)"""
content = content.replace(target_env, replacement_env)

target_prod = """    stmt = select(ProductionRecord).where(ProductionRecord.mine_id == current_user.mine_id).order_by(ProductionRecord.date.desc()).limit(30)"""
replacement_prod = """    stmt = select(ProductionRecord).order_by(ProductionRecord.date.desc()).limit(30)
    stmt = apply_tenant_scope(stmt, ProductionRecord, current_user)"""
content = content.replace(target_prod, replacement_prod)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

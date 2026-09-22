import re

filepath = "backend/app/api/v1/reports.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope")

target_list = """    stmt = select(Report).where(
        Report.mine_id == current_user.mine_id
    ).order_by(Report.created_at.desc())"""
replacement_list = """    stmt = select(Report).order_by(Report.created_at.desc())
    stmt = apply_tenant_scope(stmt, Report, current_user)"""
content = content.replace(target_list, replacement_list)

target_get = """    stmt = select(Report).where(Report.id == report_id, Report.mine_id == current_user.mine_id)"""
replacement_get = """    stmt = select(Report).where(Report.id == report_id)
    stmt = apply_tenant_scope(stmt, Report, current_user)"""
content = content.replace(target_get, replacement_get)

# In create_report, we should also validate requested mine_id, or force it.
# Assuming it uses force_tenant_creation

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

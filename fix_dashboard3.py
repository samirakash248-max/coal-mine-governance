import re

filepath = "backend/app/api/v1/dashboard.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope")

target_mine = """    mine_stmt = select(func.count(Mine.id))
    total_mines = (await db.execute(mine_stmt)).scalar()"""
replacement_mine = """    mine_stmt = select(func.count(Mine.id))
    mine_stmt = apply_tenant_scope(mine_stmt, Mine, current_user)
    total_mines = (await db.execute(mine_stmt)).scalar()"""
content = content.replace(target_mine, replacement_mine)

target_comp1 = """    record_count_base = select(func.count(ComplianceRecord.id)).select_from(ComplianceRecord).join(ComplianceRequirement)
    total_reqs = (await db.execute(record_count_base)).scalar() or 0"""
replacement_comp1 = """    record_count_base = select(func.count(ComplianceRecord.id)).select_from(ComplianceRecord).join(ComplianceRequirement)
    record_count_base = apply_tenant_scope(record_count_base, ComplianceRecord, current_user)
    total_reqs = (await db.execute(record_count_base)).scalar() or 0"""
content = content.replace(target_comp1, replacement_comp1)

target_comp2 = """    compliant_reqs = (await db.execute(record_count_base.where(ComplianceRecord.status == "COMPLIANT"))).scalar() or 0
    at_risk_reqs = (await db.execute(record_count_base.where(ComplianceRecord.status.in_(["NON_COMPLIANT", "DUE_SOON"])))).scalar() or 0"""
replacement_comp2 = """    compliant_reqs = (await db.execute(record_count_base.where(ComplianceRecord.status == "COMPLIANT"))).scalar() or 0
    at_risk_reqs = (await db.execute(record_count_base.where(ComplianceRecord.status.in_(["NON_COMPLIANT", "DUE_SOON"])))).scalar() or 0"""
# this remains same, because record_count_base is already scoped!

target_event = """    event_count_base = select(func.count(SafetyEvent.id)).select_from(SafetyEvent)
    action_count_base = select(func.count(CorrectiveAction.id)).select_from(CorrectiveAction)
    
    total_incidents = (await db.execute(event_count_base.where(SafetyEvent.type == "INCIDENT"))).scalar() or 0"""
replacement_event = """    event_count_base = select(func.count(SafetyEvent.id)).select_from(SafetyEvent)
    event_count_base = apply_tenant_scope(event_count_base, SafetyEvent, current_user)
    
    action_count_base = select(func.count(CorrectiveAction.id)).select_from(CorrectiveAction)
    action_count_base = apply_tenant_scope(action_count_base, CorrectiveAction, current_user)
    
    total_incidents = (await db.execute(event_count_base.where(SafetyEvent.type == "INCIDENT"))).scalar() or 0"""
content = content.replace(target_event, replacement_event)

target_risk1 = """    rec_stmt = select(func.count(RecurringIssue.id))
    anom_stmt = select(func.count(AnomalyEvent.id))
    
    rec_count = (await db.execute(rec_stmt)).scalar() or 0"""
replacement_risk1 = """    rec_stmt = select(func.count(RecurringIssue.id))
    rec_stmt = apply_tenant_scope(rec_stmt, RecurringIssue, current_user)
    
    anom_stmt = select(func.count(AnomalyEvent.id))
    anom_stmt = apply_tenant_scope(anom_stmt, AnomalyEvent, current_user)
    
    rec_count = (await db.execute(rec_stmt)).scalar() or 0"""
content = content.replace(target_risk1, replacement_risk1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

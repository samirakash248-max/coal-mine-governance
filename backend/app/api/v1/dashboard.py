from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models.user import User
from app.models.hierarchy import Mine
from app.models.compliance import ComplianceRecord, ComplianceRequirement, ComplianceStatus
from app.schemas.dashboard import DashboardSummary
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Total Mines Count
    mine_stmt = select(func.count(Mine.id))
    if current_user.mine_id:
        mine_stmt = mine_stmt.where(Mine.id == current_user.mine_id)
    elif current_user.region_id:
        mine_stmt = mine_stmt.where(Mine.region_id == current_user.region_id)
        
    mine_count_result = await db.execute(mine_stmt)
    total_mines = mine_count_result.scalar_one()

    # Base record query restricted by scope
    record_base_stmt = select(ComplianceRecord).join(ComplianceRequirement)
    if current_user.mine_id:
        record_base_stmt = record_base_stmt.where(ComplianceRequirement.applicable_mine_id == current_user.mine_id)

    # 2. Overdue Count
    record_count_base = select(func.count(ComplianceRecord.id)).select_from(ComplianceRecord).join(ComplianceRequirement)
    if current_user.mine_id:
        record_count_base = record_count_base.where(ComplianceRequirement.applicable_mine_id == current_user.mine_id)

    overdue_stmt = record_count_base.where(ComplianceRecord.status == ComplianceStatus.OVERDUE)
    overdue_count = (await db.execute(overdue_stmt)).scalar_one()

    # 3. Due Soon Count
    due_soon_stmt = record_count_base.where(ComplianceRecord.status == ComplianceStatus.DUE_SOON)
    due_soon_count = (await db.execute(due_soon_stmt)).scalar_one()

    # 4. Total Records for Compliance Percentage
    total_records = (await db.execute(record_count_base)).scalar_one()
    
    # 5. Compliant Records
    compliant_stmt = record_count_base.where(ComplianceRecord.status == ComplianceStatus.COMPLIANT)
    compliant_count = (await db.execute(compliant_stmt)).scalar_one()

    percentage = 0
    if total_records > 0:
        percentage = int((compliant_count / total_records) * 100)

    from app.models.field import SafetyEvent, CorrectiveAction, SafetyEventType, SafetyEventSeverity, ActionStatus

    # Base counts for Phase 4
    event_count_base = select(func.count(SafetyEvent.id)).select_from(SafetyEvent)
    action_count_base = select(func.count(CorrectiveAction.id)).select_from(CorrectiveAction)
    
    if current_user.mine_id:
        event_count_base = event_count_base.where(SafetyEvent.mine_id == current_user.mine_id)
        action_count_base = action_count_base.where(CorrectiveAction.mine_id == current_user.mine_id)

    # 6. Open Findings
    open_findings_stmt = event_count_base.where(SafetyEvent.type.in_([SafetyEventType.HAZARD_OBSERVATION, SafetyEventType.UNSAFE_CONDITION]))
    open_findings_count = (await db.execute(open_findings_stmt)).scalar_one()

    # 7. Critical Findings
    critical_findings_stmt = event_count_base.where(SafetyEvent.severity == SafetyEventSeverity.CRITICAL)
    critical_findings_count = (await db.execute(critical_findings_stmt)).scalar_one()

    # 8. Open Near Misses
    near_misses_stmt = event_count_base.where(SafetyEvent.type == SafetyEventType.NEAR_MISS)
    near_misses_count = (await db.execute(near_misses_stmt)).scalar_one()

    # 9. Incidents
    incidents_stmt = event_count_base.where(SafetyEvent.type == SafetyEventType.INCIDENT)
    incidents_count = (await db.execute(incidents_stmt)).scalar_one()

    # 10. Overdue Actions
    from datetime import datetime, timezone
    overdue_actions_stmt = action_count_base.where(
        and_(
            CorrectiveAction.status.in_([ActionStatus.OPEN, ActionStatus.ASSIGNED, ActionStatus.IN_PROGRESS]),
            CorrectiveAction.due_date < datetime.now(timezone.utc)
        )
    )
    overdue_actions_count = (await db.execute(overdue_actions_stmt)).scalar_one()

    # 11. High/Critical Risk Cases
    high_risk_stmt = event_count_base.where(SafetyEvent.risk_level.in_(["HIGH", "CRITICAL"]))
    high_critical_risk_cases = (await db.execute(high_risk_stmt)).scalar_one()

    # 12. Pending AI Reviews
    pending_ai_stmt = event_count_base.where(
        and_(
            SafetyEvent.ai_prediction_timestamp.is_not(None),
            SafetyEvent.human_reviewed_at.is_(None)
        )
    )
    pending_ai_reviews = (await db.execute(pending_ai_stmt)).scalar_one()

    # 13. AI Overrides
    ai_overrides_stmt = event_count_base.where(SafetyEvent.is_ai_overridden == True)
    ai_overrides_count = (await db.execute(ai_overrides_stmt)).scalar_one()

    # 14. Recurring Issues
    from app.models.analytics import RecurringIssue, AnomalyEvent
    rec_stmt = select(func.count(RecurringIssue.id))
    anom_stmt = select(func.count(AnomalyEvent.id))
    if current_user.mine_id:
        rec_stmt = rec_stmt.where(RecurringIssue.mine_id == current_user.mine_id)
        anom_stmt = anom_stmt.where(AnomalyEvent.mine_id == current_user.mine_id)
        
    recurring_issues_detected = (await db.execute(rec_stmt)).scalar_one()
    anomaly_signals_count = (await db.execute(anom_stmt)).scalar_one()

    return DashboardSummary(
        total_mines=total_mines,
        compliance_percentage=percentage,
        overdue_count=overdue_count,
        due_soon_count=due_soon_count,
        open_findings_count=open_findings_count,
        critical_findings_count=critical_findings_count,
        open_near_misses_count=near_misses_count,
        incidents_count=incidents_count,
        overdue_actions_count=overdue_actions_count,
        high_critical_risk_cases=high_critical_risk_cases,
        recurring_issues_detected=recurring_issues_detected,
        anomaly_signals_count=anomaly_signals_count,
        pending_ai_reviews=pending_ai_reviews,
        ai_overrides_count=ai_overrides_count
    )

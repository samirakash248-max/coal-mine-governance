from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_mines: int
    compliance_percentage: int
    overdue_count: int
    due_soon_count: int
    open_findings_count: int
    critical_findings_count: int
    open_near_misses_count: int
    incidents_count: int
    overdue_actions_count: int
    
    # New Governance Signals
    high_critical_risk_cases: int = 0
    recurring_issues_detected: int = 0
    anomaly_signals_count: int = 0
    pending_ai_reviews: int = 0
    ai_overrides_count: int = 0

import asyncio
import uuid
from datetime import datetime, timezone
import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

from app.models.user import User, Role
from app.models.field import SafetyEvent, SafetyEventType, SafetyEventSeverity, SafetyEventCategory, CorrectiveAction, ActionStatus
from app.services.risk_engine import RiskEngine
from app.services.workflow_service import WorkflowService
from app.services.anomaly_service import AnomalyService
from app.services.recurring_service import RecurringService

class MockResult:
    def __init__(self, scalar_val=0, scalars_val=[]):
        self.scalar_val = scalar_val
        self.scalars_val = scalars_val
    def scalar_one(self): return self.scalar_val
    def scalar_one_or_none(self): return self.scalar_val
    def scalars(self):
        class S:
            def __init__(self, v): self.v = v
            def all(self): return self.v
        return S(self.scalars_val)

class MockDB:
    def __init__(self):
        self.added = []
        self.executed = []
    
    def add(self, obj):
        self.added.append(obj)
        
    async def commit(self):
        pass
        
    async def refresh(self, obj):
        if not hasattr(obj, "id"):
            obj.id = uuid.uuid4()
            
    async def execute(self, stmt):
        self.executed.append(stmt)
        s = str(stmt).lower()
        if "count" in s:
            if "anomaly_events" in s: return MockResult(scalar_val=2)
            if "corrective_actions" in s: return MockResult(scalar_val=1)
            if "safety_events" in s: return MockResult(scalar_val=4)
        if "safety_events" in s and "category" in s:
            ev1 = SafetyEvent(mine_id=uuid.uuid4(), description="test", date=datetime.now(timezone.utc), category=SafetyEventCategory.SAFETY, location_details="Pit 1")
            ev2 = SafetyEvent(mine_id=uuid.uuid4(), description="test", date=datetime.now(timezone.utc), category=SafetyEventCategory.SAFETY, location_details="Pit 1")
            ev3 = SafetyEvent(mine_id=uuid.uuid4(), description="test", date=datetime.now(timezone.utc), category=SafetyEventCategory.SAFETY, location_details="Pit 1")
            ev1.id = uuid.uuid4(); ev2.id = uuid.uuid4(); ev3.id = uuid.uuid4()
            return MockResult(scalars_val=[ev1, ev2, ev3])
        if "corrective_actions" in s and not "count" in s:
            ca = CorrectiveAction(mine_id=uuid.uuid4(), description="Fix", due_date=datetime.now(), status=ActionStatus.OPEN)
            ca.id = uuid.uuid4()
            return MockResult(scalar_val=ca)
        if "safety_events" in s and not "count" in s:
            ev = SafetyEvent(mine_id=uuid.uuid4(), description="test", date=datetime.now(), type=SafetyEventType.INCIDENT, category=SafetyEventCategory.SAFETY, severity=SafetyEventSeverity.HIGH)
            ev.id = uuid.uuid4()
            ev.ai_event_type = SafetyEventType.NEAR_MISS
            ev.ai_category = SafetyEventCategory.ENVIRONMENT
            ev.ai_severity = SafetyEventSeverity.LOW
            return MockResult(scalar_val=ev)
        return MockResult(scalar_val=0, scalars_val=[])

async def test_risk_engine():
    db = MockDB()
    engine = RiskEngine(db)
    event = SafetyEvent(mine_id=uuid.uuid4(), description="A very detailed description of a critical safety issue that happened." * 2, severity=SafetyEventSeverity.CRITICAL, category=SafetyEventCategory.SAFETY, date=datetime.now(timezone.utc))
    result = await engine.evaluate_event_risk(event)
    assert result.risk_score == 85.0
    assert result.risk_level == "CRITICAL"
    print("Risk Engine Test Passed")

async def test_recurring_issue():
    db = MockDB()
    service = RecurringService(db)
    issues = await service.detect_recurring_issues(uuid.uuid4())
    assert len(issues) == 1
    assert issues[0].recurrence_count == 3
    print("Recurring Issue Test Passed")

async def test_workflow():
    db = MockDB()
    manager = User(id=uuid.uuid4(), role=Role.MINE_MANAGER)
    service = WorkflowService(db, manager)
    action = await service.transition_action(uuid.uuid4(), ActionStatus.CLOSED)
    assert action.status == ActionStatus.CLOSED
    print("Workflow Test Passed")

async def test_ai_override():
    db = MockDB()
    manager = User(id=uuid.uuid4(), role=Role.MINE_MANAGER)
    service = WorkflowService(db, manager)
    event = await service.review_ai_prediction(uuid.uuid4(), SafetyEventType.INCIDENT, SafetyEventCategory.SAFETY, SafetyEventSeverity.HIGH)
    assert event.is_ai_overridden == True
    print("AI Override Test Passed")

async def main():
    await test_risk_engine()
    await test_recurring_issue()
    await test_workflow()
    await test_ai_override()

asyncio.run(main())

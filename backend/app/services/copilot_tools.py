from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import uuid
import json
from datetime import datetime, timezone

from app.models.user import User
from app.models.field import CorrectiveAction, ActionStatus, SafetyEvent, SafetyEventType
from app.services.analytics import AnalyticsService
from app.services.rag_retrieval import RAGRetrievalService
from app.providers.ai.base import AIProvider

class CopilotTools:
    """
    Exposes strictly controlled database functions for the Copilot.
    RBAC is enforced by requiring `current_user` in every call.
    """
    
    def __init__(self, db: AsyncSession, current_user: User, ai_provider: AIProvider):
        self.db = db
        self.current_user = current_user
        self.ai_provider = ai_provider
        
    async def get_overdue_actions(self) -> str:
        stmt = select(CorrectiveAction).where(
            and_(
                CorrectiveAction.mine_id == self.current_user.mine_id,
                CorrectiveAction.status.in_([ActionStatus.OPEN, ActionStatus.ASSIGNED]),
                CorrectiveAction.due_date < datetime.now(timezone.utc)
            )
        )
        actions = (await self.db.execute(stmt)).scalars().all()
        data = [{"id": str(a.id), "description": a.description, "due_date": str(a.due_date)} for a in actions]
        return json.dumps(data)

    async def get_recent_incidents(self) -> str:
        stmt = select(SafetyEvent).where(
            and_(
                SafetyEvent.mine_id == self.current_user.mine_id,
                SafetyEvent.type == SafetyEventType.INCIDENT
            )
        ).order_by(SafetyEvent.date.desc()).limit(5)
        
        events = (await self.db.execute(stmt)).scalars().all()
        data = [{"id": str(e.id), "severity": e.severity.value, "description": e.description, "date": str(e.date)} for e in events]
        return json.dumps(data)
        
    async def get_recurring_violations(self) -> str:
        svc = AnalyticsService(self.db)
        data = await svc.get_recurring_violations(self.current_user.mine_id)
        return json.dumps(data)
        
    async def search_knowledge_base(self, query: str) -> str:
        svc = RAGRetrievalService(self.db, self.ai_provider)
        citations = await svc.retrieve_context(query)
        return json.dumps({"citations": citations})
        
    async def get_environmental_data(self) -> str:
        from app.models.operations import EnvironmentReading
        stmt = select(EnvironmentReading).where(EnvironmentReading.mine_id == self.current_user.mine_id).order_by(EnvironmentReading.created_at.desc()).limit(10)
        readings = (await self.db.execute(stmt)).scalars().all()
        return json.dumps([{"parameter": r.parameter, "value": r.value, "unit": r.unit} for r in readings])
        
    async def get_production_trends(self) -> str:
        from app.models.operations import ProductionRecord
        stmt = select(ProductionRecord).where(ProductionRecord.mine_id == self.current_user.mine_id).order_by(ProductionRecord.date.desc()).limit(7)
        records = (await self.db.execute(stmt)).scalars().all()
        return json.dumps([{"date": str(r.date), "target": r.target, "actual": r.actual, "deviation": r.deviation} for r in records])

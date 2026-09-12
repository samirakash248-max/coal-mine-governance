import asyncio
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta

from app.database import async_sessionmaker, engine
from app.models.field import CorrectiveAction, ActionStatus
from app.models.workflow import EscalationRule, Notification
from app.config import get_settings

settings = get_settings()
REDIS_URL = settings.REDIS_URL or "redis://localhost:6379"

async def check_escalations(ctx):
    """
    Periodic task to check for corrective actions that have breached their escalation delays.
    """
    async with async_sessionmaker(engine, class_=AsyncSession)() as db:
        # Find all open actions that are overdue
        now = datetime.now(timezone.utc)
        stmt = select(CorrectiveAction).where(
            and_(
                CorrectiveAction.status.in_([ActionStatus.OPEN, ActionStatus.ASSIGNED, ActionStatus.IN_PROGRESS]),
                CorrectiveAction.due_date < now
            )
        )
        result = await db.execute(stmt)
        overdue_actions = result.scalars().all()
        
        # Load rules (in a real app, query specifically for the conditions)
        rules_stmt = select(EscalationRule).where(EscalationRule.entity_type == "CorrectiveAction")
        rules = (await db.execute(rules_stmt)).scalars().all()
        
        for action in overdue_actions:
            hours_overdue = (now - action.due_date).total_seconds() / 3600
            
            for rule in rules:
                if hours_overdue >= rule.delay_hours:
                    # Trigger escalation notification
                    # We would typically find the user with `escalate_to_role` for this mine
                    # For demo purposes, we will just create a system log or a generic notification
                    print(f"ESCALATION TRIGGERED: Action {action.id} escalated to {rule.escalate_to_role}")
                    
                    notif = Notification(
                        user_id=action.assigned_to_user_id, # Fallback, ideally the manager
                        title="ESCALATION",
                        message=f"Action {action.id} is overdue by {int(hours_overdue)} hours and has been escalated to {rule.escalate_to_role}.",
                        notification_type="ESCALATION",
                        entity_type="CorrectiveAction",
                        entity_id=action.id
                    )
                    db.add(notif)
                    
        await db.commit()

async def check_document_expiries(ctx):
    """
    Periodic task to check for documents expiring within 30 days.
    """
    from app.models.document import Document
    async with async_sessionmaker(engine, class_=AsyncSession)() as db:
        now = datetime.now(timezone.utc)
        thirty_days = now + timedelta(days=30)
        
        stmt = select(Document).where(
            and_(
                Document.expiry_date != None,
                Document.expiry_date <= thirty_days,
                Document.expiry_date > now
            )
        )
        result = await db.execute(stmt)
        expiring_docs = result.scalars().all()
        
        for doc in expiring_docs:
            if doc.owner_id:
                notif = Notification(
                    user_id=doc.owner_id,
                    title="Document Expiring Soon",
                    message=f"Document '{doc.title}' ({doc.document_number}) expires on {doc.expiry_date.strftime('%Y-%m-%d')}.",
                    notification_type="DOCUMENT_EXPIRY",
                    entity_type="Document",
                    entity_id=doc.id
                )
                db.add(notif)
                
        await db.commit()

class WorkerSettings:
    functions = [check_escalations, check_document_expiries]
    cron_jobs = [
        # Run every hour
        # cron(check_escalations, minute=0),
        # cron(check_document_expiries, hour=0, minute=0)
    ]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)

if __name__ == "__main__":
    # Usually executed via `arq app.worker.WorkerSettings`
    pass

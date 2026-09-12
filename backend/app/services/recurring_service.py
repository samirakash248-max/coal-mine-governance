from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta
import uuid
from app.models.analytics import RecurringIssue
from app.models.field import SafetyEvent

class RecurringService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_recurring_issues(self, mine_id: uuid.UUID) -> list[RecurringIssue]:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        stmt = select(SafetyEvent).where(
            and_(SafetyEvent.mine_id == mine_id, SafetyEvent.date >= thirty_days_ago, SafetyEvent.category.is_not(None))
        )
        recent_events = (await self.db.execute(stmt)).scalars().all()
        
        groups = {}
        for event in recent_events:
            key = (event.category, event.location_details or 'General')
            if key not in groups: groups[key] = []
            groups[key].append(event)
            
        recurring_issues = []
        for key, events in groups.items():
            category, location = key
            if len(events) >= 3:
                issue = RecurringIssue(mine_id=mine_id, recurrence_count=len(events), time_window_days=30, location_details=location, issue_category=category.value if hasattr(category, 'value') else category, related_record_ids=[str(e.id) for e in events], recurrence_signal=f'RECURRING_{category}')
                self.db.add(issue)
                recurring_issues.append(issue)
                
        if recurring_issues:
            await self.db.commit()
            for r in recurring_issues: await self.db.refresh(r)
        return recurring_issues

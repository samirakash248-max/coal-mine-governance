from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone, timedelta
import uuid

from app.models.field import SafetyEvent, SafetyEventType

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_recurring_violations(self, mine_id: uuid.UUID):
        """
        Finds locations or categories with >3 identical issues in the last 30 days.
        """
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        stmt = select(SafetyEvent.location_details, SafetyEvent.description).where(
            and_(
                SafetyEvent.mine_id == mine_id,
                SafetyEvent.type.in_([SafetyEventType.HAZARD_OBSERVATION, SafetyEventType.UNSAFE_CONDITION]),
                SafetyEvent.date >= thirty_days_ago,
                SafetyEvent.location_details != None
            )
        )
        
        events = (await self.db.execute(stmt)).all()
        
        # Extremely basic grouping for prototype
        locations = {}
        for ev in events:
            loc = ev.location_details
            locations[loc] = locations.get(loc, 0) + 1
            
        recurring = []
        for loc, count in locations.items():
            if count >= 2: # Set threshold to 2 for easier prototyping
                recurring.append({"location": loc, "count": count, "warning": "Recurring safety hazards detected at this location."})
                
        return recurring

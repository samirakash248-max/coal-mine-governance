from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timezone, timedelta
import uuid

from app.models.analytics import AnomalyEvent
from app.models.field import SafetyEvent

class AnomalyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_anomalies(self, mine_id: uuid.UUID) -> list[AnomalyEvent]:
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        thirty_seven_days_ago = seven_days_ago - timedelta(days=30)
        
        anomalies = []
        recent_stmt = select(func.count(SafetyEvent.id)).where(
            and_(SafetyEvent.mine_id == mine_id, SafetyEvent.date >= seven_days_ago)
        )
        recent_count = (await self.db.execute(recent_stmt)).scalar_one()
        
        baseline_stmt = select(func.count(SafetyEvent.id)).where(
            and_(SafetyEvent.mine_id == mine_id, SafetyEvent.date >= thirty_seven_days_ago, SafetyEvent.date < seven_days_ago)
        )
        baseline_count = (await self.db.execute(baseline_stmt)).scalar_one()
        expected_7_day = (baseline_count / 30.0) * 7.0
        
        if expected_7_day > 0 and recent_count > (expected_7_day * 2) and recent_count >= 3:
            anomaly = AnomalyEvent(mine_id=mine_id, what_was_abnormal='Unusual increase in incidents', baseline_reference=f'Expected {expected_7_day:.1f} per 7 days', observed_value=f'{recent_count} in last 7 days', anomaly_signal='HIGH_FREQUENCY', timestamp=now)
            self.db.add(anomaly)
            anomalies.append(anomaly)
            
        if anomalies:
            await self.db.commit()
            for a in anomalies: await self.db.refresh(a)
        return anomalies

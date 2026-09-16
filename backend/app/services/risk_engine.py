from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
import uuid
import json

from app.models.field import CorrectiveAction, SafetyEvent, SafetyEventSeverity, ActionStatus, SafetyEventType
from app.models.compliance import ComplianceRecord, ComplianceStatus
from app.models.analytics import RiskHistory, RecurringIssue, AnomalyEvent
from app.providers.weather.base import WeatherProvider

class RiskEngine:
    def __init__(self, db: AsyncSession, weather_provider: WeatherProvider = None):
        self.db = db
        self.weather_provider = weather_provider
        
    async def evaluate_mine(self, mine_id: uuid.UUID, lat: float = None, lng: float = None) -> RiskHistory:
        """
        Calculates a deterministic 0-100 risk score based on concrete database rules for a whole mine.
        """
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        
        score = 0
        factors = []
        
        # 1. Overdue Actions (+15 per action, max 45)
        overdue_stmt = select(func.count(CorrectiveAction.id)).where(
            and_(
                CorrectiveAction.mine_id == mine_id,
                CorrectiveAction.due_date < now,
                CorrectiveAction.status.in_([ActionStatus.OPEN, ActionStatus.ASSIGNED, ActionStatus.IN_PROGRESS])
            )
        )
        overdue_count = (await self.db.execute(overdue_stmt)).scalar_one()
        if overdue_count > 0:
            impact = min(overdue_count * 15, 45)
            score += impact
            factors.append({"factor": "Overdue Corrective Actions", "impact": impact, "count": overdue_count})
            
        # 2. Critical Incidents (Last 30 days) (+20 per incident, max 40)
        crit_stmt = select(func.count(SafetyEvent.id)).where(
            and_(
                SafetyEvent.mine_id == mine_id,
                SafetyEvent.severity == SafetyEventSeverity.CRITICAL,
                SafetyEvent.date >= thirty_days_ago
            )
        )
        crit_count = (await self.db.execute(crit_stmt)).scalar_one()
        if crit_count > 0:
            impact = min(crit_count * 20, 40)
            score += impact
            factors.append({"factor": "Recent Critical Incidents", "impact": impact, "count": crit_count})
            
        # 3. Weather Risk (+15 if Severe)
        if lat and lng and self.weather_provider:
            weather = await self.weather_provider.get_current(lat, lng)
            if weather:
                w_assess = await self.weather_provider.assess_risk(weather)
                if w_assess.risk_level.value in ["high", "severe"]:
                    score += 15
                    factors.append({"factor": "Weather Risk Advisory", "impact": 15, "detail": w_assess.risk_level.value})

        # 4. Production Deviations
        from app.models.operations import ProductionRecord
        prod_stmt = select(ProductionRecord).where(
            and_(
                ProductionRecord.mine_id == mine_id,
                ProductionRecord.date >= thirty_days_ago.date()
            )
        )
        prod_records = (await self.db.execute(prod_stmt)).scalars().all()
        rushing_days = sum(1 for p in prod_records if p.deviation < -15.0) # More than 15% behind target
        if rushing_days > 2:
            score += 10
            factors.append({"factor": "Production Target Pressure", "impact": 10, "detail": f"{rushing_days} days severely missing target, risking safety shortcuts."})

        # 5. Environment
        from app.models.operations import EnvironmentReading
        env_stmt = select(EnvironmentReading).where(
            and_(
                EnvironmentReading.mine_id == mine_id,
                EnvironmentReading.parameter == "Dust",
                EnvironmentReading.value > 150.0 # Arbitrary threshold for prototype
            )
        )
        dust_count = len((await self.db.execute(env_stmt)).scalars().all())
        if dust_count > 0:
            score += 10
            factors.append({"factor": "Severe Dust Readings", "impact": 10})

        # Base score floor/ceiling
        score = min(max(score, 0), 100)
        
        if score < 30:
            level = "LOW"
        elif score < 60:
            level = "MEDIUM"
        elif score < 80:
            level = "HIGH"
        else:
            level = "CRITICAL"

        
        history = RiskHistory(
            mine_id=mine_id,
            score=score,
            factors={"explainable_factors": factors, "risk_level": level},
            evaluated_at=now
        )
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        
        return history

    async def evaluate_event_risk(self, event: SafetyEvent) -> SafetyEvent:
        """
        Deterministic Risk Score = 0.35 * Severity + 0.25 * Recurrence + 0.20 * Overdue + 0.15 * Anomaly + 0.05 * DataQuality
        """
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        
        # 1. Severity Score (0-100)
        sev_map = {
            SafetyEventSeverity.LOW: 25,
            SafetyEventSeverity.MEDIUM: 50,
            SafetyEventSeverity.HIGH: 75,
            SafetyEventSeverity.CRITICAL: 100
        }
        severity = event.severity or event.ai_severity or SafetyEventSeverity.MEDIUM
        sev_score = sev_map.get(severity, 50)
        
        # 2. Recurrence Score (0-100)
        # Check if there are similar categories in the last 30 days
        rec_score = 0
        rec_count = 0
        category = event.category or event.ai_category
        if category:
            rec_stmt = select(func.count(SafetyEvent.id)).where(
                and_(
                    SafetyEvent.mine_id == event.mine_id,
                    SafetyEvent.id != event.id,
                    SafetyEvent.date >= thirty_days_ago,
                    SafetyEvent.category == category
                )
            )
            rec_count = (await self.db.execute(rec_stmt)).scalar_one()
            rec_score = min(rec_count * 33.3, 100.0)
            
        # 3. Overdue Corrective Actions Score (0-100)
        overdue_stmt = select(func.count(CorrectiveAction.id)).where(
            and_(
                CorrectiveAction.mine_id == event.mine_id,
                CorrectiveAction.due_date < now,
                CorrectiveAction.status.in_([ActionStatus.OPEN, ActionStatus.ASSIGNED, ActionStatus.IN_PROGRESS])
            )
        )
        overdue_count = (await self.db.execute(overdue_stmt)).scalar_one()
        overdue_score = min(overdue_count * 25.0, 100.0)
        
        # 4. Anomaly Score (0-100)
        anom_stmt = select(func.count(AnomalyEvent.id)).where(
            and_(
                AnomalyEvent.mine_id == event.mine_id,
                AnomalyEvent.timestamp >= thirty_days_ago
            )
        )
        anom_count = (await self.db.execute(anom_stmt)).scalar_one()
        anom_score = min(anom_count * 50.0, 100.0)
        
        # 5. Data Quality Score (0-100) (e.g. detailed description)
        desc_len = len(event.description) if event.description else 0
        dq_score = 100.0 if desc_len > 50 else (50.0 if desc_len > 10 else 0.0)
        
        # Final Formula
        final_score = (0.35 * sev_score) + (0.25 * rec_score) + (0.20 * overdue_score) + (0.15 * anom_score) + (0.05 * dq_score)
        
        # Determine Level
        if final_score < 30:
            level = "LOW"
        elif final_score < 60:
            level = "MEDIUM"
        elif final_score < 80:
            level = "HIGH"
        else:
            level = "CRITICAL"
            
        factors = []
        factors.append(f"{severity.value} severity observation.")
        if rec_count > 0:
            factors.append(f"{rec_count} similar {category.value if category else 'issue'} observations in the last 30 days.")
            event.is_recurring = rec_count >= 3
        if overdue_count > 0:
            factors.append(f"Corrective actions overdue: {overdue_count}.")
        if anom_count > 0:
            factors.append(f"Recent anomalies detected: {anom_count}.")
            
        event.risk_score = round(final_score, 2)
        event.risk_level = level
        event.risk_factors = {"contributors": factors, "explanation": "Risk calculated based on fixed prototype rules."}
        
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        
        return event

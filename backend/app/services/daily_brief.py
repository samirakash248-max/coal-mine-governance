from sqlalchemy.ext.asyncio import AsyncSession
import json
from typing import Dict, Any

from app.models.user import User
from app.providers.ai.base import AIProvider
from app.services.copilot_tools import CopilotTools
from app.services.risk_engine import RiskEngine
from app.providers.weather import get_weather_provider

class DailyBriefService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider, current_user: User):
        self.db = db
        self.ai_provider = ai_provider
        self.current_user = current_user
        self.tools = CopilotTools(db, current_user, ai_provider)
        
    async def generate_brief(self) -> Dict[str, Any]:
        """
        Generates the daily governance brief based on analytical data.
        """
        # Collect Data
        incidents_json = await self.tools.get_recent_incidents()
        overdue_json = await self.tools.get_overdue_actions()
        recurring_json = await self.tools.get_recurring_violations()
        
        # Determine Risk
        risk_engine = RiskEngine(self.db, get_weather_provider("mock")) # Inject default for prototype
        # Ideally fetch mine's lat/long. Using mock coordinates.
        risk_assessment = await risk_engine.evaluate_mine(self.current_user.mine_id, 23.0, 80.0)
        
        # LLM Synthesis for the Brief
        brief_prompt = f"""
You are the AI Governance Analyst. Generate a daily brief using the following structured data.
Return STRICT JSON format:
{{
  "critical_issues": ["bullet 1", "bullet 2"],
  "attention_items": ["bullet 1", "bullet 2"],
  "positive_developments": ["bullet 1"],
  "recommendations": ["bullet 1"]
}}

Data:
Risk Score: {risk_assessment.score}/100
Incidents: {incidents_json}
Overdue Actions: {overdue_json}
Recurring: {recurring_json}
"""
        
        response = await self.ai_provider.process_prompt("You are a data synthesis analyst.", brief_prompt)
        
        try:
            # Fallback for mock provider behavior
            if "mock" in response.lower() or "{" not in response:
                incidents = json.loads(incidents_json)
                overdue = json.loads(overdue_json)
                return {
                    "critical_issues": [f"{len(incidents)} recent incidents detected."] if incidents else [],
                    "attention_items": [f"{len(overdue)} overdue actions requiring attention."] if overdue else [],
                    "positive_developments": ["No severe weather alerts today."],
                    "recommendations": ["Conduct weekly safety stand-down."]
                }
            
            json_str = response[response.find("{"):response.rfind("}")+1]
            return json.loads(json_str)
        except Exception:
            # Safe fallback
            return {
                "critical_issues": ["Error parsing AI brief data."],
                "attention_items": [],
                "positive_developments": [],
                "recommendations": []
            }

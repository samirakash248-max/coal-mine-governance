from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json

from app.models.grievance import Grievance
from app.providers.ai.base import AIProvider

class GrievanceAIProcessor:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider):
        self.db = db
        self.ai_provider = ai_provider
        
    async def process_new_grievance(self, grievance_id: uuid.UUID):
        """
        Analyzes a new grievance and stores AI suggestions for a human to review.
        """
        doc = (await self.db.execute(select(Grievance).where(Grievance.id == grievance_id))).scalar_one_or_none()
        if not doc:
            return
            
        prompt = f"""
You are an HR/Grievance triage assistant.
Analyze this grievance and suggest a Category (Safety, Harassment, Equipment, Pay, Other) and Priority (Low, Medium, High).
Output STRICT JSON:
{{
    "suggested_category": "Category",
    "suggested_priority": "Priority"
}}

Title: {doc.title}
Description: {doc.description}
"""
        response = await self.ai_provider.process_prompt("You are a strict JSON triage assistant.", prompt)
        
        try:
            if "mock" in response.lower() or "{" not in response:
                doc.ai_suggestions = {
                    "suggested_category": "Safety" if "safe" in doc.description.lower() else "Other",
                    "suggested_priority": "High" if "urgent" in doc.description.lower() else "Medium"
                }
            else:
                json_str = response[response.find("{"):response.rfind("}")+1]
                doc.ai_suggestions = json.loads(json_str)
        except Exception:
            doc.ai_suggestions = {"error": "Failed to parse AI suggestion"}
            
        await self.db.commit()

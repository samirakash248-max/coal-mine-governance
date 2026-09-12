from sqlalchemy.ext.asyncio import AsyncSession
import json
from typing import List, Dict, Any

from app.models.user import User
from app.providers.ai.base import AIProvider
from app.services.copilot_tools import CopilotTools
from app.services.domain_guard import is_coal_mine_related, DOMAIN_REFUSAL

class CopilotService:
    def __init__(self, db: AsyncSession, ai_provider: AIProvider, current_user: User):
        self.db = db
        self.ai_provider = ai_provider
        self.current_user = current_user
        self.tools = CopilotTools(db, current_user, ai_provider)
        
    async def process_chat(self, user_message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Orchestration Loop:
        0. Domain Guard
        1. Intent Extraction (JSON Schema)
        2. Tool Execution
        3. LLM Synthesis
        """
        
        # 0. Domain Guard (Deterministic fast-fail)
        if not is_coal_mine_related(user_message):
            return {
                "answer": DOMAIN_REFUSAL,
                "citations": [],
                "recommended_actions": []
            }
        
        intent_prompt = f"""
You are an intent analyzer for a Coal Mine Governance Copilot.
Available tools:
- get_overdue_actions: Use if asking about overdue tasks/actions.
- get_recent_incidents: Use if asking about incidents/accidents.
- get_recurring_violations: Use if asking about recurring problems or bad contractors.
- search_knowledge_base: Use if asking about regulations, compliance rules, or documents.
- get_environmental_data: Use if asking about air, dust, water, or environmental readings.
- get_production_trends: Use if asking about coal production, targets, or deviations.

Analyze the user's message and output STRICT JSON format:
{{
  "tool": "tool_name_or_null",
  "search_query": "if knowledge base, put query here, else null"
}}

User Message: {user_message}
"""
        
        # 1. Ask LLM for intent
        intent_response = await self.ai_provider.process_prompt("You are a strict JSON intent matcher.", intent_prompt)
        
        # Very crude JSON extraction (real app uses structural enforcement)
        tool_name = None
        search_query = None
        citations = []
        try:
            # Fallback for mock provider behavior which might not output strict JSON
            if "mock" in intent_response.lower() or "{" not in intent_response:
                # Mock parsing
                if "overdue" in user_message.lower(): tool_name = "get_overdue_actions"
                elif "incident" in user_message.lower(): tool_name = "get_recent_incidents"
                elif "recurring" in user_message.lower(): tool_name = "get_recurring_violations"
                elif "rule" in user_message.lower() or "regulation" in user_message.lower(): 
                    tool_name = "search_knowledge_base"
                    search_query = user_message
                elif "environment" in user_message.lower() or "dust" in user_message.lower(): tool_name = "get_environmental_data"
                elif "production" in user_message.lower() or "target" in user_message.lower(): tool_name = "get_production_trends"
            else:
                json_str = intent_response[intent_response.find("{"):intent_response.rfind("}")+1]
                intent_data = json.loads(json_str)
                tool_name = intent_data.get("tool")
                search_query = intent_data.get("search_query")
        except Exception:
            pass
            
        # 2. Execute Tool
        tool_context = ""
        if tool_name == "get_overdue_actions":
            tool_context = await self.tools.get_overdue_actions()
        elif tool_name == "get_recent_incidents":
            tool_context = await self.tools.get_recent_incidents()
        elif tool_name == "get_recurring_violations":
            tool_context = await self.tools.get_recurring_violations()
        elif tool_name == "search_knowledge_base":
            kb_res = await self.tools.search_knowledge_base(search_query or user_message)
            kb_data = json.loads(kb_res)
            citations = kb_data.get("citations", [])
            tool_context = kb_res
        elif tool_name == "get_environmental_data":
            tool_context = await self.tools.get_environmental_data()
        elif tool_name == "get_production_trends":
            tool_context = await self.tools.get_production_trends()
            
        # 3. LLM Synthesis
        synthesis_prompt = f"""
You are the Coal Mine Governance Assistant for this application.
Your sole purpose is to assist with coal mine governance, safety, compliance, inspections, corrective actions, risk information, environmental monitoring, mine operations, workforce safety, regulatory reporting, and use of this application.
Answer only questions that are relevant to these areas.
Do not answer general knowledge, entertainment, unrelated programming, politics, sports, personal advice, or unrelated factual questions.
For unrelated questions, politely state that you are designed only for Coal Mine Governance application-related queries.
Do not invent mine data, inspection results, compliance status, risk scores, regulations, or other facts.
When authoritative application data is available, rely on that data.
The application's deterministic Risk Engine remains authoritative for risk scoring.

Context Data: {tool_context}
User Message: {user_message}

If the context contains citations, refer to them. Never hallucinate facts not in the context.
"""
        final_answer = await self.ai_provider.process_prompt(
            "You are the Coal Mine Governance Assistant. Answer ONLY coal mine related queries.", 
            synthesis_prompt
        )
        
        # 4. Generate Recommended Actions (Hardcoded for prototype based on intent)
        recommended_actions = []
        if "overdue" in user_message.lower():
            recommended_actions.append({"id": "action-1", "action": "NOTIFY_OWNERS", "description": "Send automated reminders to all owners of overdue actions."})
        elif "incident" in user_message.lower() or "recurring" in user_message.lower():
            recommended_actions.append({"id": "action-2", "action": "SCHEDULE_INSPECTION", "description": "Schedule a targeted safety inspection."})
            
        return {
            "answer": final_answer,
            "citations": citations,
            "recommended_actions": recommended_actions
        }

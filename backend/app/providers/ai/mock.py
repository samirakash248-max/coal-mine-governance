from .base import AIProvider, AIMessage, AIResponse, AIRole
from typing import Optional
import random

class MockAIProvider(AIProvider):
    async def chat(
        self, 
        messages: list[AIMessage],
        context: Optional[dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AIResponse:
        last_message = messages[-1].content if messages else "No query provided."
        topics = ["safety regulations", "environmental compliance", "operational guidelines", "maintenance records"]
        selected_topic = random.choice(topics)
        content = (f"[Simulated AI Response] Based on the governance guidelines regarding {selected_topic}, "
                   f"your query about '{last_message[:50]}...' suggests careful monitoring of compliance protocols. "
                   "Ensure all safety gear is utilized and regular audits are performed.")
        return AIResponse(
            content=content,
            model="mock-gpt-4",
            provider="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 40, "total_tokens": 50},
            is_simulated=True
        )
    
    async def process_prompt(self, system_prompt: str, user_prompt: str) -> str:
        return "This is a mock AI response. The system is operating in simulated AI mode."

    async def generate_embeddings(self, text: str) -> list[float]:
        # Return a mock 1536-d vector (mostly zeros with some deterministic pseudo-randomness)
        length = 1536
        vector = [0.0] * length
        vector[0] = 0.5
        vector[1] = 0.5
        return vector

    async def summarize(self, text: str, max_length: int = 200) -> str:
        truncated = text[:max_length]
        return f"{truncated}...\n\n[Simulated summary: The provided text highlights key aspects of coal mine safety and compliance.]"
    
    async def explain(
        self, 
        data: dict, 
        context: str,
        explanation_type: str = "general"
    ) -> str:
        keys = ", ".join(data.keys()) if data else "none"
        return (f"[Simulated Explanation] This {explanation_type} explanation of {context} "
                f"shows variations in the following data points: {keys}. "
                "The analysis indicates normal operational variance within permitted thresholds.")
    
    async def extract_compliance_info(
        self,
        text: str,
        regulation_context: Optional[str] = None
    ) -> dict:
        return {
            "potential_violations": ["Missing safety helm check in log", "Delayed machinery maintenance"],
            "requirements_met": ["Daily shift supervisor signature present", "Air quality within normal limits"],
            "risk_score_estimate": random.randint(10, 40),
            "is_simulated": True
        }
        
    async def classify_event(self, text: str) -> dict:
        """Mock implementation of the field report classifier."""
        return {
            "event_type": "hazard_observation",
            "category": "safety",
            "severity": "medium",
            "needs_human_review": True,
            "is_simulated": True
        }

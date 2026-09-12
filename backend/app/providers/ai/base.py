from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class AIRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class AIMessage(BaseModel):
    role: AIRole
    content: str

class AIResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: dict | None = None  # token counts if available
    is_simulated: bool = False  # True for mock provider

class AIProvider(ABC):
    """Abstract interface for AI/LLM providers.
    
    This abstraction supports:
    - Mock provider for development
    - Local model via HTTP API (e.g., POST /v1/chat/completions)
    - Future external providers if needed
    
    IMPORTANT: This is for LLM capabilities only (chat, summarize, explain).
    ML tasks (risk scoring, anomaly detection) use separate ML services.
    """
    
    @abstractmethod
    async def chat(
        self, 
        messages: list[AIMessage],
        context: Optional[dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> AIResponse:
        """General chat/completion. Used for Governance Copilot."""
        ...
    
    @abstractmethod
    async def process_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """Process a text prompt and return the response."""
        ...
        
    @abstractmethod
    async def generate_embeddings(self, text: str) -> list[float]:
        """Generate a 1536-dimensional embedding vector for the text."""
        ...
    
    @abstractmethod
    async def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text. Used for report/inspection summaries."""
        ...
    
    @abstractmethod
    async def explain(
        self, 
        data: dict, 
        context: str,
        explanation_type: str = "general"
    ) -> str:
        """Generate human-readable explanation of analytical results.
        
        The LLM explains results from ML/rule engines — it does NOT
        perform the analysis itself.
        """
        ...
    
    @abstractmethod
    async def extract_compliance_info(
        self,
        text: str,
        regulation_context: Optional[str] = None
    ) -> dict:
        """Extract compliance-relevant information from text.
        Returns structured data about potential violations, requirements.
        """
        ...
        
    @abstractmethod
    async def classify_event(self, text: str) -> dict:
        """Classify a field report into an event type, category, and severity."""
        ...

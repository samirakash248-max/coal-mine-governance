from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, get_ai_provider_dep
from app.providers.ai.base import AIProvider
from app.services.copilot import CopilotService
from app.services.daily_brief import DailyBriefService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_copilot(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    service = CopilotService(db, ai_provider, current_user)
    result = await service.process_chat(req.message, req.history)
    return result

@router.get("/daily-brief", response_model=Dict[str, Any])
async def get_daily_brief(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    service = DailyBriefService(db, ai_provider, current_user)
    brief = await service.generate_brief()
    return brief

class ClassifyRequest(BaseModel):
    text: str

@router.post("/classify", response_model=Dict[str, Any])
async def classify_field_report(
    req: ClassifyRequest,
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    """
    Experimental AI Assistant endpoint. 
    Classifies raw text into event_type, category, and severity.
    DO NOT use this as authoritative compliance data.
    """
    result = await ai_provider.classify_event(req.text)
    return result

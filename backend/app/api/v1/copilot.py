import logging
import time
from fastapi import APIRouter, Depends, Request
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
logger = logging.getLogger("ai.observability")

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

@router.post("/chat", response_model=Dict[str, Any])
async def chat_with_copilot(
    req: ChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    start_time = time.time()
    logger.info(f"AI Request Started: {request.url.path} by user {current_user.id}")
    try:
        service = CopilotService(db, ai_provider, current_user)
        result = await service.process_chat(req.message, req.history)
        duration = time.time() - start_time
        logger.info(f"AI Request Completed: {request.url.path} | Duration: {duration:.2f}s | Provider: {ai_provider.__class__.__name__}")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"AI Request Failed: {request.url.path} | Duration: {duration:.2f}s | Error: {str(e)}")
        raise

@router.get("/daily-brief", response_model=Dict[str, Any])
async def get_daily_brief(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    start_time = time.time()
    logger.info(f"AI Request Started: {request.url.path} by user {current_user.id}")
    try:
        service = DailyBriefService(db, ai_provider, current_user)
        brief = await service.generate_brief()
        duration = time.time() - start_time
        logger.info(f"AI Request Completed: {request.url.path} | Duration: {duration:.2f}s | Provider: {ai_provider.__class__.__name__}")
        return brief
    except Exception as e:
        duration = time.time() - start_time
        is_timeout = "timeout" in str(e).lower()
        if is_timeout:
            logger.warning(f"AI Request Timed Out: {request.url.path} | Duration: {duration:.2f}s")
        else:
            logger.error(f"AI Request Failed: {request.url.path} | Duration: {duration:.2f}s | Error: {str(e)}")
        raise

class ClassifyRequest(BaseModel):
    text: str

@router.post("/classify", response_model=Dict[str, Any])
async def classify_field_report(
    req: ClassifyRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    ai_provider: AIProvider = Depends(get_ai_provider_dep)
):
    start_time = time.time()
    logger.info(f"AI Request Started: {request.url.path} by user {current_user.id}")
    try:
        result = await ai_provider.classify_event(req.text)
        duration = time.time() - start_time
        logger.info(f"AI Request Completed: {request.url.path} | Duration: {duration:.2f}s | Provider: {ai_provider.__class__.__name__}")
        return result
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"AI Request Failed: {request.url.path} | Duration: {duration:.2f}s | Error: {str(e)}")
        raise

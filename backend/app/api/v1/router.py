from fastapi import APIRouter, Depends
from redis import asyncio as aioredis
from sqlalchemy import text
from app.api.deps import get_db, get_settings, get_ai_provider_dep, get_weather_provider_dep, get_ocr_provider_dep, get_storage_provider_dep
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import HealthResponse
from app.config import Settings
import redis
import asyncio

from app.api.v1.auth import router as auth_router
from app.api.v1.hierarchy import router as hierarchy_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

@api_router.get("/health", response_model=HealthResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
    ai_provider = Depends(get_ai_provider_dep),
    weather_provider = Depends(get_weather_provider_dep),
    ocr_provider = Depends(get_ocr_provider_dep),
    storage_provider = Depends(get_storage_provider_dep),
):
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"
        
    redis_status = "ok"
    try:
        redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await asyncio.to_thread(redis_client.ping)
    except Exception:
        redis_status = "error"
        
    # AI Health Check
    ai_status_details = {
        "configured_provider": ai_provider.__class__.__name__,
        "status": "ok",
        "reachable": False,
        "inference_successful": False,
        "error": None
    }
    
    if hasattr(ai_provider, "base_url"):
        import httpx
        try:
            # Check the /health endpoint of the model server (if any) or just the root
            health_url = ai_provider.base_url.replace("/v1", "/health") if "/v1" in ai_provider.base_url else f"{ai_provider.base_url}/health"
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(health_url)
                if res.status_code == 200:
                    ai_status_details["reachable"] = True
                    ai_status_details["inference_successful"] = True # Assumed if server health is OK
                else:
                    ai_status_details["status"] = "degraded"
                    ai_status_details["reachable"] = True
                    ai_status_details["error"] = f"Model server returned {res.status_code}"
        except Exception as e:
            # Backend must not fail just because AI is offline
            ai_status_details["status"] = "degraded"
            ai_status_details["error"] = "AI inference server unreachable"
    else:
        # Mock provider or standard
        ai_status_details["reachable"] = True
        ai_status_details["inference_successful"] = True
        
    overall_status = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
        
    return HealthResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        version=settings.APP_VERSION,
        providers={
            "ai": ai_status_details,
            "weather": weather_provider.__class__.__name__,
            "ocr": ocr_provider.__class__.__name__,
            "storage": storage_provider.__class__.__name__
        }
    )

from app.api.v1.auth import router as auth_router
from app.api.v1.hierarchy import router as hierarchy_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.field import router as field_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.audit import router as audit_router
from app.api.v1.weather import router as weather_router
from app.api.v1.documents import router as documents_router
from app.api.v1.copilot import router as copilot_router
from app.api.v1.operations import router as operations_router
from app.api.v1.grievances import router as grievances_router
from app.api.v1.reports import router as reports_router
from app.api.v1.analytics import router as analytics_router

from app.api.v1.inspections import router as inspections_router
from app.api.v1.settings import router as settings_router

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(hierarchy_router, prefix="/hierarchy", tags=["Hierarchy"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(field_router, prefix="/field", tags=["Field Operations"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(audit_router, prefix="/audit", tags=["Audit Trail"])
api_router.include_router(weather_router, prefix="/weather", tags=["Weather"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(copilot_router, prefix="/copilot", tags=["AI Copilot"])
api_router.include_router(operations_router, prefix="/operations", tags=["Operations"])
api_router.include_router(grievances_router, prefix="/grievances", tags=["Grievances"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(inspections_router, prefix="/inspections", tags=["Inspections"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])

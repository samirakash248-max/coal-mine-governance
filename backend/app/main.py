from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging
from sqlalchemy import text
from redis import asyncio as aioredis
import uvicorn

from app.config import get_settings
from app.database import engine
from app.core.exceptions import register_exception_handlers
from app.api.v1.router import api_router
from app.api.public.v1.transparency import router as public_router

logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up CoalMine Governance Platform")
    
    # Verify DB connection and create tables
    try:
        from app.models.base import Base
        import app.models  # This imports all models
        from app.models.analytics import AnomalyEvent, RecurringIssue
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("SELECT 1"))
        logger.info("Database tables created and connection verified")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        
    # Verify Redis connection
    try:
        redis = aioredis.from_url(settings.REDIS_URL)
        await redis.ping()
        logger.info("Redis connection verified")
        await redis.close()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        
    yield
    
    # Shutdown
    logger.info("Shutting down CoalMine Governance Platform")
    await engine.dispose()

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="Backend for the CoalMine governance platform.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Include v1 Router
app.include_router(api_router, prefix="/api/v1")
app.include_router(public_router, prefix="/api/public/v1", tags=["Public Transparency"])

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=settings.DEBUG)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.models.contractor import Contractor, Worker
from app.models.operations import EnvironmentReading, ProductionRecord
from app.schemas.secondary import ContractorResponse, WorkerResponse, EnvironmentReadingResponse, ProductionRecordResponse

router = APIRouter()

@router.get("/contractors", response_model=list[ContractorResponse])
async def list_contractors(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Contractor).where(Contractor.mine_id == current_user.mine_id)
    return (await db.execute(stmt)).scalars().all()

@router.get("/environment", response_model=list[EnvironmentReadingResponse])
async def list_environment(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(EnvironmentReading).where(EnvironmentReading.mine_id == current_user.mine_id).order_by(EnvironmentReading.created_at.desc()).limit(20)
    return (await db.execute(stmt)).scalars().all()

@router.get("/production", response_model=list[ProductionRecordResponse])
async def list_production(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(ProductionRecord).where(ProductionRecord.mine_id == current_user.mine_id).order_by(ProductionRecord.date.desc()).limit(30)
    return (await db.execute(stmt)).scalars().all()

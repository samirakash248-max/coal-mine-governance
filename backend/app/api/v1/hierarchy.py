import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.hierarchy import Mine
from app.schemas.hierarchy import MineResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/mines", response_model=list[MineResponse])
async def get_mines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Mine)
    
    if current_user.mine_id:
        stmt = stmt.where(Mine.id == current_user.mine_id)
    elif current_user.region_id:
        stmt = stmt.where(Mine.region_id == current_user.region_id)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/mines/{mine_id}", response_model=MineResponse)
async def get_mine(
    mine_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base security check
    if current_user.mine_id and current_user.mine_id != mine_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this mine")
        
    stmt = select(Mine).where(Mine.id == mine_id)
    result = await db.execute(stmt)
    mine = result.scalar_one_or_none()
    
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
        
    # Region security check
    if current_user.region_id and mine.region_id != current_user.region_id:
        raise HTTPException(status_code=403, detail="Not authorized to view mines in this region")
        
    return mine

@router.get("/mines/{mine_id}/nearby", response_model=list[MineResponse])
async def get_nearby_mines(
    mine_id: uuid.UUID,
    radius_km: float = 50.0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from sqlalchemy import func
    
    # 1. Get target mine
    target_mine = (await db.execute(select(Mine).where(Mine.id == mine_id))).scalar_one_or_none()
    if not target_mine or not target_mine.location_geom:
        return []
        
    # 2. Base query
    stmt = select(Mine).where(Mine.id != mine_id)
    
    # 3. Security Check (Same as normal mines endpoint)
    if current_user.mine_id:
        # A mine user can only see their own mine, so nearby is empty for them unless they have broader scope
        return []
    elif current_user.region_id:
        stmt = stmt.where(Mine.region_id == current_user.region_id)
        
    # 4. Spatial PostGIS Query
    # Convert km to degrees roughly (1 degree ~ 111 km)
    radius_deg = radius_km / 111.0
    
    stmt = stmt.where(
        func.ST_DWithin(Mine.location_geom, target_mine.location_geom, radius_deg)
    ).limit(10)
    
    result = await db.execute(stmt)
    return result.scalars().all()

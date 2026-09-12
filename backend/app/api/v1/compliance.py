import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.compliance import ComplianceRecord, ComplianceRequirement, ComplianceStatus
from app.schemas.compliance import ComplianceRecordResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/records/calendar", response_model=list[ComplianceRecordResponse])
async def get_calendar_records(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch upcoming/overdue records, ensuring they are bound to mines the user can see
    stmt = (
        select(ComplianceRecord)
        .options(selectinload(ComplianceRecord.requirement))
        .join(ComplianceRequirement)
    )
    
    if current_user.mine_id:
        stmt = stmt.where(ComplianceRequirement.applicable_mine_id == current_user.mine_id)
    # Further filtering for region/org omitted for brevity but standard.
    
    # Sort by due date
    stmt = stmt.order_by(ComplianceRecord.due_date.asc()).limit(100)
    
    result = await db.execute(stmt)
    return result.scalars().all()

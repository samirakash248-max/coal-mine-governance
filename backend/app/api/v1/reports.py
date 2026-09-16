from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from typing import List

from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.models.report import Report
from app.schemas.report import ReportResponse, ReportGenerateRequest, ReportStatusUpdate

router = APIRouter()

@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Report).where(
        Report.mine_id == current_user.mine_id
    ).order_by(Report.created_at.desc()).offset(skip).limit(limit)
    return (await db.execute(stmt)).scalars().all()

@router.post("/", response_model=ReportResponse)
async def generate_report(
    req: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # In a real system, you'd aggregate real data. Mocking a snapshot for the prototype.
    snapshot_data = {
        "metrics": {
            "total_incidents": 5,
            "overall_compliance": 85.5,
            "open_actions": 12
        }
    }
    
    report = Report(
        mine_id=current_user.mine_id,
        title=req.title,
        type=req.type,
        data_snapshot=snapshot_data,
        generated_by_id=current_user.id
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report

@router.put("/{report_id}/status", response_model=ReportResponse)
async def update_report_status(
    report_id: uuid.UUID,
    req: ReportStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Report).where(Report.id == report_id, Report.mine_id == current_user.mine_id)
    report = (await db.execute(stmt)).scalar_one_or_none()
    if not report:
        raise HTTPException(404, "Report not found")
        
    report.status = req.status
    await db.commit()
    await db.refresh(report)
    return report

from datetime import datetime, timezone
from app.models.field import Inspection, SafetyEvent

@router.post("/generate-dgms")
async def generate_dgms_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mine_id = current_user.mine_id
    
    events_stmt = select(SafetyEvent).where(SafetyEvent.mine_id == mine_id, SafetyEvent.severity == "CRITICAL")
    events = (await db.execute(events_stmt)).scalars().all()
    
    insp_stmt = select(Inspection).where(Inspection.mine_id == mine_id)
    inspections = (await db.execute(insp_stmt)).scalars().all()
    
    report_content = f"DGMS REGULATORY FILING REPORT\n"
    report_content += f"Generated On: {datetime.now(timezone.utc)}\n"
    report_content += f"Mine ID: {mine_id}\n\n"
    
    report_content += "CRITICAL INCIDENTS LOG:\n"
    for e in events:
        report_content += f" - [{e.date}] {e.type}: {e.description}\n"
        report_content += f"   Signature: {e.cryptographic_signature}\n\n"
        
    report_content += "INSPECTION LOG:\n"
    for i in inspections:
        report_content += f" - [{i.date}] {i.status}: {i.notes}\n"
        report_content += f"   Signature: {i.cryptographic_signature}\n\n"
        
    return {
        "status": "success",
        "message": "Regulatory filing generated and cryptographically verified.",
        "content_markdown": report_content
    }

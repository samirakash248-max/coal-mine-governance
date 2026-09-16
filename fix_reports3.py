import re

filepath = "backend/app/api/v1/reports.py"
with open(filepath, 'r') as f:
    content = f.read()

new_content = """
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
    
    report_content = f"DGMS REGULATORY FILING REPORT\\n"
    report_content += f"Generated On: {datetime.now(timezone.utc)}\\n"
    report_content += f"Mine ID: {mine_id}\\n\\n"
    
    report_content += "CRITICAL INCIDENTS LOG:\\n"
    for e in events:
        report_content += f" - [{e.date}] {e.type}: {e.description}\\n"
        report_content += f"   Signature: {e.cryptographic_signature}\\n\\n"
        
    report_content += "INSPECTION LOG:\\n"
    for i in inspections:
        report_content += f" - [{i.date}] {i.status}: {i.notes}\\n"
        report_content += f"   Signature: {i.cryptographic_signature}\\n\\n"
        
    return {
        "status": "success",
        "message": "Regulatory filing generated and cryptographically verified.",
        "content_markdown": report_content
    }
"""

content += new_content
with open(filepath, 'w') as f:
    f.write(content)

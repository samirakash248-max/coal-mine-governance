import re

filepath = "backend/app/api/v1/field.py"
with open(filepath, 'r') as f:
    content = f.read()

# Fix get_event
old_get = """    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event"""
new_get = """    event = (await db.execute(stmt)).scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if current_user.mine_id and event.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return event"""
content = content.replace(old_get, new_get)

# Fix create_safety_event
old_create = """    event = SafetyEvent(
        **event_data,
        date=datetime.now(timezone.utc),
        reporter_id=current_user.id
    )"""
new_create = """    if current_user.mine_id and event_data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create event for another mine")
    event = SafetyEvent(
        **event_data,
        date=datetime.now(timezone.utc),
        reporter_id=current_user.id
    )"""
content = content.replace(old_create, new_create)

# Fix review_event
# Note: workflow_svc handles review_ai_prediction, let's see if it handles mine_id.
# Better to add check directly in route.
old_review = """@router.post("/events/{event_id}/review", response_model=SafetyEventResponse)
async def review_event(
    event_id: uuid.UUID,
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_UPDATE))
):
    workflow_svc = WorkflowService(db, current_user)"""
new_review = """@router.post("/events/{event_id}/review", response_model=SafetyEventResponse)
async def review_event(
    event_id: uuid.UUID,
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.SAFETY_UPDATE))
):
    event = (await db.execute(select(SafetyEvent).where(SafetyEvent.id == event_id))).scalar_one_or_none()
    if not event or (current_user.mine_id and event.mine_id != current_user.mine_id):
        raise HTTPException(status_code=404, detail="Event not found")
    workflow_svc = WorkflowService(db, current_user)"""
content = content.replace(old_review, new_review)

with open(filepath, 'w') as f:
    f.write(content)


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.settings import UserSettings, NotificationPreference
from app.schemas.settings import UserSettingsUpdate, UserSettingsResponse, NotificationPreferenceUpdate, NotificationPreferenceResponse
from app.api.deps import get_current_user
import uuid

router = APIRouter()

@router.get('/preferences', response_model=UserSettingsResponse)
async def get_preferences(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(UserSettings).where(UserSettings.user_id == current_user.id)
    prefs = (await db.execute(stmt)).scalar_one_or_none()
    if not prefs:
        prefs = UserSettings(user_id=current_user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
    return prefs

@router.put('/preferences', response_model=UserSettingsResponse)
async def update_preferences(prefs_in: UserSettingsUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(UserSettings).where(UserSettings.user_id == current_user.id)
    prefs = (await db.execute(stmt)).scalar_one_or_none()
    if not prefs:
        prefs = UserSettings(user_id=current_user.id)
        db.add(prefs)
    
    update_data = prefs_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prefs, key, value)
        
    await db.commit()
    await db.refresh(prefs)
    return prefs

@router.get('/notifications', response_model=NotificationPreferenceResponse)
async def get_notifications(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    notifs = (await db.execute(stmt)).scalar_one_or_none()
    if not notifs:
        notifs = NotificationPreference(user_id=current_user.id)
        db.add(notifs)
        await db.commit()
        await db.refresh(notifs)
    return notifs

@router.put('/notifications', response_model=NotificationPreferenceResponse)
async def update_notifications(notifs_in: NotificationPreferenceUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(NotificationPreference).where(NotificationPreference.user_id == current_user.id)
    notifs = (await db.execute(stmt)).scalar_one_or_none()
    if not notifs:
        notifs = NotificationPreference(user_id=current_user.id)
        db.add(notifs)
        
    update_data = notifs_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(notifs, key, value)
        
    await db.commit()
    await db.refresh(notifs)
    return notifs


import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import uuid

from app.database import get_db
from app.config import get_settings, Settings
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User, Role
from app.schemas.auth import Token, GoogleAuthCallback
from app.schemas.user import UserResponse
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/google/login")
async def get_google_auth_url(settings: Settings = Depends(get_settings)):
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")
    
    import secrets
    state = secrets.token_urlsafe(32)
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        "scope=openid email profile&"
        "access_type=offline&"
        f"state={state}"
    )
    return {"url": url, "state": state}

@router.post("/google/callback", response_model=Token)
async def google_auth_callback(
    payload: GoogleAuthCallback,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth is not configured on the server")

    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback"
    
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": payload.code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )
        if token_response.status_code != 200:
            logger.error(f"Google OAuth token exchange failed: {token_response.text}")
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        userinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_response.status_code != 200:
            logger.error(f"Google OAuth userinfo failed: {userinfo_response.text}")
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
            
        userinfo = userinfo_response.json()
        
    email = userinfo.get("email")
    email_verified = userinfo.get("email_verified")
    
    if not email:
        raise HTTPException(status_code=400, detail="No email provided by Google")
    if not email_verified:
        raise HTTPException(status_code=400, detail="Google email is not verified")
        
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        random_password = uuid.uuid4().hex
        user = User(
            email=email,
            full_name=userinfo.get("name", "Google User"),
            hashed_password=hash_password(random_password),
            role=Role.FIELD_INSPECTOR,
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    app_access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    
    return {"access_token": app_access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

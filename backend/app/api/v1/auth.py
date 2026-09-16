from app.services.audit import log_audit_event
from fastapi import Request
import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
import uuid
import asyncio
from datetime import datetime

from app.database import get_db
from app.config import get_settings, Settings
from app.core.security import verify_password, create_access_token, hash_password
from app.models.user import User, Role
from app.schemas.auth import Token, GoogleAuthCallback, ChangePasswordRequest, SignupRequest
from app.schemas.user import UserResponse, UserUpdateMe
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

_failed_logins = {} # simple in-memory progressive delay

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    client_ip = request.client.host if request and request.client else "unknown"
    now = datetime.now()
    attempts, last_time = _failed_logins.get(client_ip, (0, now))
    
    if now - last_time > timedelta(minutes=15):
        attempts = 0
        
    if attempts > 3:
        delay = min(2 ** (attempts - 3), 5)
        await asyncio.sleep(delay)

    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        _failed_logins[client_ip] = (attempts + 1, datetime.now())
        if user:
            await log_audit_event(db, user.id, user.role.value, "LOGIN_FAILURE", "User", user.id, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        _failed_logins[client_ip] = (attempts + 1, datetime.now())
        await log_audit_event(db, user.id, user.role.value, "LOGIN_FAILURE_INACTIVE", "User", user.id, request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password", # Do not reveal account status vs existence to brute force
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    _failed_logins.pop(client_ip, None)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    
    await log_audit_event(db, user.id, user.role.value, "LOGIN_SUCCESS", "User", user.id, request)
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
    request: Request,
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
        await log_audit_event(db, user.id, user.role.value, "USER_CREATED", "User", user.id, request)
        
    if not user.is_active:
        await log_audit_event(db, user.id, user.role.value, "LOGIN_FAILURE_INACTIVE", "User", user.id, request)
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    app_access_token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=access_token_expires
    )
    
    await log_audit_event(db, user.id, user.role.value, "LOGIN_SUCCESS", "User", user.id, request)
    return {"access_token": app_access_token, "token_type": "bearer"}


@router.post("/signup", response_model=UserResponse)
async def signup(
    request: Request,
    payload: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=Role.MINE_OFFICER,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await log_audit_event(db, user.id, user.role.value, "USER_CREATED", "User", user.id, request)
    return user

@router.post("/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await log_audit_event(db, current_user.id, current_user.role.value, "LOGOUT", "User", current_user.id, request)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdateMe,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the currently authenticated user's own profile. Role and email are not modifiable here."""
    if update_data.full_name is not None:
        stripped = update_data.full_name.strip()
        if not stripped:
            raise HTTPException(status_code=422, detail="Full name cannot be empty")
        current_user.full_name = stripped
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/change-password", status_code=204)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change the password for the currently authenticated user only."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        await log_audit_event(db, current_user.id, current_user.role.value, "PASSWORD_CHANGE_FAILURE", "User", current_user.id, request)
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=422, detail="New password must be at least 8 characters")
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    
    await log_audit_event(db, current_user.id, current_user.role.value, "PASSWORD_CHANGED", "User", current_user.id, request)
    return None





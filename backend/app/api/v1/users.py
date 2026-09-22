import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.user import User, Role
from app.schemas.user import UserResponse, UserUpdateMe
from app.schemas.pagination import PaginatedResponse
from app.api.deps import get_pagination, PaginationParams
from app.api.deps import require_permission, require_role, get_current_user, apply_tenant_scope, validate_tenant_mutation, force_tenant_creation
from app.core.permissions import Permission
from app.core.security import hash_password
from app.services.audit import log_audit_event
from pydantic import BaseModel

router = APIRouter()

class UserCreateAdmin(BaseModel):
    email: str
    password: str
    full_name: str
    role: Role
    is_active: bool = True

class UserUpdateAdmin(BaseModel):
    full_name: str | None = None
    role: Role | None = None
    is_active: bool | None = None
    password: str | None = None

from sqlalchemy import func
@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: User = Depends(require_permission(Permission.USER_READ))
):
    stmt = select(User).order_by(User.email).offset(pagination.skip).limit(pagination.limit)
    stmt = apply_tenant_scope(stmt, User, current_user)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=UserResponse)
async def create_user(
    request: Request,
    req: UserCreateAdmin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_CREATE))
):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = User(
        email=req.email,
        full_name=req.full_name,
        hashed_password=hash_password(req.password),
        role=req.role,
        is_active=req.is_active
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await log_audit_event(db, current_user.id, current_user.role.value, "USER_CREATED", "User", user.id, request)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_READ))
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    req: UserUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    # STRICT TENANT ISOLATION (IDOR Prevention):
    # A MINE_MANAGER can only modify users belonging to their own mine.
    if current_user.role == Role.MINE_MANAGER and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot modify users from another mine.")
        
    old_role = user.role
    old_active = user.is_active
        
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.role is not None:
        user.role = req.role
    if req.is_active is not None:
        user.is_active = req.is_active
    if req.password is not None and len(req.password) >= 8:
        user.hashed_password = hash_password(req.password)
        
    if (req.role is not None and req.role != old_role) or (req.is_active is not None and req.is_active == False):
        if old_role in (Role.ADMIN, Role.SYSTEM_ADMIN):
            # Check if this is the last admin
            stmt = select(User).where(User.role.in_([Role.ADMIN, Role.SYSTEM_ADMIN]), User.is_active == True)
            admins = (await db.execute(stmt)).scalars().all()
            if len(admins) <= 1 and admins[0].id == user_id:
                raise HTTPException(status_code=400, detail="Cannot modify or deactivate the last active administrator")
        
    await db.commit()
    await db.refresh(user)
    
    # CRYPTOGRAPHIC AUDIT TRAIL:
    # We log the event using our unified ledger which computes a rolling SHA-256 hash chain for absolute immutability.
    await log_audit_event(db, current_user.id, current_user.role.value, "USER_UPDATED", "User", user.id, request)
    if req.role is not None and req.role != old_role:
        await log_audit_event(db, current_user.id, current_user.role.value, "ROLE_CHANGED", "User", user.id, request, before_state={"role": old_role}, after_state={"role": user.role})
    if req.is_active is not None and req.is_active != old_active and not req.is_active:
        await log_audit_event(db, current_user.id, current_user.role.value, "USER_DEACTIVATED", "User", user.id, request)
        
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_DELETE))
):
    # Instead of actual deletion, we just deactivate to preserve audit logs
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if user.role in (Role.ADMIN, Role.SYSTEM_ADMIN):
        stmt = select(User).where(User.role.in_([Role.ADMIN, Role.SYSTEM_ADMIN]), User.is_active == True)
        admins = (await db.execute(stmt)).scalars().all()
        if len(admins) <= 1 and admins[0].id == user_id:
            raise HTTPException(status_code=400, detail="Cannot deactivate the last active administrator")
    
    user.is_active = False
    await db.commit()
    await log_audit_event(db, current_user.id, current_user.role.value, "USER_DEACTIVATED", "User", user.id, request)
    return None



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
    mine_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    region_id: uuid.UUID | None = None
    subsidiary_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None

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
        
    data_dict = {
        "email": req.email,
        "full_name": req.full_name,
        "hashed_password": hash_password(req.password),
        "role": req.role,
        "is_active": req.is_active,
        "mine_id": req.mine_id,
        "organization_id": req.organization_id,
        "region_id": req.region_id,
        "subsidiary_id": req.subsidiary_id,
        "department_id": req.department_id,
    }
    force_tenant_creation(data_dict, current_user)
    
    if current_user.role == Role.MINE_MANAGER:
        # Prevent privilege escalation
        allowed_roles = [Role.MINE_MANAGER, Role.MINE_OFFICER, Role.FIELD_INSPECTOR, Role.CONTRACTOR, Role.MINER]
        if req.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="MINE_MANAGER cannot create users with elevated corporate roles.")
            
    user = User(**data_dict)
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
    if current_user.role not in [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER, Role.REGULATORY_AUDITOR, Role.REGULATOR]:
        if current_user.mine_id and user.mine_id != current_user.mine_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access users from your own mine.")
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
    if current_user.role not in [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER, Role.REGULATORY_AUDITOR, Role.REGULATOR]:
        if current_user.mine_id and user.mine_id != current_user.mine_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access users from your own mine.")
        
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
    if current_user.role not in [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER, Role.REGULATORY_AUDITOR, Role.REGULATOR]:
        if current_user.mine_id and user.mine_id != current_user.mine_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access users from your own mine.")
        
    if user.role in (Role.ADMIN, Role.SYSTEM_ADMIN):
        stmt = select(User).where(User.role.in_([Role.ADMIN, Role.SYSTEM_ADMIN]), User.is_active == True)
        admins = (await db.execute(stmt)).scalars().all()
        if len(admins) <= 1 and admins[0].id == user_id:
            raise HTTPException(status_code=400, detail="Cannot deactivate the last active administrator")
    
    user.is_active = False
    await db.commit()
    await log_audit_event(db, current_user.id, current_user.role.value, "USER_DEACTIVATED", "User", user.id, request)
    return None



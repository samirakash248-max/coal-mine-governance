import re

filepath = "backend/app/api/v1/users.py"
with open(filepath, 'r') as f:
    content = f.read()

# Update the patch route to include tenant isolation
target_route = """@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    req: UserUpdateAdmin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission(Permission.USER_UPDATE))
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")"""

replacement_route = """@router.patch("/{user_id}", response_model=UserResponse)
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
        
    # STRICT TENANT ISOLATION (IDOR Prevention):
    # A MINE_MANAGER can only modify users belonging to their own mine.
    if current_user.role == Role.MINE_MANAGER and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot modify users from another mine.")"""

content = content.replace(target_route, replacement_route)

# Add comment about cryptographic audit
target_audit = """    await log_audit_event(db, current_user.id, current_user.role.value, "USER_UPDATED", "User", user.id, request)"""
replacement_audit = """    # CRYPTOGRAPHIC AUDIT TRAIL:
    # We log the event using our unified ledger which computes a rolling SHA-256 hash chain for absolute immutability.
    await log_audit_event(db, current_user.id, current_user.role.value, "USER_UPDATED", "User", user.id, request)"""

content = content.replace(target_audit, replacement_audit)

with open(filepath, 'w') as f:
    f.write(content)

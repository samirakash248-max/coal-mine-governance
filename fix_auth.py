import re
filepath = "backend/app/api/v1/auth.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

target = """@router.post("/signup", response_model=UserResponse)
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
    return user"""

replacement = """# Signup route removed for enterprise security. Users must be provisioned by an Admin."""
content = content.replace(target, replacement)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

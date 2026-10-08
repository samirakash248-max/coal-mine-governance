import re
filepath = "backend/app/api/v1/users.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

target1 = """class UserCreateAdmin(BaseModel):
    email: str
    password: str
    full_name: str
    role: Role
    is_active: bool = True"""

replacement1 = """class UserCreateAdmin(BaseModel):
    email: str
    password: str
    full_name: str
    role: Role
    is_active: bool = True
    mine_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    region_id: uuid.UUID | None = None
    subsidiary_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None"""

content = content.replace(target1, replacement1)

target2 = """    user = User(
        email=req.email,
        full_name=req.full_name,
        hashed_password=hash_password(req.password),
        role=req.role,
        is_active=req.is_active
    )"""

replacement2 = """    data_dict = {
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
            
    user = User(**data_dict)"""

content = content.replace(target2, replacement2)

# Fix duplicate checks in get_user
target3 = """    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current_user.mine_id and user.mine_id != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Forbidden")"""

replacement3 = """    if current_user.role not in [Role.SYSTEM_ADMIN, Role.ADMIN, Role.CORPORATE_MANAGER, Role.REGULATORY_AUDITOR, Role.REGULATOR]:
        if current_user.mine_id and user.mine_id != current_user.mine_id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only access users from your own mine.")"""

content = content.replace(target3, replacement3)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

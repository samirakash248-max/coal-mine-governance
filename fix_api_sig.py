import re

filepath = "backend/app/api/v1/field.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add import
content = content.replace("from app.core.permissions import Permission", "from app.core.permissions import Permission\nfrom app.core.security import generate_cryptographic_signature")

# Add signature generation in create_safety_event
target = """    event = SafetyEvent(
        **event_data,
        date=datetime.now(timezone.utc),
        reporter_id=current_user.id
    )"""

replacement = """    event = SafetyEvent(
        **event_data,
        date=datetime.now(timezone.utc),
        reporter_id=current_user.id
    )
    event.cryptographic_signature = generate_cryptographic_signature(event_data)"""

content = content.replace(target, replacement)

with open(filepath, 'w') as f:
    f.write(content)

filepath = "backend/app/api/v1/inspections.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add import
content = content.replace("from app.core.permissions import Permission", "from app.core.permissions import Permission\nfrom app.core.security import generate_cryptographic_signature")

# Add signature generation
target = """    data = inspection_in.model_dump()
    if current_user.mine_id and data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create an inspection for another mine")
    inspection = Inspection(**data, inspector_id=current_user.id)"""

replacement = """    data = inspection_in.model_dump()
    if current_user.mine_id and data.get("mine_id") != current_user.mine_id:
        raise HTTPException(status_code=403, detail="Cannot create an inspection for another mine")
    inspection = Inspection(**data, inspector_id=current_user.id)
    inspection.cryptographic_signature = generate_cryptographic_signature(data)"""

content = content.replace(target, replacement)

with open(filepath, 'w') as f:
    f.write(content)

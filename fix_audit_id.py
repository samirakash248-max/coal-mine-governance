import re

filepath = "backend/app/api/v1/copilot.py"
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace("entity_id=req.mine_id,", "entity_id=req.mine_id or current_user.id,")

with open(filepath, 'w') as f:
    f.write(content)

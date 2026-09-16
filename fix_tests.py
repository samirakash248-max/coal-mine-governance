import re

filepath = "backend/tests/test_isolation.py"
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace("inspector_id=None", "inspector_id=user_a.id")
with open(filepath, 'w') as f:
    f.write(content)

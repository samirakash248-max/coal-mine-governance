import re

filepath = "backend/tests/test_isolation.py"
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace("email=\"user_isol@example.com\",", "id=uuid.uuid4(), email=\"user_isol@example.com\",")

with open(filepath, 'w') as f:
    f.write(content)

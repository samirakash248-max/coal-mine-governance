import re
filepath = "backend/app/core/security.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

target = 'pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")'
replacement = 'pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")'
content = content.replace(target, replacement)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

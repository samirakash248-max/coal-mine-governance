import re

filepath = "backend/app/api/v1/router.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add import
content = content.replace("from app.api.v1 import auth", "from app.api.v1 import auth, iot")

# Add router
target = "api_router.include_router(auth.router, prefix=\"/auth\", tags=[\"auth\"])"
replacement = "api_router.include_router(auth.router, prefix=\"/auth\", tags=[\"auth\"])\napi_router.include_router(iot.router, prefix=\"/iot\", tags=[\"iot\"])"
content = content.replace(target, replacement)

with open(filepath, 'w') as f:
    f.write(content)

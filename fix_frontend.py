import re

filepath = "frontend/src/pages/HealthCheck.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix useState
content = content.replace("import { useState } from 'react';\n", "")

# Fix useMock usage
content = content.replace("checked={useMock}", "checked={false}")
content = content.replace("onChange={(e) => setUseMock(e.target.checked)}", "")
content = content.replace("setUseMock", "console.log")
content = content.replace("useMock", "false")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

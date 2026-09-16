import re

filepath = "frontend/src/pages/Login.tsx"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace mock signup with actual API call (or a realistic placeholder error if no endpoint)
old_mock = """        // Mock signup flow as backend endpoint is not implemented
        setTimeout(() => {
          setSuccess('Account created successfully! Please sign in.');
          setMode('signin');
        }, 1000);"""

new_mock = """        throw new Error('Public registration is disabled. Please contact your system administrator to provision your account.');"""

content = content.replace(old_mock, new_mock)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

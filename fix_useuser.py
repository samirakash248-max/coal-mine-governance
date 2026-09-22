import re

filepath = "frontend/src/hooks/useUser.ts"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = """export interface UserProfile {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  department: string;
  status: string;
}"""

replacement = """export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  permissions: string[];
}"""

content = content.replace(target, replacement)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

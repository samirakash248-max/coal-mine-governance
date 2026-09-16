import re

filepath = "backend/app/core/security.py"
with open(filepath, 'r') as f:
    content = f.read()

new_code = """
import hashlib
import json

def generate_cryptographic_signature(payload: dict) -> str:
    # Remove mutable or system fields before hashing
    clean_payload = {k: v for k, v in payload.items() if k not in ["id", "created_at", "updated_at", "cryptographic_signature"]}
    # Sort keys for deterministic hashing
    encoded = json.dumps(clean_payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
"""

content += new_code
with open(filepath, 'w') as f:
    f.write(content)

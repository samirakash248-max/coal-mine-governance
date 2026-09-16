import re

filepath = "backend/app/models/field.py"
with open(filepath, 'r') as f:
    content = f.read()

# Add cryptographic_signature to Inspection
insp_target = "idempotency_key = Column(String, nullable=True)"
insp_replacement = "idempotency_key = Column(String, nullable=True)\n    cryptographic_signature = Column(String, nullable=True)"
content = content.replace(insp_target, insp_replacement)

# Add cryptographic_signature to SafetyEvent
se_target = "idempotency_key = Column(String, nullable=True)"
se_replacement = "idempotency_key = Column(String, nullable=True)\n    cryptographic_signature = Column(String, nullable=True)"
content = content.replace(se_target, se_replacement)

with open(filepath, 'w') as f:
    f.write(content)

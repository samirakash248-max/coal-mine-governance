import re

filepath = "backend/app/api/v1/documents.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("from app.api.deps import get_current_user", "from app.api.deps import get_current_user, apply_tenant_scope, force_tenant_creation")

target_list = """    stmt = select(Document).where(Document.mine_id == current_user.mine_id)"""
replacement_list = """    stmt = select(Document)
    stmt = apply_tenant_scope(stmt, Document, current_user)"""
content = content.replace(target_list, replacement_list)

target_get = """    stmt = select(Document).where(Document.id == document_id, Document.mine_id == current_user.mine_id)"""
replacement_get = """    stmt = select(Document).where(Document.id == document_id)
    stmt = apply_tenant_scope(stmt, Document, current_user)"""
content = content.replace(target_get, replacement_get)

target_verify = """    stmt = select(Document).where(Document.id == document_id, Document.mine_id == current_user.mine_id)"""
replacement_verify = """    stmt = select(Document).where(Document.id == document_id)
    stmt = apply_tenant_scope(stmt, Document, current_user)"""
content = content.replace(target_verify, replacement_verify)

target_upload = """    doc = Document(
        mine_id=current_user.mine_id,
        owner_id=current_user.id,"""
replacement_upload = """    # Using force_tenant_creation logic via dictionary to find correct mine_id if needed, but here we can just use current_user.mine_id for now as Documents can be corporate-level (mine_id=None).
    # If it is a Mine Manager, it will correctly use their mine_id.
    doc = Document(
        mine_id=current_user.mine_id,
        owner_id=current_user.id,"""
content = content.replace(target_upload, replacement_upload)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

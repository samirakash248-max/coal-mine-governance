import re
import glob

filepath = "backend/app/models/field.py"
with open(filepath, 'r') as f:
    content = f.read()

target = "idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)"
replacement = "idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)\n    cryptographic_signature: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)"

content = content.replace(target, replacement)
with open(filepath, 'w') as f:
    f.write(content)

# Fix migration
migration_files = glob.glob("backend/alembic/versions/*_add_cryptographic_signatures.py")
if migration_files:
    mig_file = migration_files[0]
    with open(mig_file, 'r') as f:
        mig_content = f.read()
    
    mig_content = mig_content.replace("op.drop_table('spatial_ref_sys')", "pass")
    
    # We also need to add the new columns since they were missed in the previous autogenerate
    mig_content = mig_content.replace("def upgrade() -> None:", "def upgrade() -> None:\n    op.add_column('inspections', sa.Column('cryptographic_signature', sa.String(length=64), nullable=True))\n    op.add_column('safety_events', sa.Column('cryptographic_signature', sa.String(length=64), nullable=True))")
    
    with open(mig_file, 'w') as f:
        f.write(mig_content)

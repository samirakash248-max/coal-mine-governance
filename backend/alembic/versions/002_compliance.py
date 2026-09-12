"""Compliance models

Revision ID: 002_compliance
Revises: 001_initial
Create Date: 2026-09-10 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '002_compliance'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Modify Mine
    op.add_column('mines', sa.Column('mine_type', sa.String(length=100), nullable=True))
    op.add_column('mines', sa.Column('manager_id', sa.UUID(), nullable=True))
    op.add_column('mines', sa.Column('operational_metadata', JSONB(), nullable=True))
    op.create_foreign_key(None, 'mines', 'users', ['manager_id'], ['id'], ondelete='SET NULL')

    # Create compliance_requirements
    op.create_table('compliance_requirements',
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('frequency', sa.String(length=100), nullable=True),
        sa.Column('source_reference', sa.String(length=500), nullable=True),
        sa.Column('applicable_mine_id', sa.UUID(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['applicable_mine_id'], ['mines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create compliance_records
    op.create_table('compliance_records',
        sa.Column('requirement_id', sa.UUID(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('responsible_department_id', sa.UUID(), nullable=True),
        sa.Column('responsible_officer_id', sa.UUID(), nullable=True),
        sa.Column('submission_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['requirement_id'], ['compliance_requirements.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['responsible_department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['responsible_officer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create compliance_evidence
    op.create_table('compliance_evidence',
        sa.Column('record_id', sa.UUID(), nullable=False),
        sa.Column('storage_path', sa.String(length=1024), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['record_id'], ['compliance_records.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('compliance_evidence')
    op.drop_table('compliance_records')
    op.drop_table('compliance_requirements')
    op.drop_column('mines', 'operational_metadata')
    op.drop_column('mines', 'manager_id')
    op.drop_column('mines', 'mine_type')

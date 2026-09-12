"""Phase 11 Hardening Indexes

Revision ID: 010_hardening_indexes
Revises: 009_reports
Create Date: 2026-09-11 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '010_hardening_indexes'
down_revision: Union[str, None] = '009_reports'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Adding B-Tree indexes on high-query tenant boundary columns (mine_id)
    op.create_index('ix_safety_events_mine_id', 'safety_events', ['mine_id'])
    op.create_index('ix_corrective_actions_mine_id', 'corrective_actions', ['mine_id'])
    op.create_index('ix_inspections_mine_id', 'inspections', ['mine_id'])
    op.create_index('ix_compliance_records_mine_id', 'compliance_records', ['mine_id'])
    op.create_index('ix_documents_mine_id', 'documents', ['mine_id'])
    op.create_index('ix_reports_mine_id', 'reports', ['mine_id'])
    op.create_index('ix_environment_readings_mine_id', 'environment_readings', ['mine_id'])
    op.create_index('ix_production_records_mine_id', 'production_records', ['mine_id'])
    op.create_index('ix_grievances_mine_id', 'grievances', ['mine_id'])
    op.create_index('ix_audit_logs_mine_id', 'audit_logs', ['mine_id'])
    
    # Time-series indexes for faster analytics
    op.create_index('ix_safety_events_date', 'safety_events', ['date'])
    op.create_index('ix_production_records_date', 'production_records', ['date'])
    op.create_index('ix_reports_created_at', 'reports', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_reports_created_at', table_name='reports')
    op.drop_index('ix_production_records_date', table_name='production_records')
    op.drop_index('ix_safety_events_date', table_name='safety_events')
    
    op.drop_index('ix_audit_logs_mine_id', table_name='audit_logs')
    op.drop_index('ix_grievances_mine_id', table_name='grievances')
    op.drop_index('ix_production_records_mine_id', table_name='production_records')
    op.drop_index('ix_environment_readings_mine_id', table_name='environment_readings')
    op.drop_index('ix_reports_mine_id', table_name='reports')
    op.drop_index('ix_documents_mine_id', table_name='documents')
    op.drop_index('ix_compliance_records_mine_id', table_name='compliance_records')
    op.drop_index('ix_inspections_mine_id', table_name='inspections')
    op.drop_index('ix_corrective_actions_mine_id', table_name='corrective_actions')
    op.drop_index('ix_safety_events_mine_id', table_name='safety_events')

"""GIS and PWA Idempotency keys

Revision ID: 005_gis_pwa
Revises: 004_workflow
Create Date: 2026-09-10 12:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005_gis_pwa'
down_revision: Union[str, None] = '004_workflow'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add idempotency keys and map coords
    op.add_column('inspections', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.create_unique_constraint(None, 'inspections', ['idempotency_key'])
    
    op.add_column('safety_events', sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.add_column('safety_events', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('safety_events', sa.Column('longitude', sa.Float(), nullable=True))
    op.create_unique_constraint(None, 'safety_events', ['idempotency_key'])

def downgrade() -> None:
    op.drop_constraint(None, 'safety_events', type_='unique')
    op.drop_column('safety_events', 'longitude')
    op.drop_column('safety_events', 'latitude')
    op.drop_column('safety_events', 'idempotency_key')
    
    op.drop_constraint(None, 'inspections', type_='unique')
    op.drop_column('inspections', 'idempotency_key')

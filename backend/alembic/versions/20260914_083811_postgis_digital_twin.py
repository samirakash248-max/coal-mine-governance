"""postgis_digital_twin

Revision ID: 9b2d8c7f1a3e
Revises: 
Create Date: 2026-09-14 08:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = '9b2d8c7f1a3e'
down_revision: Union[str, None] = '010_hardening_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Safely enable postgis extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')

    # Add geometry columns safely
    op.add_column('mines', sa.Column('location_geom', Geometry(geometry_type='POINT', srid=4326, spatial_index=True), nullable=True))
    op.add_column('safety_events', sa.Column('location_geom', Geometry(geometry_type='POINT', srid=4326, spatial_index=True), nullable=True))
    op.add_column('inspections', sa.Column('location_geom', Geometry(geometry_type='POINT', srid=4326, spatial_index=True), nullable=True))

    # Migrate existing data safely
    op.execute("""
        UPDATE mines 
        SET location_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND latitude BETWEEN -90 AND 90 
        AND longitude BETWEEN -180 AND 180;
    """)
    op.execute("""
        UPDATE safety_events 
        SET location_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND latitude BETWEEN -90 AND 90 
        AND longitude BETWEEN -180 AND 180;
    """)
    op.execute("""
        UPDATE inspections 
        SET location_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE longitude IS NOT NULL AND latitude IS NOT NULL
        AND latitude BETWEEN -90 AND 90 
        AND longitude BETWEEN -180 AND 180;
    """)

def downgrade() -> None:
    op.drop_column('inspections', 'location_geom')
    op.drop_column('safety_events', 'location_geom')
    op.drop_column('mines', 'location_geom')
    # We do NOT drop the postgis extension as other things might depend on it now

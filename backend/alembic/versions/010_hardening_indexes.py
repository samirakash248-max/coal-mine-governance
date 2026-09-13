"""add hardening indexes

Revision ID: 010_hardening_indexes
Revises: 009_reports
Create Date: 2026-09-13
"""

from alembic import op


revision = "010_hardening_indexes"
down_revision = "009_reports"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_safety_events_mine_id",
        "safety_events",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_corrective_actions_mine_id",
        "corrective_actions",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_inspections_mine_id",
        "inspections",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_documents_mine_id",
        "documents",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_reports_mine_id",
        "reports",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_environment_readings_mine_id",
        "environment_readings",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_production_records_mine_id",
        "production_records",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_grievances_mine_id",
        "grievances",
        ["mine_id"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_safety_events_date",
        "safety_events",
        ["date"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_production_records_date",
        "production_records",
        ["date"],
        if_not_exists=True,
    )

    op.create_index(
        "ix_reports_created_at",
        "reports",
        ["created_at"],
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_index("ix_reports_created_at", table_name="reports")
    op.drop_index("ix_production_records_date", table_name="production_records")
    op.drop_index("ix_safety_events_date", table_name="safety_events")

    op.drop_index("ix_grievances_mine_id", table_name="grievances")
    op.drop_index("ix_production_records_mine_id", table_name="production_records")
    op.drop_index("ix_environment_readings_mine_id", table_name="environment_readings")
    op.drop_index("ix_reports_mine_id", table_name="reports")
    op.drop_index("ix_documents_mine_id", table_name="documents")
    op.drop_index("ix_inspections_mine_id", table_name="inspections")
    op.drop_index("ix_corrective_actions_mine_id", table_name="corrective_actions")
    op.drop_index("ix_safety_events_mine_id", table_name="safety_events")
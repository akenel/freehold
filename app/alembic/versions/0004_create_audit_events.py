"""create audit_events table

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("actor", sa.String(80), nullable=False, server_default="system"),
        sa.Column("action", sa.String(60), nullable=False, server_default=""),
        sa.Column("target", sa.String(200), nullable=False, server_default=""),
        sa.Column("detail", sa.JSON, nullable=True),
    )
    # The three axes we filter/sort the cockpit by: time, who, what.
    op.create_index("ix_audit_events_at", "audit_events", ["at"])
    op.create_index("ix_audit_events_actor", "audit_events", ["actor"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])


def downgrade() -> None:
    op.drop_index("ix_audit_events_action", table_name="audit_events")
    op.drop_index("ix_audit_events_actor", table_name="audit_events")
    op.drop_index("ix_audit_events_at", table_name="audit_events")
    op.drop_table("audit_events")

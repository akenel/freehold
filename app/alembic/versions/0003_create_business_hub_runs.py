"""create business_hub_runs table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_hub_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("source", sa.String(120), nullable=False, server_default=""),
        sa.Column("count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("report_key", sa.String(200), nullable=False, server_default=""),
        sa.Column("run_by", sa.String(80), nullable=False, server_default="anonymous"),
    )


def downgrade() -> None:
    op.drop_table("business_hub_runs")

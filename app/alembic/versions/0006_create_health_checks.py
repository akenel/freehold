"""create health_checks — one row per service, upserted on every probe

The Service Health Dashboard declared HealthCheck in app/models.py but shipped
without a migration, so on any real database the model existed and the table did
not. record_check() swallows exceptions on purpose (health recording must never
break the health check), which meant /status stayed green while persisting
nothing — machine-green, not human-green. This creates the table.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-09
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "health_checks",
        sa.Column("id", sa.Integer, primary_key=True),
        # One row per service, updated in place on each probe — not append-only,
        # so `service` is unique and record_check() can select-then-update on it.
        sa.Column("service", sa.String(60), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("detail", sa.Text, nullable=True),
    )
    op.create_index("ix_health_checks_service", "health_checks", ["service"])


def downgrade() -> None:
    op.drop_index("ix_health_checks_service", table_name="health_checks")
    op.drop_table("health_checks")

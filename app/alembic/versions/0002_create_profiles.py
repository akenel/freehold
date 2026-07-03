"""create profiles table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(80), nullable=False),
        sa.Column("display_name", sa.String(120), nullable=False, server_default=""),
        sa.Column("tagline", sa.String(160), nullable=False, server_default=""),
        sa.Column("bio", sa.Text, nullable=False, server_default=""),
        sa.Column("avatar_key", sa.String(120), nullable=True),
        sa.Column("banner_key", sa.String(120), nullable=True),
        sa.Column("links", sa.JSON, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_profiles_username", "profiles", ["username"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_profiles_username", "profiles")
    op.drop_table("profiles")

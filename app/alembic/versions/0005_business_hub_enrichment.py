"""add enrichment provenance to business_hub_runs

Which brain touched this run, under which prompt, how many rows it wrote, what
it cost, and how many it handed to a human. Nullable-with-defaults so existing
rows stay valid — a pre-AI run is honestly recorded as model "none".

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("business_hub_runs", sa.Column(
        "model", sa.String(80), nullable=False, server_default="none"))
    op.add_column("business_hub_runs", sa.Column(
        "prompt_version", sa.String(40), nullable=False, server_default=""))
    op.add_column("business_hub_runs", sa.Column(
        "enriched_count", sa.Integer, nullable=False, server_default="0"))
    op.add_column("business_hub_runs", sa.Column(
        "tokens", sa.Integer, nullable=False, server_default="0"))
    op.add_column("business_hub_runs", sa.Column(
        "review_count", sa.Integer, nullable=False, server_default="0"))


def downgrade() -> None:
    for col in ("review_count", "tokens", "enriched_count", "prompt_version", "model"):
        op.drop_column("business_hub_runs", col)

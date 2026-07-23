"""Freehold — data models (SQLAlchemy 2.0).

Phase 4 introduces the first real table: tickets. A ticket is a piece of
feedback / a bug / an idea that moves open -> in_progress -> closed. Closing
demands a *resolution* — so the closed pile becomes a searchable record of
"what was wrong and why we did what we did." Tickets are the knowledge base.
"""
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Profile(Base):
    """One per user (keyed by Keycloak username). The juicy public page:
    banner + avatar + bio + a set of links the person chooses themselves."""
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    tagline: Mapped[str] = mapped_column(String(160), default="")
    bio: Mapped[str] = mapped_column(Text, default="")
    avatar_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    banner_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    links: Mapped[list | None] = mapped_column(JSON, nullable=True)  # [{"label":..,"url":..}]
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BusinessHubRun(Base):
    """One row per integration sync — the 'record' step of pull → transform →
    store → record. Proves the job ran: who ran it, how many records moved, and
    the key of the report we stashed in MinIO. Swap the source system and this
    same table logs a real client integration."""
    __tablename__ = "business_hub_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    source: Mapped[str] = mapped_column(String(120), default="")   # the system we pulled from
    count: Mapped[int] = mapped_column(default=0)                    # records moved
    report_key: Mapped[str] = mapped_column(String(200), default="") # object key in MinIO
    run_by: Mapped[str] = mapped_column(String(80), default="anonymous")


class AuditEvent(Base):
    """Append-only trail of who did what, when — logins, Business Hub syncs, ticket
    moves, admin actions. Cousin of BusinessHubRun, generalized: one honest row per
    meaningful action. NEVER updated, NEVER deleted — that's the whole point of an
    audit log. Written via audit.record(), which swallows its own errors so logging
    can never roll back the real action it's recording."""
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    actor: Mapped[str] = mapped_column(String(80), default="system", index=True)  # who ('system'/'anonymous' if none)
    action: Mapped[str] = mapped_column(String(60), default="", index=True)         # dotted verb: user.login, ticket.close…
    target: Mapped[str] = mapped_column(String(200), default="")                    # human 'what': "Ticket #12", source name
    detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)                # structured extras {count, status, …}


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), default="feedback")   # feedback | bug | idea
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)  # open|in_progress|closed
    created_by: Mapped[str] = mapped_column(String(80), default="anonymous")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # captured on close — the "why" that makes the archive worth mining
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

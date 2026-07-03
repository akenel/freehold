"""Freehold — the ticket service (all DB access for the feedback/QA loop)."""
from datetime import datetime, timezone

from sqlalchemy import func, select

from db import async_session
from models import Ticket

OPEN_STATES = ("open", "in_progress")


async def create_ticket(kind: str, title: str, body: str, created_by: str) -> None:
    async with async_session() as s:
        s.add(Ticket(kind=kind, title=title, body=body, created_by=created_by))
        await s.commit()


async def list_tickets(status: str | None = None) -> list[Ticket]:
    async with async_session() as s:
        query = select(Ticket).order_by(Ticket.created_at.desc())
        if status:
            query = query.where(Ticket.status == status)
        return list((await s.execute(query)).scalars().all())


async def counts() -> dict[str, int]:
    async with async_session() as s:
        rows = (await s.execute(
            select(Ticket.status, func.count()).group_by(Ticket.status)
        )).all()
        return {status: n for status, n in rows}


async def set_status(ticket_id: int, status: str) -> None:
    async with async_session() as s:
        ticket = await s.get(Ticket, ticket_id)
        if ticket:
            ticket.status = status
            await s.commit()


async def close_ticket(ticket_id: int, resolution: str, by: str) -> None:
    """Close a ticket WITH its resolution — the discipline that builds the archive."""
    async with async_session() as s:
        ticket = await s.get(Ticket, ticket_id)
        if ticket:
            ticket.status = "closed"
            ticket.resolution = resolution
            ticket.resolved_by = by
            ticket.resolved_at = datetime.now(timezone.utc)
            await s.commit()

"""Freehold — the audit log service.

Append-only "who did what, when." One honest row per meaningful action:
a login, a Business Hub sync, a ticket move, an admin action. The selling
point is provable, self-hosted action history — their data, their server,
nothing to subpoena a SaaS vendor for.

Two rules, both borrowed from a real POS audit trail (helixPOS/banco):

  1. NEVER let auditing break the thing it audits. record() swallows every
     error — worst case we lose one audit row, never the real sale/login/edit.
  2. Append-only. There is no update() and no delete() here, on purpose.

Written by app code at the event site (a login has no table write, so a DB
trigger can't see it) — semantic events, not raw row diffs.
"""
from sqlalchemy import distinct, select

from db import async_session
from models import AuditEvent

# The vocabulary of actions, so the codebase agrees on the strings. The admin
# page turns these into human labels + emoji; unknown ones still render fine.
LOGIN = "user.login"
LOGOUT = "user.logout"
SYNC = "business_hub.sync"
TICKET_NEW = "ticket.create"
TICKET_STATUS = "ticket.status"
TICKET_CLOSE = "ticket.close"


async def record(actor: str | None, action: str, target: str = "", **detail) -> None:
    """Write one append-only audit row. Fire-and-forget: any failure is swallowed
    so a logging hiccup can NEVER roll back or 500 the real action being recorded."""
    try:
        async with async_session() as s:
            s.add(AuditEvent(
                actor=(actor or "anonymous"),
                action=action,
                target=target[:200],
                detail=(detail or None),
            ))
            await s.commit()
    except Exception:  # noqa: BLE001 — auditing must never break the real action
        pass


async def recent(limit: int = 100, action: str = "", actor: str = "") -> list[AuditEvent]:
    """The feed for the cockpit, newest first, with optional who/what filters."""
    async with async_session() as s:
        q = select(AuditEvent).order_by(AuditEvent.id.desc())
        if action:
            q = q.where(AuditEvent.action == action)
        if actor:
            q = q.where(AuditEvent.actor == actor)
        return list((await s.execute(q.limit(limit))).scalars())


async def facets() -> dict:
    """Distinct actions + actors present in the log — powers the filter chips."""
    async with async_session() as s:
        actions = list((await s.execute(
            select(distinct(AuditEvent.action)).order_by(AuditEvent.action)
        )).scalars())
        actors = list((await s.execute(
            select(distinct(AuditEvent.actor)).order_by(AuditEvent.actor)
        )).scalars())
        return {"actions": [a for a in actions if a], "actors": [a for a in actors if a]}

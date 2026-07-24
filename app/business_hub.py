"""Freehold — Business Hub pack (the integration service).

The billable shape, wearing the house colours:
**pull → transform → enrich → store → record.**

Pull from an external system's API, reshape the data, run it past the enrichment
step (rules first, your chosen brain second — see enrich.py), stash a report in
MinIO, and log the run in Postgres. Swap the one source URL for a real client
system and this same pack becomes a paid integration job — the demo IS the product.

The enrich step is the part nobody else sells: every value it writes carries
provenance (which rule or which model, how confident, when), the original is
always kept beside it, and anything the model wasn't sure about is gated to a
human instead of being written into master data. That's what makes it safe to
point at a real customer's CRM or product catalogue.

Storage note: the report lands in its own MinIO bucket and is served back through
an AUTHENTICATED route, /business-hub/report/<key>. It used to go out via Caddy's
/media/* handler, which proxies to MinIO with no login at all — and the key was
`{filename}-{timestamp}.json`, i.e. guessable by anyone who knew the filename.
A report contains every enriched record: names, emails, phone numbers. Two fixes,
both in this file: the key is now 128 random bits, and report_url() points at a
route that checks the session. Caddy's /media/* matcher was narrowed to the
images bucket at the same time, so this bucket is no longer reachable at all
from the internet.
"""
import io
import json
import os
import secrets
from datetime import datetime, timezone

import httpx
from minio import Minio
from sqlalchemy import select

import audit
import enrich
import inbound
from db import async_session
from models import BusinessHubRun

# The stand-in "client CRM". Swap this URL for a real system and the demo is a job.
SOURCE_NAME = "jsonplaceholder (demo CRM)"
SOURCE_URL = "https://jsonplaceholder.typicode.com/users"

_BUCKET = "business-hub"
_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
_ACCESS = os.getenv("MINIO_ROOT_USER", "freehold")
_SECRET = os.getenv("MINIO_ROOT_PASSWORD", "change_me_dev_only")

_client = Minio(_ENDPOINT, access_key=_ACCESS, secret_key=_SECRET, secure=False)
_ready = False

def _ensure_bucket() -> None:
    """Create the reports bucket once (lazily) — and make sure it is PRIVATE.

    This bucket used to carry an anonymous `s3:GetObject` allow, because the hub
    page linked reports at /media/business-hub/<key>. A report is every enriched
    record in a run: names, emails, phone numbers. It should never have been
    world-readable, so the policy is actively removed here rather than merely
    not set — a box that already ran the old code has the old policy on disk, and
    "we stopped adding it" would leave those installs open forever.

    load_report() and the new /business-hub/report/<key> route both read through
    the authenticated client, so nothing needs the public policy at all."""
    global _ready
    if _ready:
        return
    if not _client.bucket_exists(_BUCKET):
        _client.make_bucket(_BUCKET)
    try:
        _client.delete_bucket_policy(_BUCKET)
    except Exception:  # noqa: BLE001 — no policy to remove is the desired state
        pass
    _ready = True


def report_url(key: str | None) -> str:
    """Where to read a stored report. Login required — see routers/business_hub.py.

    Deliberately NOT /media/business-hub/<key> any more: that path is proxied
    straight to MinIO by Caddy with no authentication on every vhost, which made
    every customer record in every report a public URL away from anyone who could
    guess a filename and a timestamp."""
    return f"/business-hub/report/{key}" if key else ""


def report_key() -> str:
    """128 unguessable bits. The old `{stem}-{%Y%m%dT%H%M%S}.json` scheme leaked
    the source filename and could be swept for a whole day in ~86k requests; the
    API channel's was worse — fully determined by the second the job ran."""
    return f"{secrets.token_hex(16)}.json"


async def run_sync(run_by: str, model: str = enrich.DEFAULT_MODEL) -> BusinessHubRun:
    """The whole job, five honest steps. Returns the recorded run."""
    # 1. PULL from the external system's API (stand-in for a client's CRM).
    async with httpx.AsyncClient(timeout=30) as c:
        source = (await c.get(SOURCE_URL)).json()

    # 2. TRANSFORM into the shape we want. We carry the *messy* fields through
    #    (raw phone, city, slogan) precisely because they're what enrichment
    #    feeds on — a transform that drops them has thrown away the raw material.
    contacts = [
        {
            "name": u["name"],
            "email": u["email"],
            "company": u["company"]["name"],
            "phone": u.get("phone", ""),
            "city": u.get("address", {}).get("city", ""),
            "slogan": u["company"].get("catchPhrase", ""),
            "keywords": u["company"].get("bs", ""),
        }
        for u in source
    ]

    # 3. ENRICH — rules first, chosen brain second, provenance on everything.
    records, stats = await enrich.enrich(contacts, model=model, profile="contacts")

    # 4. STORE the report in self-hosted MinIO (not a paid cloud bucket). The
    #    report is self-describing: the meta block says who enriched it and how,
    #    so the JSON stands on its own even if it leaves this system.
    _ensure_bucket()
    key = report_key()
    report = {
        "meta": {
            "source": SOURCE_NAME,
            "run_by": run_by,
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": len(records),
            **stats,
        },
        "records": records,
    }
    body = json.dumps(report, indent=2).encode()
    _client.put_object(
        _BUCKET, key, io.BytesIO(body), length=len(body), content_type="application/json"
    )

    # 5. RECORD the run in Postgres (their data, their server).
    async with async_session() as s:
        run = BusinessHubRun(
            source=SOURCE_NAME, count=len(records), report_key=key, run_by=run_by,
            model=stats["model"], prompt_version=stats["prompt_version"],
            enriched_count=stats["enriched_count"], tokens=stats["tokens"],
            review_count=stats["review_count"],
        )
        s.add(run)
        await s.commit()
        await s.refresh(run)

    # 6. AUDIT the action (best-effort; never blocks the run it records).
    await audit.record(
        run_by, audit.SYNC, SOURCE_NAME, count=len(records), report_key=key,
        model=stats["model"], prompt_version=stats["prompt_version"],
        enriched=stats["enriched_count"], tokens=stats["tokens"],
        review=stats["review_count"],
    )
    return run


async def run_import(blob: bytes, filename: str, run_by: str,
                     model: str = enrich.DEFAULT_MODEL,
                     profile: str = "call_list", sheet: int = 0) -> BusinessHubRun:
    """The same job, different inbound channel: a spreadsheet instead of an API.

    This is the point of the whole design. read_xlsx() produces the same list of
    dicts an API pull produces, so from step 3 onward *nothing changes* — same
    enrichment, same provenance, same gate, same report, same audit row. An
    integration's inbound channel is an adapter; the mapping is the product.
    """
    # 1. PULL — from a file a human dragged in, rather than from an API.
    fields, records = inbound.read_xlsx(blob, sheet=sheet)

    # 2. TRANSFORM — none needed; the header row already named the columns.
    # 3. ENRICH — rules first, chosen brain second, provenance on everything.
    enriched, stats = await enrich.enrich(records, model=model, profile=profile)

    # 4. STORE the report in self-hosted MinIO.
    # The human name for the run lives in meta.source and in the run row; the
    # object key carries no information at all, which is the point.
    _ensure_bucket()
    key = report_key()
    report = {
        "meta": {
            "source": filename, "run_by": run_by, "channel": "spreadsheet",
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": len(enriched), "columns": fields, **stats,
        },
        "records": enriched,
    }
    body = json.dumps(report, indent=2, ensure_ascii=False).encode()
    _client.put_object(
        _BUCKET, key, io.BytesIO(body), length=len(body), content_type="application/json"
    )

    # 5. RECORD + 6. AUDIT — identical to the API channel.
    source = f"{filename} (spreadsheet)"
    async with async_session() as s:
        run = BusinessHubRun(
            source=source[:120], count=len(enriched), report_key=key, run_by=run_by,
            model=stats["model"], prompt_version=stats["prompt_version"],
            enriched_count=stats["enriched_count"], tokens=stats["tokens"],
            review_count=stats["review_count"],
        )
        s.add(run)
        await s.commit()
        await s.refresh(run)

    await audit.record(
        run_by, audit.SYNC, source, count=len(enriched), report_key=key,
        channel="spreadsheet", profile=stats["profile"], model=stats["model"],
        prompt_version=stats["prompt_version"], enriched=stats["enriched_count"],
        tokens=stats["tokens"], review=stats["review_count"],
    )
    return run


def load_report(key: str) -> dict:
    """Read a stored report back out of MinIO — powers the before/after pane.

    Best-effort: a missing or unreadable object just means the pane doesn't
    render. Never let a display nicety take down the page that shows the log."""
    try:
        resp = _client.get_object(_BUCKET, key)
        try:
            return json.loads(resp.read())
        finally:
            resp.close()
            resp.release_conn()
    except Exception:  # noqa: BLE001 — the run log matters more than the preview
        return {}


async def recent_runs(limit: int = 20) -> list[BusinessHubRun]:
    async with async_session() as s:
        return list((await s.execute(
            select(BusinessHubRun).order_by(BusinessHubRun.id.desc()).limit(limit)
        )).scalars())

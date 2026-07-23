"""Freehold — Business Hub pack (the integration service).

The billable shape, wearing the house colours: **pull → transform → store → record.**
Pull from an external system's API, reshape the data, stash a report in MinIO, and
log the run in Postgres. Swap the one source URL for a real client system and this
same pack becomes a paid integration job — the demo IS the product.

Storage note: the report lands in its own public-read MinIO bucket, so Caddy's
existing /media/* route serves it back at /media/business-hub/<key> — no new route.
"""
import io
import json
import os
from datetime import datetime, timezone

import httpx
from minio import Minio
from sqlalchemy import select

import audit
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

_PUBLIC_READ = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"AWS": ["*"]},
        "Action": ["s3:GetObject"],
        "Resource": [f"arn:aws:s3:::{_BUCKET}/*"],
    }],
}


def _ensure_bucket() -> None:
    """Create the reports bucket + set public-read once (lazily, on first run)."""
    global _ready
    if _ready:
        return
    if not _client.bucket_exists(_BUCKET):
        _client.make_bucket(_BUCKET)
    _client.set_bucket_policy(_BUCKET, json.dumps(_PUBLIC_READ))
    _ready = True


def report_url(key: str | None) -> str:
    """Public URL for a stored report, served via Caddy's /media/* route."""
    return f"/media/{_BUCKET}/{key}" if key else ""


async def run_sync(run_by: str) -> BusinessHubRun:
    """The whole job, four honest steps. Returns the recorded run."""
    # 1. PULL from the external system's API (stand-in for a client's CRM).
    async with httpx.AsyncClient(timeout=30) as c:
        source = (await c.get(SOURCE_URL)).json()

    # 2. TRANSFORM into the shape we want.
    contacts = [
        {"name": u["name"], "email": u["email"], "company": u["company"]["name"]}
        for u in source
    ]

    # 3. STORE the report in self-hosted MinIO (not a paid cloud bucket).
    _ensure_bucket()
    key = f"contacts-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}.json"
    body = json.dumps(contacts, indent=2).encode()
    _client.put_object(
        _BUCKET, key, io.BytesIO(body), length=len(body), content_type="application/json"
    )

    # 4. RECORD the run in Postgres (their data, their server).
    async with async_session() as s:
        run = BusinessHubRun(
            source=SOURCE_NAME, count=len(contacts), report_key=key, run_by=run_by
        )
        s.add(run)
        await s.commit()
        await s.refresh(run)

    # 5. AUDIT the action (best-effort; never blocks the run it records).
    await audit.record(
        run_by, audit.SYNC, SOURCE_NAME, count=len(contacts), report_key=key
    )
    return run


async def recent_runs(limit: int = 20) -> list[BusinessHubRun]:
    async with async_session() as s:
        return list((await s.execute(
            select(BusinessHubRun).order_by(BusinessHubRun.id.desc()).limit(limit)
        )).scalars())

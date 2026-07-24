"""Freehold — the vault: the bucket with no policy on it.

Everything else in this app that touches MinIO (media.py, business_hub.py) calls
set_bucket_policy() with an anonymous `s3:GetObject` allow, because avatars are
meant to be served by a plain URL. This bucket is the opposite, and the
difference is the entire reason the list feature is safe to point at a customer's
data.

What lands here is the **original uploaded spreadsheet** — not the columns we
parsed, the whole workbook. Every row the pipeline never read, the hidden sheet
somebody forgot, the pasted salary column, the comments, the document author's
name, and the tab called "old prices DO NOT USE". A report leaks the fields we
mapped; the original leaks everything anyone ever typed into that file.

Three things keep it private, and all three are load-bearing:

  1. **No bucket policy.** MinIO default-denies anonymous access. `_ensure()`
     creates the bucket and stops. See the shouting comment below.
  2. **Unguessable keys.** secrets.token_hex(16) — 128 bits, never derived from
     the filename. business_hub's old `{stem}-{timestamp}.json` keys were
     guessable in about 86k requests if you knew the filename, and the API
     channel's were fully determined by the second the job ran.
  3. **Authenticated reads only.** Objects come back through a login-gated route
     that streams them with this client's credentials — never through Caddy's
     /media/* handler, which proxies to MinIO with no auth at all and which this
     change narrows to the images bucket.

Known limit, stated here and on the page rather than hidden: any logged-in
Freehold user who learns a key can fetch that object. Freehold is a single-tenant
box for one company, so "logged in" and "allowed" are the same set today.
Per-object ownership needs an index object and read-modify-write races we are not
buying in v1. There is also no TTL and no scan; delete() exists so the erasure
story has something to call when we write it.
"""
import io
import json
import os
import re
import secrets

from minio import Minio

BUCKET = os.getenv("VAULT_BUCKET", "freehold-vault")
_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
_ACCESS = os.getenv("MINIO_ROOT_USER", "freehold")
_SECRET = os.getenv("MINIO_ROOT_PASSWORD", "change_me_dev_only")

_client = Minio(_ENDPOINT, access_key=_ACCESS, secret_key=_SECRET, secure=False)
_ready = False

SRC = "src/"           # the original .xlsx, immutable
DRAFTS = "drafts/"     # an unapproved mapping, deletable
RECIPES = "recipes/"   # the approved recipe + its whole version chain

# Keys are matched against these before anything is read. A regex allowlist, not
# a "../" strip — a blocklist of bad shapes is a game you lose eventually.
SRC_KEY = re.compile(r"^src/[0-9a-f]{32}\.xlsx$")
DRAFT_KEY = re.compile(r"^drafts/[0-9a-f]{32}\.json$")


def _ensure() -> None:
    """Create the bucket once, lazily. And then do nothing else."""
    global _ready
    if _ready:
        return
    if not _client.bucket_exists(BUCKET):
        _client.make_bucket(BUCKET)
    # ⚠️ DO NOT ADD set_bucket_policy HERE. This bucket holds customers' raw
    # spreadsheets. Caddy's /media/* handler proxies whatever bucket it is asked
    # for; the ONLY thing keeping this private is the absence of a policy.
    # One line here = every uploaded file on the public internet, forever, at a
    # URL with no login and no expiry. There is no second safety net.
    _ready = True


def new_key(prefix: str, ext: str) -> str:
    """128 unguessable bits. Never the filename — the filename is the guess."""
    return f"{prefix}{secrets.token_hex(16)}.{ext}"


def put(blob: bytes, key: str, content_type: str = "application/octet-stream") -> str:
    _ensure()
    _client.put_object(BUCKET, key, io.BytesIO(blob), length=len(blob),
                       content_type=content_type)
    return key


def put_json(obj, key: str) -> str:
    return put(json.dumps(obj, indent=2, ensure_ascii=False).encode(), key,
               "application/json")


def get(key: str) -> bytes:
    _ensure()
    resp = _client.get_object(BUCKET, key)
    try:
        return resp.read()
    finally:
        resp.close()
        resp.release_conn()


def get_json(key: str):
    """Read a JSON object back. Returns None when it isn't there or isn't readable —
    a missing draft is a normal thing (somebody discarded it), not an exception."""
    try:
        return json.loads(get(key))
    except Exception:  # noqa: BLE001 — a gone object is an answer, not a crash
        return None


def stream(key: str):
    """The urllib3 response, for streaming a download straight to the browser.
    Caller must close it — routers/lists.py does that in the generator's finally."""
    _ensure()
    return _client.get_object(BUCKET, key)


def exists(key: str) -> bool:
    try:
        _ensure()
        _client.stat_object(BUCKET, key)
        return True
    except Exception:  # noqa: BLE001
        return False


def list_prefix(prefix: str) -> list[str]:
    try:
        _ensure()
        return [o.object_name for o in _client.list_objects(BUCKET, prefix=prefix)]
    except Exception:  # noqa: BLE001 — an empty or unreachable vault reads as empty
        return []           # the index page renders; it just has nothing to show


def delete(key: str) -> None:
    """Used for discarding a draft today; the erasure story will use it tomorrow."""
    try:
        _ensure()
        _client.remove_object(BUCKET, key)
    except Exception:  # noqa: BLE001
        pass

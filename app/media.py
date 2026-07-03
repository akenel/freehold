"""Freehold — object storage (MinIO / S3-compatible).

Uploaded images (avatars, banners) live in MinIO, not on the app's disk — so the
app stays stateless and you can scale or move it freely. Public read is served
back through Caddy at /media/<bucket>/<key>, so the browser gets a plain URL.
"""
import io
import json
import os
import secrets

from minio import Minio

ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
ACCESS = os.getenv("MINIO_ROOT_USER", "freehold")
SECRET = os.getenv("MINIO_ROOT_PASSWORD", "change_me_dev_only")
BUCKET = os.getenv("MINIO_BUCKET", "freehold")

_client = Minio(ENDPOINT, access_key=ACCESS, secret_key=SECRET, secure=False)
_ready = False

EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif"}

_PUBLIC_READ = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"AWS": ["*"]},
        "Action": ["s3:GetObject"],
        "Resource": [f"arn:aws:s3:::{BUCKET}/*"],
    }],
}


def _ensure() -> None:
    """Create the bucket + set public-read once (lazily, on first upload)."""
    global _ready
    if _ready:
        return
    if not _client.bucket_exists(BUCKET):
        _client.make_bucket(BUCKET)
    _client.set_bucket_policy(BUCKET, json.dumps(_PUBLIC_READ))
    _ready = True


def is_image(content_type: str) -> bool:
    return content_type in EXT


def save_image(data: bytes, content_type: str) -> str:
    """Store bytes, return the object key. Caller keeps the key; render via url()."""
    _ensure()
    key = f"{secrets.token_hex(16)}.{EXT.get(content_type, 'bin')}"
    _client.put_object(BUCKET, key, io.BytesIO(data), length=len(data), content_type=content_type)
    return key


def url(key: str | None) -> str:
    return f"/media/{BUCKET}/{key}" if key else ""

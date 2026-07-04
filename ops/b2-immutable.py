#!/usr/bin/env python3
"""Freehold — turn on B2 Object-Lock retention + lifecycle for the backup bucket.

Makes every uploaded backup **immutable** for B2_LOCK_DAYS (governance mode — can't
be overwritten or deleted during the window, so ransomware/an fat-fingered `delete`
can't erase your recovery point), and a lifecycle rule auto-deletes after
B2_KEEP_DAYS so the bucket doesn't grow forever (cleanup happens B2-side, so the
backup key never needs delete rights). Reads B2 creds from .env. Idempotent.

    python3 ops/b2-immutable.py

Governance mode is reversible/adjustable. For attacker-proof immutability, ALSO use a
write-only B2 key (no deleteFiles / no bypassGovernance) — see docs/HARDENING.md.
"""
import base64
import json
import sys
import urllib.error
import urllib.request

from _common import load_env

AUTH_URL = "https://api.backblazeb2.com/b2api/v2/b2_authorize_account"


def _post(url, token, data):
    req = urllib.request.Request(
        url, data=json.dumps(data).encode(),
        headers={"Authorization": token, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def main() -> int:
    env = load_env()
    kid, app_key = env.get("B2_KEY_ID", "").strip(), env.get("B2_APP_KEY", "").strip()
    bucket = env.get("B2_BUCKET", "").strip()
    lock_days = int(env.get("B2_LOCK_DAYS", "14") or 14)
    keep_days = int(env.get("B2_KEEP_DAYS", "30") or 30)
    # governance = a bypass-capable key can still delete; compliance = NOBODY can delete
    # a locked object until it expires (truly ransomware-proof, but irreversible).
    lock_mode = (env.get("B2_LOCK_MODE", "governance").strip().lower() or "governance")
    if lock_mode not in ("governance", "compliance"):
        print(f"ERROR: B2_LOCK_MODE must be governance or compliance (got '{lock_mode}')"); return 1
    if not (kid and app_key and bucket):
        print("ERROR: B2_KEY_ID / B2_APP_KEY / B2_BUCKET must be set in .env"); return 1
    if keep_days <= lock_days:
        print(f"ERROR: B2_KEEP_DAYS ({keep_days}) must exceed B2_LOCK_DAYS ({lock_days})"); return 1

    # 1) authorize
    basic = base64.b64encode(f"{kid}:{app_key}".encode()).decode()
    req = urllib.request.Request(AUTH_URL, headers={"Authorization": f"Basic {basic}"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            a = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print("ERROR: B2 authorize failed —", e.read().decode()[:200]); return 1
    api_url, account_id = a["apiUrl"], a["accountId"]
    bucket_id = (a.get("allowed") or {}).get("bucketId")
    if not bucket_id:  # key not bucket-scoped — look it up
        lb = _post(f"{api_url}/b2api/v2/b2_list_buckets", a["authorizationToken"],
                   {"accountId": account_id, "bucketName": bucket})
        bucket_id = lb["buckets"][0]["bucketId"]

    # 2) set default retention + lifecycle in one update
    try:
        res = _post(f"{api_url}/b2api/v2/b2_update_bucket", a["authorizationToken"], {
            "accountId": account_id, "bucketId": bucket_id,
            "defaultRetention": {"mode": lock_mode,
                                 "period": {"duration": lock_days, "unit": "days"}},
            "lifecycleRules": [{"fileNamePrefix": "",
                                "daysFromUploadingToHiding": keep_days,
                                "daysFromHidingToDeleting": 1}],
        })
    except urllib.error.HTTPError as e:
        print("ERROR: b2_update_bucket failed —", e.read().decode()[:300]); return 1

    # Read back the applied retention from the response (nested under fileLockConfiguration).
    dr = (((res.get("fileLockConfiguration") or {}).get("value") or {}).get("defaultRetention") or {})
    mode, period = dr.get("mode"), dr.get("period") or {}
    if mode != lock_mode:
        print(f"⚠️  retention not applied as '{lock_mode}' (got '{mode}') — is Object Lock enabled?"); return 1
    print(f"✅ B2 '{bucket}': backups IMMUTABLE for {period.get('duration')} {period.get('unit')} "
          f"({mode}), auto-deleted ~{keep_days}d after upload (lifecycle).")
    print("   Cleanup is B2-side now — switch the backup key to write-only for full ransomware-proofing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

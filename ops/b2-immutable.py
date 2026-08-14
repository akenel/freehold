#!/usr/bin/env python3
"""Freehold — turn on B2 Object-Lock retention + lifecycle for the backup bucket.

Makes every uploaded backup **immutable** for B2_LOCK_DAYS (governance mode — can't
be overwritten or deleted during the window, so ransomware/an fat-fingered `delete`
can't erase your recovery point), and a lifecycle rule auto-deletes after
B2_KEEP_DAYS so the bucket doesn't grow forever (cleanup happens B2-side, so the
backup key never needs delete rights). Reads B2 creds from .env. Idempotent.

    python3 ops/b2-immutable.py

Governance mode is reversible/adjustable. For attacker-proof immutability, ALSO use a
write-only B2 key (no deleteFiles / no bypassGovernance) — see docs/private/HARDENING.md.

⚠️ RUNNING THIS ON THE BOX NOW RETURNS 401. THAT IS CORRECT — DO NOT "FIX" IT.
Verified 2026-08-14: `ssh wolfhold` → this script → `b2_update_bucket failed 401
unauthorized`. Authorize succeeds; only the bucket-admin call is refused, because the
box's key is the restricted backup key and lacks `writeBuckets`. That is the whole
point: **an attacker who owns the box cannot weaken Object Lock or the lifecycle rule.**
The 401 is the hardening working, demonstrated.

So this script is "run once" (see .env.example) in a stronger sense than it reads — it
is run once, from somewhere holding a B2 key with `writeBuckets`, BEFORE the box is
switched to the restricted key. After that switch it is deliberately un-runnable there.
To genuinely change bucket policy, run it from the laptop with a master/admin key.

Don't confuse this 401 with the 2026-08-10 one in WORKLIST's "next session" item 6.
That was `backup-volumes.py --cold` failing on a *write* capability and was fixed. This
is a *bucket-admin* capability and is refused on purpose. Same status code, opposite
meaning — check which API call failed before concluding anything.
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

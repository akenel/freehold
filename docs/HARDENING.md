# Freehold — hardening plan

The honest design review, turned into a checklist we knock off one by one. Ranked
worst-first. Owner: 🐯 = Claude can do it solo (repo + SSH), 🐺 = needs Angelo (a
decision, a console, or a cost), 🤝 = both.

---

## ✅ Tier 0 — done
- [x] **Off-box backups** — encrypted, restore-verified dumps ship to Backblaze B2
      on every prod deploy; round-trip proven. *(was the #1 gap: box death = data death)*

## 🟢 Tier 1 — quick wins
- [x] **1. Immutability (90% — accepted)** — governance 14d Object-Lock retention + 30d lifecycle
      cleanup (ops/b2-immutable.py, B2_LOCK_MODE); backups un-deletable 14d, backup.py
      upload-only (--no-check-dest, write-only-key-ready). PARKED until real user data — attacker-proof
      (🐺, needs the B2 MASTER key — app keys can't): either flip to **compliance** mode
      (no key incl. master can delete a locked object) OR `b2 create-key ...
      writeFiles,listBuckets` for a genuinely delete-less box key. B2's web-UI "Write
      Only" is NOT enough (it keeps deleteFiles+bypassGovernance).
      but no retention, and the key can delete → off-box but not ransomware-proof.
      Fix: a **write-only** B2 key + **default retention** (e.g. 14-day compliance) +
      a lifecycle rule for cleanup. *You: 2 clicks in the B2 console. Me: wire it.*
- [x] **2. `make` on the box** — done (GNU Make 4.4.1 installed).
- [x] **3. Client-secret coupling killed** — `.env` is now the single source;
      `make apply` (`prod-apply.py`) sets the client secret on the running Keycloak,
      and a **production `promote` auto-runs it** — you can't deploy prod with drifted
      auth anymore.
- [x] **4. `ops/` consolidated** — removed `set-domain.py` (dead), `set-smtp.py` +
      `set-idp.py` (folded into `make apply`, the ONE config path). `secrets.py` now
      just decrypts. Deploy tools split by role: `deploy` (single-env) vs `promote`
      (multi-env ladder). 10 scripts → 7.

## 🟡 Tier 2 — the real safety net
- [x] **5. Test coverage (14→25)** — auth-helper units + RBAC gates added, run in the deploy gate. Deeper integration (OIDC
      login flow, RBAC gating (admin-only routes), profile + ticket CRUD, and an
      `ops/` smoke. Then the CI gate is a net, not a speed bump.
- [ ] **6. Observability** — 🤝 — nothing watches it live. Add **uptime + alerts**
      (self-host Uptime Kuma, $0, I deploy it) and **error tracking** (self-host
      GlitchTip, or hosted Sentry free tier). *You: pick self-host vs hosted.*

## 🟠 Tier 3 — structural / your call
- [ ] **7. Feature triage** — 🐺→🐯 — robot / DuckDNS / money / i18n: which are core
      vs demo? You decide what stays; I prune the grab-bag so "what you get" is honest.
- [x] **8. `main.py` broke up** — 516 → 29 lines. deps.py (config + templates + guards)
      + routers/{base,door,loop,profile,extras,robot_panel}.py. Route surface proven
      identical (before/after diff empty); 25 tests green.
- [ ] **9. True env isolation** — 🐺 — sandbox/staging/prod share one Postgres +
      Keycloak + box (a shared SPOF). Real isolation = separate boxes. *Cost decision:
      keep one-box-pragmatic, or pay for 1–2 more small VPS.*

---

## What only 🐺 can do (the unblock list)
1. **Decide the observability flavor** — self-hosted (free, one more container on the
   box) or hosted (free tier, needs a signup). → unblocks #6.
2. **Two clicks in the B2 console** — a write-only key + turn on default retention.
   → unblocks #1 (I'll walk you through it).
3. **Triage the features** — I'll hand you the list; you mark keep/cut. → unblocks #7.
4. **The multi-box call** — willing to pay ~$5–10/mo more for real isolation, or stay
   one-box for now? → unblocks #9.
5. **Human-in-the-loop verify** — after each change, click through in a browser (the
   one e2e a script can't do). You've been great at this.

Everything else (3, 4, 5, 8, and my half of 1, 2, 6) I do solo and you review.

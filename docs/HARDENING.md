# Freehold — hardening plan

The honest design review, turned into a checklist we knock off one by one. Ranked
worst-first. Owner: 🐯 = Claude can do it solo (repo + SSH), 🐺 = needs Angelo (a
decision, a console, or a cost), 🤝 = both.

---

## ✅ Tier 0 — done
- [x] **Off-box backups** — encrypted, restore-verified dumps ship to Backblaze B2
      on every prod deploy; round-trip proven. *(was the #1 gap: box death = data death)*

## 🟢 Tier 1 — quick wins (do next, hours not days)
- [ ] **1. Finish the backup story: immutability** — 🤝 — bucket has Object Lock on
      but no retention, and the key can delete → off-box but not ransomware-proof.
      Fix: a **write-only** B2 key + **default retention** (e.g. 14-day compliance) +
      a lifecycle rule for cleanup. *You: 2 clicks in the B2 console. Me: wire it.*
- [ ] **2. `make` on the box** — 🐯 — docs say `make backup`/`make apply`; box has no
      `make`. One `apt-get install -y make`.
- [ ] **3. Kill the client-secret coupling** — 🐯 — `KC_CLIENT_SECRET` must match the
      realm JSON by hand (it bit us). Make it a single source (vault ref or generated
      in `prod-apply`). Removes a whole class of "login broke on deploy".
- [ ] **4. Consolidate `ops/`** — 🐯 — `deploy.py` vs `promote.py`, `set-idp.py` vs
      `prod-apply.py`, three ways to stamp a realm. Collapse into one clear path so a
      junior isn't guessing. *(I made this sprawl worse — I'll clean it.)*

## 🟡 Tier 2 — the real safety net
- [ ] **5. Test coverage that matters** — 🐯 — today: 14 shallow tests. Add the OIDC
      login flow, RBAC gating (admin-only routes), profile + ticket CRUD, and an
      `ops/` smoke. Then the CI gate is a net, not a speed bump.
- [ ] **6. Observability** — 🤝 — nothing watches it live. Add **uptime + alerts**
      (self-host Uptime Kuma, $0, I deploy it) and **error tracking** (self-host
      GlitchTip, or hosted Sentry free tier). *You: pick self-host vs hosted.*

## 🟠 Tier 3 — structural / your call
- [ ] **7. Feature triage** — 🐺→🐯 — robot / DuckDNS / money / i18n: which are core
      vs demo? You decide what stays; I prune the grab-bag so "what you get" is honest.
- [ ] **8. Break up `main.py`** — 🐯 — 505-line kitchen sink; split routers by concern.
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

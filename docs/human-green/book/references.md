# References — Human-Green

Every factual claim in the book, and where it came from. Built as we go, so
re-checking a chapter after an edit is cheap instead of a full re-derivation.

Verdicts per `longhand/config/writing-kit/CHECK.md`: **VERIFIED** · **STALE** ·
**UNSOURCED** · **UNCHECKABLE** (no source exists on this machine — not a
failure, but say so).

Paths are relative to `~/repos/` unless absolute.

---

## Chapter 1 — Owe No One

*Last checked: 2026-08-11.*

| # | Claim | Verdict | Source |
|---|---|---|---|
| 1.1 | *"I just want to scan stuff and know what I sold. Today it's paper and pen."* | **UNCHECKABLE** | Felix said it to Angel, 2026-08-10. No source on disk and there shouldn't be. Recorded in `banco-starter/WORKLIST.md` (Gate Zero) and `freehold/docs/human-green/book/00-brief.md`. |
| 1.2 | 97.8% of stock carries synthetic `2000000…` in-store EANs | **VERIFIED** | `freehold/docs/GO-LIVE-PLAN-felix.md:20` |
| 1.3 | The figure comes from a 500-row sample | **VERIFIED** | `freehold/docs/GO-LIVE-PLAN-felix.md:3` — "the real 500-row sample" |
| 1.4 | The `2` prefix range is reserved worldwide for shop-internal codes | **UNCHECKABLE** | GS1 restricted-distribution range (`02`, `20`–`29`). External standard, no local source. Chapter states it loosely as "that range" — accurate in substance. |
| 1.5 | Felix's catalogue is 5,389 rows | **VERIFIED** | `banco-starter/WORKLIST.md` — "prod now holds **5,389**" |
| 1.6 | Freehold is Postgres + Keycloak + MinIO + Caddy + FastAPI | **VERIFIED** | `freehold/docs/private/FREEHOLD-SPEC.md:13-18` |
| 1.7 | Clone → `docker compose up -d` → dashboard in 5 minutes | **VERIFIED** | `freehold/docs/private/FREEHOLD-SPEC.md:6` |
| 1.8 | Cost prices never leave the box; enforced at the export edge, checked by diff | **VERIFIED** | `GO-LIVE-PLAN-felix.md:28` (locked decision 3) and `:45` (P0.1 gate) |
| 1.9 | *"The real RTO is bounded by Angel's consciousness."* | **VERIFIED** | `freehold/docs/GO-LIVE-PLAN-felix.md:124`. Quoted verbatim. |
| 1.10 | Bus factor one is a live risk, not a joke | **VERIFIED** | `GO-LIVE-PLAN-felix.md:124`, `:188` (risk register) |
| 1.11 | Backups ran green nightly while omitting staff logins and photos | **VERIFIED** | commit `4eb4f36`; `GO-LIVE-PLAN-felix.md:46` (P0.2) |
| 1.12 | The DR runbook had no restore step — it said register a new admin | **VERIFIED** | commit `0d24d13` |
| 1.13 | Both database dumps restored, `psql` exit 0 | **VERIFIED** | commit `0d24d13` |
| 1.14 | Restored identity DB: 4 realms, 5 users, 5 credentials, 6 role grants | **VERIFIED** | commit `0d24d13` |
| 1.15 | Keycloak 26.0.8 booted on the restored schema in 3.8s, no realm import | **VERIFIED** | commit `0d24d13` |
| 1.16 | A credential restored from backup obtained a valid token | **VERIFIED** | commit `0d24d13` |
| 1.17 | *"A restore procedure nobody has run is a rumor wearing a hat."* | **VERIFIED** | commit `0d24d13`, verbatim |
| 1.18 | The AI doc claimed no data left the EU; the endpoint is US-hosted | **VERIFIED** | `freehold/docker-compose.openwebui.yml:41` — `OLLAMA_BASE_URL: https://ollama.com`. Live config, not just the commit. |
| 1.19 | Two of the three named components existed nowhere in the repo | **VERIFIED** | commit `f02d376`. Re-confirmed 2026-08-11: `grep -ril litellm` matches only documents *about* the incident, never code. |
| 1.20 | For a Swiss shop, data residency is the reason they're talking to you | **UNCHECKABLE** | Judgement, stated as such in the chapter. |

### Fixed by the first check run, 2026-08-11

| Was | Verdict | What happened |
|---|---|---|
| *"the fix he made last Tuesday about which grinder is which"* | **UNSOURCED** | Invented. "Grinder" appeared nowhere in the repo except that sentence. Replaced with 1.5. |
| *"his 52 categories"* | **UNSOURCED** | `MAX_TAXONOMY` raised 40→52 in a script (`GO-LIVE-PLAN-felix.md:105`) — a config cap, not a fact about a man's shelves. Replaced with 1.5. |

### Needs re-checking

- **1.2 / 1.3** — 97.8% is from the pre-capture sample. If the catalogue capture
  moved it, the chapter's opening leans on the number being exact.

---

## Chapter 2 — The Crew of Two

*Not yet checked. Draft only.*

Most of its claims are about this project's own transcript — the 2,800-word
draft, the four-objective question, the escalation over the public repo. Those
are **UNCHECKABLE** against the repo by nature: the evidence is the conversation,
not the filesystem. Verify what *is* on disk (the seven incident notes, the
0001/0002 pairing, `ON DECK` in `CLAUDE.md`) and mark the rest honestly rather
than dressing it up.

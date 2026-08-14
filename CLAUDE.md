# CLAUDE.md — Freehold

*This file loads every session. Keep it short and true; update it when reality changes.*

---

## THE PROJECT

**What it is:** A production-grade self-hosted app foundation — FastAPI, Keycloak, Postgres, MinIO, Caddy — running live on the wolfhold box and serving several sites from one stack.
**Why it exists:** Own your stack, owe no one. No platform landlord, no lock-in, no per-user rent.
**Tech / tools:** Python, FastAPI, SQLAlchemy 2.0 (async), Jinja2, Keycloak OIDC, Postgres, MinIO, Docker Compose, Caddy.

## THE CODE WORD

**ON DECK** — read `WORKLIST.md` and start executing the top item. Don't re-plan what's already decided; don't ask what to work on.

## CURRENT SITUATION (2026-08-14)

- **🟢 LIVE in production** at `wolfhold.app`, with `ai`, `auth`, `staging`, `sandbox`, `tempest`, `wk` and `iw` alongside it. Signed-in flow works end to end: Keycloak vouches, the app trusts the token, nothing leaves the server.
- **Location:** `/home/angel/repos/freehold`. Deploys run **on the box** (`ssh wolfhold`, `/root/freehold`), never from the laptop.
- **This repo is PUBLIC.** Think before committing transcripts, customer detail, or pricing. There is an open UNDECIDED item in `WORKLIST.md` about exactly that.
- **Work spans three repos and `WORKLIST.md` is the one list** — Freehold, Longhand, and Tempest items all live there in priority order.
- **🕹️ Tempest is ours now.** It ships as a route (`app/static/tempest.html` + `app/routers/tempest.py` + a nav link), *not* a separate app, container, or subdomain. Its deck moved here on 2026-08-14 when `ground-control` was cut back to the kit alone. Prefer this route pattern for adding features.
- **⚠️ Health dashboard is DONE**, not "starting" — that mission line sat stale in this file for months. See `memory/2026-12-19-health-dashboard.md`.
- **Deploys may be gated.** `promote.py` gates on `backup.py` reaching the off-box target; see the BLOCKED section in `WORKLIST.md`, and note it currently disagrees with `~/repos/MAP.md` about whether the cap is lifted.

## STANDING RULES

1. **Write to files, not chat.** If it only lives in chat, it didn't happen.
2. **Execute, don't note.** If it can be done this turn, do it this turn.
3. **Read before edit.** Never modify a file not looked at this session.
4. **Prove, don't assume.** "Done" is a claim until the output is verified — and a health check can go green a beat before the system actually serves.
5. **Human-green beats machine-green.** Tests passing is a checkpoint, not the finish line.
6. **Steer, I row.** Angel owns direction; the copilot owns execution.
7. **When you find one problem, check for the pattern.** One bad endpoint → inspect its siblings.
8. **Prod changes are gated, never freehand.** PRE-FLIGHT → Angel says "deploy" → DEPLOY → POST-FLIGHT. Deliver a script he runs and screenshots, never a wall of commands to paste. Non-negotiable: `memory/deploy-ritual.md`.

## KEY PATTERNS (follow these exactly)

- **Models:** SQLAlchemy 2.0 declarative in `app/models.py`, `Base = DeclarativeBase`
- **Routers:** FastAPI `APIRouter` in `app/routers/`, registered in `app/main.py`
- **Templates:** Jinja2 via `deps.templates.TemplateResponse`
- **DB:** async sessions via `app/db.py` `async_session`
- **Tests:** pytest in `app/tests/`
- **Ops:** `ops/*.py` — `promote.py` to ship, `backup.py`/`backup-volumes.py` for backups, `deploy.py` on the box

## MEMORY

`memory/MEMORY.md` is the index — one line per fact. Open a memory file when its line says it's relevant. Before touching the box, read `memory/freehold-caddy-sop.md`. Before any prod deploy, read `memory/deploy-ritual.md`.

## LESSONS (append-only)

- **2026-07-09 — Caddy must start with the prod overlay.** Base compose alone leaves `SITE_DOMAIN` empty, Caddy reads the collapsed line as a global-options block, and it crash-loops. Two prod mistakes the same day, both from acting without confirming state — that's where the gated ritual came from.
- **2026-08-14 — A spine that isn't in git is one `git clean` from gone.** This file was untracked for months while claiming the current mission was a task that had already shipped. A stale spine is worse than none: a cold session trusts it.
- **2026-08-14 — Client code without server routes fails silently.** `static/tempest.html` calls `/me`, `/api/ping` and `/api/scores`; this app serves none of them, and the `.catch()` swallows it. Nothing looks broken and nothing works. If you ship a client half, ship the server half or write down that you didn't.

---

*Last updated: 2026-08-14*
*"Own your stack, owe no one."*

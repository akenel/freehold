# MEMORY — Index

*Loaded every session. One line per memory — this is the map; the `memory/*.md` files are the territory.*
*Open a memory file only when its line says it's relevant right now. Never put memory content here.*

- [Deploy ritual](deploy-ritual.md) — the gated PRE-FLIGHT → "deploy" → DEPLOY → POST-FLIGHT method for ALL prod changes, and why; **read before any production deploy**
- [Freehold Caddy SOP](freehold-caddy-sop.md) — wolfhold box gotchas: Caddy needs the prod overlay or it crash-loops, **`reload` after a `git pull` silently applies the OLD file (stale bind-mount inode) — use `--force-recreate`**, routing an external app; **read before touching the box**
- [Health dashboard](2026-12-19-health-dashboard.md) — why HealthCheck isn't append-only, the direct-httpx pattern, the `from main import app` test import path; open when working on `/status` or adding a router

---

*Adding one? One fact per file, frontmatter with `name` / `description` / `type`, then one line here.
Check for an existing file that covers it before writing a new one. Full method:
[ground-control/kit/MEMORY-SYSTEM.md](https://github.com/akenel/ground-control/blob/main/kit/MEMORY-SYSTEM.md).*

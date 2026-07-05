# Freehold — internal docs

*Everything here is **internal**. It lives under `docs/private/`, which is physically
outside the public site's `docs_dir` (`docs/public/`), so **none of it is ever
published** — see the safety note in `mkdocs.yml`. Read it nicely in a browser with
`make docs-read` (→ http://127.0.0.1:8001).*

## What's here

### 📈 Business strategy — [`studio/`](studio/README.md)
The plan for turning Freehold into sellable SaaS: the sourced pain research, the scored
app portfolio, the roadmap, and the runnable Phase-0 validation pack. Start with the
[studio README](studio/README.md) or the one-page [boss brief](studio/BOSS-BRIEF.md).

### 🛠️ Product runbooks
Freehold's own operational docs:

- [FREEHOLD-SPEC.md](FREEHOLD-SPEC.md) — what it is, and what it deliberately says *no* to
- [GOING-LIVE.md](GOING-LIVE.md) — production, shared auth, the promotion ladder
- [HARDENING.md](HARDENING.md) — the perimeter + security posture
- [SECRETS.md](SECRETS.md) — SOPS + age secret management
- [SOCIAL-LOGIN.md](SOCIAL-LOGIN.md) — Google / GitHub / Facebook sign-in
- [EMAIL.md](EMAIL.md) — SMTP / forgot-password wiring

---
*Public, outside-reader docs live in [`../public/`](../public/) and are the only thing
the deployed site publishes.*

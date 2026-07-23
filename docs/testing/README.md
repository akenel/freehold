# Freehold — Testing (the golden kit) 🐺🐯

*How a change earns its way from local → sandbox → prod. Machines confirm it didn't
break; a human confirms it's actually **good**. Adapted from the HelixNet/Banco QA
library — the battle-tested house standard.*

---

## The gates (in order, no skipping)

| # | Gate | Catches | Tool |
|---|------|---------|------|
| 1 | **Machine** | dead endpoints, regressions, broken auth wiring | `make test` (22 tests, no infra) + `alembic upgrade head` on boot |
| 2 | **Human sanity check** | "it runs but feels wrong" — UX, copy, the real flow | the **fillable HTML sheets** in this folder |

**Flow:** build locally → green on Gate 1 → **run the sandbox sheet on `sandbox.wolfhold.app`**
→ ask Angel for explicit sign-off → deploy to prod → **run the prod hypercare sheet on
`www.wolfhold.app`**. Never deploy to prod without the sandbox sheet green and the human go.

---

## What's in here

| File | Use |
|------|-----|
| **`TEST-SHEET-TEMPLATE.html`** | The **golden template**. Copy it per feature. Live progress %, timer, one-tap PASS/FAIL per row, 🎤 voice notes, autosave, Copy/Download results. No dependencies — open in Chrome/Edge. |
| **`TEST-business-hub-sandbox.html`** | Ready-to-run **sandbox** sheet: SSO login, core screens, and the Business Hub pull→transform→store→record. Run this before promoting to prod. |
| **`HYPERCARE-PROD.html`** | The **prod hypercare** sheet: run right after every prod deploy — HTTPS, all three logins, the back-button fix, Business Hub, health, `/register`. |
| `archive/` | Signed PDFs of completed runs live here. |

---

## Make a new sheet (2 minutes)

1. `cp TEST-SHEET-TEMPLATE.html FEATURE-NAME-<env>.html`
2. In the new file, change only the marked bits (the engine is done):
   - `<title>`, the `.docid`, `<h1>`, `.sub` — name the test
   - the `.links` block + `.creds` — your click-to-test URLs and how to log in
   - the `.meta` build/login values — what's under test
   - `var LSKEY = '…'` — a **UNIQUE** key (so saved state doesn't collide with another sheet)
   - `var CHECKS = [ {do, exp, big?} … ]` — one row per step; mark the make-or-break with `big:true`
3. Open it in a browser, hand it to the tester.

## Fill it (important)

Fill it **on screen** — tick verdicts, type/dictate notes — **then** hit **🖨️ Print / Save
as PDF**. A browser-printed PDF *freezes* the fields, so always complete it in the browser
first. Everything autosaves to that browser (close/reopen = progress kept). Hit **📋 Copy
results** to paste the run back to Tig.

## Sign-off rule

Sandbox sheet 100% green → **explicit go from Angel** → deploy to prod → run the prod
hypercare sheet → archive the signed PDF in `archive/`. Prove, don't assume — human-green
beats machine-green for anything a user sees.

---
*🐺 own your stack · owe no one — and test it like you mean it.*

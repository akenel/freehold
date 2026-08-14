---
name: deploy-ritual
description: The two-part before/after gated deploy method Angel & Tig agreed on for ALL prod changes — recall before any production deploy
type: feedback
---

**For any change touching production, Tig delivers a two-part runbook/script — never a wall of commands to copy-paste** (Angel has copy/paste issues; a script he runs + screenshots is a screwdriver, a pasted command wall is a broken hammer).

**The ritual (agreed 2026-07-09):**
1. **PRE-FLIGHT (before)** — a check script: is the current state sane? is the change ready? will anything collide (ports, config, upstream)? Ends with a clear **GO / NO-GO** and then STOPS.
2. **THE GATE** — Angel reads the pre-flight output (screenshots it to Tig) and explicitly says **"deploy"**.
3. **DEPLOY** — Tig runs the full deploy, all the way, new build number.
4. **POST-FLIGHT (after)** — the second half: is the new SHA actually serving? does the feature work? did anything regress? Ends with **✅ 100%** or **❌**.

Every prod change = one paired artifact (before + after), one human pause in the middle. **Nothing is "done" until POST-FLIGHT is green.**

**Why:** Two prod mistakes on 2026-07-09 (over-probing → firewall block; forcing Caddy onto :443 → crash-loop) both came from *acting without a pre-flight check and confirming state*. The gate + paired checks make those impossible to repeat. Delivery: commit the script to the repo → Angel `git pull` + `bash` on the box → screenshots the output (screenshots work around the broken clipboard).

**How to apply:** Before ANY prod deploy, write `pre-flight` + `post-flight` (one file or two), push, and have Angel run pre-flight first. Wait for his "deploy." See [[method-works]]. Could graduate into the Ground Control kit itself — it's a genuinely good practice.

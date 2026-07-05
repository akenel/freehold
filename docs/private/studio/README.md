# 🏗️ Studio — what to build, and why

This folder is the **strategy layer** for turning the Freehold starter kit into
sellable, business-grade software. It answers the question a new lead has to answer
before writing product code:

> *What do we build first, for whom, and how do we know people will pay for it?*

It is deliberately **paper before code** — a direction we can defend to the boss with
sources, not a demo we can't back up.

## The decisions this folder is built on

| Decision | Choice | Where it's argued |
|---|---|---|
| Who the software is for | **SaaS sold to other small businesses** | [00-brief](00-brief.md) |
| Market | **Switzerland beachhead → Germany scale** (DACH) | [00-brief](00-brief.md), [01](01-pain-landscape.md) |
| The forcing function | **Germany's B2B e-invoicing deadline (all firms by 1 Jan 2028)** | [01](01-pain-landscape.md) |
| Sector | **Construction / trades (Handwerk)** — manufacturing ruled out | [01](01-pain-landscape.md) |
| The wedge | **The workflow for the smallest crews — NOT another invoice generator** | [02](02-app-portfolio.md) |
| Monday deliverable | **A sharp strategy doc + roadmap** (no code changed) | this folder |

## Read in this order

1. **[00-brief.md](00-brief.md)** — situation, mission, the compliance-ratchet thesis, honest risk.
2. **[01-pain-landscape.md](01-pain-landscape.md)** — the *sourced* pains, Switzerland + Germany, every claim tagged verified/unverified.
3. **[02-app-portfolio.md](02-app-portfolio.md)** — candidate apps scored; the beachhead wedge and the bet.
4. **[03-roadmap.md](03-roadmap.md)** — 30/90/180 days with a two-test validation gate.
5. **[04-team-and-freehold.md](04-team-and-freehold.md)** — junior execution + the Freehold gaps (multi-tenancy, DE/FR/IT).
6. **[phase-0/](phase-0/README.md)** — the runnable validation pack. **This is the Monday work.**

## The one-paragraph version

Compliance is a rising, regressive tax on small firms — and **Germany just put a hard
deadline on it** (every trades firm must issue digital invoices by **2028**; ~1M firms,
avg 6 people). The big tools are too complex for a two-man crew and the invoice *format*
is already commoditized, so the opening is the **whole job-to-cash workflow made dead
simple on a phone** — the life raft, not another generator. We **land at home in
Switzerland** (a small, dated QR-bill tool every firm needs before a Sept-2026 bank
cutoff — low risk, real revenue), then carry the same workflow into Germany on the 2028
deadline. We **validate price, the workflow gap, and DATEV lock-in with real firms first**.

## How to use it with the boss

Hand him **[BOSS-BRIEF.md](BOSS-BRIEF.md)** — the one-page, decision-first summary. If he
wants the evidence, **[00-brief.md](00-brief.md)** and the scorecard in
**[02-app-portfolio.md](02-app-portfolio.md)** are the working-out that proves we didn't guess.

---
*Status: complete, re-anchored UK → Switzerland/DACH. Grounded in two deep-research
runs (Switzerland + Germany/Austria; 44 sources fetched, claims adversarially
fact-checked). Verified vs. unverified is tagged throughout [01](01-pain-landscape.md)
— the honest split is the point, and the commercially-critical claims are the unproven ones.*

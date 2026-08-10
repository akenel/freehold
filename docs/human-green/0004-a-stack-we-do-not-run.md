# 0004 — A stack we do not run

- **Date:** 2026-08-10
- **Where:** `docs/private/openwebui-AI-wolfhold-app.md`
- **Commit:** `f02d376`
- **Cost:** near-miss, and the expensive kind — this was outward-facing copy
  about data residency for Swiss SMEs

## What the machine reported

A clean, confident transcript describing the AI deployment:

> "Self-hosted AI (Open WebUI + LiteLLM + Llama.com API) — No reliance on
> US-based AI providers"
>
> "No data leaves the EU — Full GDPR compliance"

Nothing flagged it. There is no test for a sentence.

## What was actually true

Neither claim held.

- `docker-compose.openwebui.yml` sets `OLLAMA_BASE_URL: https://ollama.com`,
  which is US-hosted. **Every prompt leaves the box.**
- There is no LiteLLM anywhere in the repo and no Llama.com key. The document
  described a stack that exists nowhere — verified by grep.

For the Swiss SME market, data residency *is* the pitch. That wording would not
have survived one question from an IT lead or a Treuhänder, and the question
would have arrived in a sales conversation.

## How the gap surfaced

Reading the claims against the compose files deliberately, and grepping for the
components named. The check took minutes. Nothing would ever have surfaced it on
its own.

## The shape

**Documentation is green until someone greps it.** Prose has no test suite, no
type checker and no linter, so a confident false claim can sit indefinitely
looking exactly like a true one — and marketing copy is the highest-stakes
untested code in the repo, because it is the part that reaches customers.

Corollary: claims that name specific components are *checkable*. "Self-hosted AI"
is vague enough to argue about; "Open WebUI + LiteLLM + Llama.com API" can be
grepped in ten seconds. Prefer the specific claim — it is the one that can be
caught.

## What changed

An accuracy note sits at the top rather than editing bKf's words — the transcript
stays a faithful record, the correction sits above it.

Reframed the honest way, which sells better anyway: **self-hosted interface,
identity and chat history on a Swiss box; the brain is a plug.** Names Apertus
(Swiss AI Initiative — EPFL/ETH Zurich/CSCS, Swisscom strategic partner) as the
sovereign option with its four access routes and which one to quote.

Two things flagged so nobody promises them by accident: this 4 GB no-GPU box
cannot run Apertus locally — sovereign here means a Swiss-hosted endpoint, not
local inference — and `openwebui_data`, the entire chat history, had no backup
at all. See [0005](0005-the-backup-that-never-saw-it.md).

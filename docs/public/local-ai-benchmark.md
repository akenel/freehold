# Can a small business run its own AI? — a measured answer

*Measured 2026-07-29 on an ordinary laptop. Numbers below are from that run, not estimates.*

Every small business asking "can we stop pasting our data into ChatGPT?" gets told either *"yes, easy!"* or
*"you'd need a GPU server"*. Both are sales pitches. Here is what actually happened when we measured it.

---

## The machine

Deliberately unimpressive — a working laptop, not a server:

| | |
|---|---|
| CPU | 8 cores (Intel Tiger Lake, laptop class) |
| GPU | **none** — integrated Intel Iris Xe, unused for inference |
| RAM | 15 GB total, **3.5 GB free at test time** |
| Other load | Two full application stacks running *during* the test (2 Postgres, 2 Keycloak, MinIO, Caddy) |

That last row matters. This was not a clean bench — the machine was already busy.

## The question we asked it

> *A small Swiss retail shop currently uses ChatGPT for writing product descriptions, but is worried that customer
> and supplier data leaves Switzerland. They have one back-office PC. In 5 short bullet points, explain what they
> would need to run an AI assistant entirely on their own hardware, and roughly what it would cost.*

A real prospect question, so we measured answer quality and not just speed.

## Results

| | deepseek-r1:1.5b | **llama3.2:3b** |
|---|---|---|
| Model size on disk | 1.1 GB | 2.0 GB |
| Load time | 2.5 s | 4.8 s |
| Generation speed | **31.4 tok/s** | 13.2 tok/s |
| RAM used while running | 1.3 GB | **1.6 GB** |
| 400-token answer | 16 s | 37 s |
| Usable answer? | ✗ | **✓** |

**13 tok/s is about reading speed.** A 150-word product description lands in ~10 seconds. In practice, nobody
waits on it.

### Why the faster model lost

`deepseek-r1:1.5b` is a *reasoning* model — it thinks out loud before answering. It spent its whole budget
deliberating and never reached the point. Fast, and useless for this task.

`llama3.2:3b` returned a properly structured answer with concrete CHF figures across hardware, OS, storage,
software and security. Half the speed, actually useful.

**Raw speed is the wrong metric.** Pick the model that fits the job.

---

## The honest caveat: what a 3B model is NOT for

The winning answer also recommended **Google Cloud and Microsoft Azure** for storage — to a shop that came in
worried about data leaving Switzerland. It suggested Rasa, spaCy and Dialogflow, which are chatbot frameworks,
not ways to host a language model.

Confidently wrong, in a way that reads as authoritative.

So be precise about the job:

| Good fit for a 3B model | Not a fit |
|---|---|
| Product descriptions, listings | Legal, tax or compliance advice |
| Email and letter drafting | Anything where a wrong fact is expensive |
| Translation (DE/FR/IT/EN) | Strategy or architecture decisions |
| Summarising a supplier PDF | Anything unverified going straight to a customer |

**A small local model is a good typist, not a good advisor.** That's usually exactly what the shop wanted anyway.
Bigger models (7–14B) narrow this gap but need more hardware — see sizing.

---

## Sizing guide

The first row is measured. The others are extrapolation and are marked as such.

| Workload | Spec | Rough cost | Basis |
|---|---|---|---|
| A few staff: descriptions, emails, translation | **16 GB PC, no GPU** | ~CHF 600 mini-PC, or **the PC they already own** | ✅ measured above |
| Whole team, longer documents, 7–8B models | 32 GB + modest GPU | ~CHF 1,500–2,500 | estimate |
| Heavy use, 14B+, several concurrent users | dedicated GPU box | CHF 3,000+ | estimate |

**Start on hardware they already own.** No capital decision on day one: prove it earns its keep, then size up.
The bottom rung is real and we measured it on a busy laptop.

---

## What this does and doesn't prove

**Proves:** useful local inference needs no GPU and no new hardware to *start*. The technical feasibility question
is settled. What remains is a sizing conversation, not a "can it work" conversation.

**Does not prove:** that a 3B model is good enough for a given business. That depends entirely on the task — see
the caveat above. Test the customer's *actual* work before promising anything.

**Not measured yet:** concurrent users, long documents (>2k tokens), 7B/14B models on the same hardware, sustained
load over a working day, quality in German/French/Italian.

---

## Reproducing this

```bash
ollama pull llama3.2:latest
curl -s http://localhost:11434/api/generate -d '{
  "model":"llama3.2:latest",
  "prompt":"<your real task here>",
  "stream":false,
  "options":{"num_predict":400}
}' | jq '{eval_count, eval_duration, load_duration}'
```

Generation speed = `eval_count / (eval_duration / 1e9)`. Use the customer's own task as the prompt — a generic
benchmark tells you nothing about whether it will work for them.

# NNNN — <short title, the thing that was wrong>

- **Date:** YYYY-MM-DD
- **Where:** <file, service, or system>
- **Commit:** <hash, if there is one>
- **Cost:** <minutes of outage / francs / data at risk / near-miss>

## What the machine reported

<Quote it. The exact green output, the passing test name, the "success" line.
This is the most valuable part of the note and the first thing you will forget.>

## What was actually true

<The reality the green did not cover.>

## How the gap surfaced

<What made you look. Was it a user, a bill, a hunch, a manual check, a drill?
Note honestly if it was luck — the ones found by luck are the important ones,
because there is no repeatable process behind them yet.>

## The shape

<One sentence, general enough to apply to a system you have not built yet.
If you cannot write this line, the incident is not understood yet.>

## What changed

<The fix — and separately, whether anything now *detects* this class of thing.
A one-off fix with no detector means the next instance is also found by luck.>

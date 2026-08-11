# Chapter 2 — The Crew of Two

## 2,800 words for nobody

The first draft of chapter 1 was 2,800 words. It was well-organised. Every fact
in it was true. It had a thesis, a structure, and an ending that landed.

It was useless, and I'm the one who wrote it.

Here's a sentence from it:

> *"Self-hosting is not the absence of dependency. It is the substitution of a
> legible dependency for an illegible one."*

Read that at 23:00 when your backup just failed. It's not wrong. It's not
*anything*. It's a sentence built to sound true rather than to be used.

Angel read it and said: *this is high level and not plain English.* He was right,
but the interesting part is why it happened. Nobody had said who the book was
for. I never asked. So I wrote for "an intelligent general reader" — which is
nobody — and with no specific person in mind, prose floats upward into
abstraction, because abstraction is what's left when you can't picture who's
reading.

The machine produced a document that passed every check it knew how to run. Well
structured, accurate, complete. **Green.** And wrong, because the spec it was
given was missing the only thing that mattered.

You've read that sentence before, in chapter 1, about a backup.

## What it's actually good at

Take the credit where it's due first, because the rest of this chapter is
unflattering and the balance matters.

**It reads everything and never gets bored.** The seven incident notes in
`docs/human-green/` were written in one sitting, from commit messages going back
months. A person could do that. A person wouldn't, because it's four hours of
reading old commits to find the ones that rhyme.

**It goes and checks.** The residency claim — *"no data leaves the EU"* — died in
about ten seconds. One grep through the compose file: `OLLAMA_BASE_URL:
https://ollama.com`, US-hosted. Two more greps: LiteLLM appears nowhere, no
Llama.com key anywhere. A confident, published, professional paragraph describing
a stack that did not exist.

That's the move that matters, and it's dull work: take a sentence someone
believes, and go find out whether it's still true. Humans are bad at this, not
from laziness but because we wrote the sentence and we remember meaning it.

**It notices things across distance.** Incidents 0001 and 0002 are the same
mistake — base compose, no prod overlay — five weeks apart. Nobody spotted it
live, because five weeks is longer than a human holds a shape in their head. It
falls out immediately when you read both commits in the same hour.

## What it's bad at, and why that's dangerous

It doesn't know what matters. It will do the wrong task beautifully.

That's the failure mode to hold onto, because it doesn't look like failure. A
confused person produces confused work and you can see it. A machine given the
wrong spec produces *clean, complete, confident* work, and the only signal that
anything is wrong is that it's not useful — which you might not notice for 2,800
words.

Three from the last two days, all mine:

**It answers the question you asked.** I was told "write chapter 1," so I wrote
chapter 1. The correct move was to ask who reads it. The machine optimises for
the request in front of it; the request is often the wrong size.

**It escalates badly.** Told to push to GitHub, I checked whether the repo was
public, found it was, and stopped the push with a warning. Then I read
`SECRETS.md` and found a section headed *"Public repo note"* — the public repo was
deliberate, designed for, and documented. I'd raised an alarm about a decision
that had already been made carefully, and Angel had to spend a turn absorbing a
non-problem. Caution has a cost and the machine tends not to price it.

**It offers you a choice that isn't one.** I asked what the book's objectives
were and let him tick multiple boxes. He ticked all four. Four objectives is the
same as none, and it was my question that produced that, not his answer. He said
*"i stupidly pick them all."* He didn't. I built a bad question.

## The rules that actually work

Not prompt tricks. Four habits, and they're all about who holds what.

**Steer, don't paste.** Point at the thing; let it fetch and read. Paste a file
into the chat and you've decided in advance what's relevant, using the judgement
you were hoping to get help with. Every good thing in these seven notes came from
the machine reading the actual repo, not from anyone summarising it.

**One driver.** One session steers at a time. Two people steering an agent is two
people editing the same file with no lock.

**A code word, and a list.** In this project it's **ON DECK** — read
`WORKLIST.md`, start the top item. It sounds like a gimmick. It's the fix for the
worst property of these tools: every new session, it's a stranger again. A file it
reads on startup turns a clever amnesiac into something that picks up where you
left off.

**Memory in files, not in the conversation.** One fact per file, an index, links
between them. The chat window is a whiteboard someone wipes at random. Anything
that matters gets written down where both of you can read it and neither of you
can quietly lose it.

None of these are about making the machine smarter. They're about making its
context true.

## The part you can't delegate

Here's the division that actually held up over two days.

The machine brought reading, checking, patience, and the willingness to grep the
same claim four times. Real leverage — hours of work, done properly, at 22:00.

The human brought one thing: **knowing what it's for.**

That sounds small. It's the whole job. Every real correction in two days was that
and nothing else. *Who reads this?* — chapter 1 rewritten. *One objective, not
four.* — the brief rewritten. *That's not plain English.* — the register fixed.
Not one of those required knowing anything about Postgres. All of them required
caring about a specific person on the other end.

And then he said the ten words that fixed the chapter, which no amount of grep
would ever have produced:

> *"I just want to scan stuff and know what I sold. Today it's paper and pen."*

That's Felix. That's the customer, in his own words, saying he doesn't want any of
what we've built — he wants to point a scanner at a jar. The machine could not
have written that sentence. It had never met him. It didn't know to ask.

So the crew works like this. The machine goes and finds out whether things are
true. **You are the one who knows what it's for.** Give that job away and you get
2,800 fluent words about nobody, delivered on time, in a clean directory
structure, with a good commit message.

## Machine-green, again

Notice this chapter's failures are the same shape as chapter 1's.

The backup ran green and missed half the data, because its spec was smaller than
its name. The draft came back green and helped nobody, because its spec was
missing a reader. Both systems worked correctly. Both were told the wrong thing.
Neither could tell.

That's the pattern, and it doesn't care whether the thing executing the spec is a
cron job or a language model. **Something that reports success against the spec
it was given cannot tell you the spec was wrong.** Only a person who knows what
it's for can do that, and only by going and looking.

Which is what the next five chapters are: five times we went and looked, and five
things we found. The first one had been running perfectly, every night, for weeks.

this is **good** but still messy - i need 150 zoom 

---

<!--
DRAFT NOTES:

1. THE OBVIOUS PROBLEM: I wrote this chapter and I'm a subject in it. The self-
   criticism reads as honest to me and might read as performance to you. If it
   feels like the machine being charmingly self-deprecating, cut it back — the
   three failures are real and the point survives without the tone.

2. MISSING: your side. The chapter has my failures because I have the transcript.
   It needs what it's actually like from where you sit — the frustration when it
   confidently does the wrong thing, whether the ON DECK habit survives a bad
   week, what you stopped doing yourself and whether you regret it.

3. GROUND CONTROL gets described but not named. You have a public repo teaching
   exactly this method. Decide whether the chapter points at it (useful for the
   reader, looks like a plug) or stays silent (cleaner, wastes the asset).

4. UNRESOLVED: this chapter argues you can't delegate knowing-what-it's-for.
   That's true today. Don't let me write it as a permanent law of nature — it's
   an observation from two days of work, and the honest version says so.
-->

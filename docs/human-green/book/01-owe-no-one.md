# Chapter 1 — Owe No One

## What the customer actually asked for

> *"I just want to scan stuff and know what I sold. Today it's paper and pen."*
>
> — Felix

That's the whole requirement. Ten words and a status report.

Notice what isn't in it. No stack. No sovereignty. No cloud, no self-hosting, no
data residency. He is not asking to own anything. He wants to point a scanner at a
jar and, at the end of the day, know what left the shop.

Everything in this book sits underneath that sentence. If you ever find yourself
defending an architecture that doesn't help a man scan a jar, you've lost the
plot, and this chapter is about the one exception — the reason the boring answer
was wrong for him.

Because "just scan stuff" turns out to be expensive.

## A barcode that only works in one building

Almost every barcode in Felix's shop is made up.

They start with `2000000`. That range is reserved, worldwide, for codes a shop
invents for itself. Scan one at any other till and nothing comes back — no
product, no price, no maker, no record it exists. Scan it at Felix's counter and
it lands on one jar, on one shelf, at a price he set.

97.8% of his stock. We counted, on a sample of 500 rows.

Those numbers are worth nothing to anyone on earth except the man standing at
that counter. That is what owning your data looks like when you go and actually
look at it. Not a principle. A number that only works in one building.

## You already made this choice

You have a box too. Maybe it's a VPS, maybe it's a machine in a cupboard. It runs
Postgres and something that talks HTTP, and there's a compose file you can read.

At some point you told someone — a client, a friend, a shop owner — that their
data stays on it. That nobody else gets to see it. That they aren't renting.

You were right to. Here's what you were actually turning down.

**The rent is per person.** Your customer hires a Saturday assistant and pays
more. The software isn't working harder. Headcount is just the meter the industry
agreed to bill against, so growth shows up as a cost.

**The data comes back in their shape, not yours.** Sure, there's an export. What
comes out is a CSV flattened from a structure you never saw. The photo-to-variant
links are gone. The supplier codes don't line up with the shelves. Three years of
hand corrections are in there somewhere, unmarked. The export exists so the sales
page can say the export exists.

**Leaving costs more the longer you stay.** Nobody plans this. It just happens.
Staff learn the screens. Label stock gets ordered to fit. The accountant builds
habits around the reports. After five years, moving costs more than staying, and
that's true even if everyone involved was decent about it.

That's why *landlord* is a better word than *supplier*. A supplier sells you a
thing. A landlord lets you stand somewhere, on terms, for as long as the terms
hold.

## What one box buys

So you run it yourself. Postgres for the data. Keycloak for the logins. MinIO for
the photos. Caddy in front. Your app behind it. All of it in files you can read in
an afternoon.

Clone the repo, `docker compose up -d`, and five minutes later you're looking at a
dashboard you own.

That five-minute number is the design target for Freehold, and it isn't about
speed. It's about who can act. If a stranger can go from nothing to running in
five minutes on a clean machine, then the shop doesn't depend on that particular
box, or that company, or that one person still being interested. The stack moves
because you can describe it.

For Felix that means the catalogue is in his shape — 5,389 rows of it, in his
categories, corrected by his own hand as stock moves. The photos are on his disk.
The cost prices — the numbers that tell a competitor what he pays and who he buys
from — never leave the box. Not by policy. By rule, enforced where the file gets
written, checked with a diff.

Own your stack, owe no one. It fits on a sticker.

Now the part that doesn't fit on the sticker.

## The bill nobody sends you

Running it yourself doesn't remove the dependency. It moves it onto you.

The sharpest line anyone wrote about this project is in our own go-live plan, and
it isn't flattering:

> **The real RTO is bounded by Angel's consciousness.**

RTO means recovery time objective — how fast you're selling again after the box
dies. Write "under 4 hours" in that column and you've quietly assumed an
organisation: a rota, a second engineer, someone whose shift starts when the first
one doesn't pick up.

There's no rota. There's one man. So it's four hours *if he's awake.* If he isn't
on a plane. If he isn't ill. If he isn't, that particular Saturday, unreachable
for reasons that would be completely fine in any other week.

You've heard "bus factor one" as a joke about consultants. It isn't a joke here.
It's the live risk sitting under a real shop's ability to take money.

Look at the actual trade. Felix stopped paying a company that would have answered
the phone at 3am on a bank holiday — which is the one thing a company can do that
a person can't. In exchange he got his data, in his shape, on his premises, with
no per-seat meter running. That's a good trade. It isn't a free one, and the part
he gave up only shows itself on the worst day.

Self-hosting doesn't mean you depend on nobody. It means you pick who.

Rent from a vendor and you're betting they stay interested in customers like
yours. You can't check that bet. You can't fix it. Run your own box and the bet
changes: that the backup ran last night, that the restore works, that there's a
spare machine in the cupboard. You can check all three tonight.

That's the whole deal. You swap a risk you can't check for one you can. The catch
is in the second half — you have to actually go and check it. Most self-hosting
stories stop right before that part.

## You own what you can restore

Here's the rule this book is built on. It cost us a bad week to find:

**You own what you can restore. Everything else you're just holding.**

Not "have root on." Not "keep in the building." Restore — the box is gone, and you
can build a working shop out of what's left.

Try it against Felix. The data is on his machine, in his building, in an open
format, under his hand. By any normal test, he owns it. Now take the machine away.
Fire, theft, a dead disk, a bad Tuesday. What does he have?

Whatever he can bring back.

If that's everything, in about four hours — he owned it. If it's the products but
not the staff logins and none of the photos — he owned some of it and was holding
the rest. If it's *we've never actually tried* — he didn't own it. He believed he
did. That's a different thing, and you can't tell the two apart until the only day
it matters.

We were the third case.

## What we found when we looked

For weeks the backups ran nightly, succeeded nightly, and shipped off-box nightly.
They saved the product database. They did not save the staff logins. They did not
save the photos.

Nothing was ever red. There was nothing to be red about. The job did exactly what
we told it to do. What we'd told it to do was smaller than what the word *backup*
meant to everyone who read it.

While that was going on, the disaster-recovery document — written, checked in,
followed end to end without error — had no restore step in it at all. It said:
bring up a clean box, then register a new admin.

That was right once, back when there was nothing to restore. Then we built
backups, and nobody went back to the document. So the official route from *dead
shop* to *trading shop* was: throw away every verified backup you've been
carefully shipping for weeks, and start from scratch.

Following the procedure correctly was the failure.

Nobody was careless. That's the interesting part. There was a backup system and it
was well built. There was a runbook and it was written down. There were tests and
they passed. Every piece did its job against the description it was given, and the
descriptions drifted away from reality by inches, over weeks, in a direction
nobody was looking.

The whole promise — own your stack, owe no one — was resting on a file nobody had
ever opened.

## How you prove it

The fix is boring, which is why this is a book about practice and not a manifesto.

Take a clean machine. Pretend the real box is gone. Using only what's off-site,
bring it back: the data, the logins, the photos, the certificate, the front door.
Run a stopwatch. Write down the real number.

It will blow up the first time. Volume permissions, realm import ordering, a
bucket that doesn't exist yet. Budget for that. Fix what broke, wipe it, do it
again from zero. It has to pass **twice** — once proves it's possible, twice
proves it's a procedure.

When we finally did this properly, we could write down things we'd only been
assuming. Both database dumps restored clean, `psql` exit 0. The login database
came back with 4 realms, 5 users, 5 credentials, 6 role grants. Keycloak booted on
the restored schema in 3.8 seconds with no manual import. And a password that
existed **only inside an encrypted archive** got a valid token.

That last one is the chapter in a single test. Not "the backup file is there." Not
"the restore command exited zero." A user who only existed in a backup logged in.

Every command in the runbook was run before it was written down. That order
matters more than it sounds. A runbook written first and run later is a
description of what somebody expected to happen. Our repo puts it harder, and I
haven't improved on it since:

> A restore procedure nobody has run is a rumor wearing a hat.

The same move works outside disaster recovery. Find the sentence everyone
believes, and go check whether it's true.

We had a document saying our AI setup kept every prompt in the country. One grep
through the compose file: the model endpoint was in the United States, and two of
the three named components didn't exist anywhere in the repo. Confident,
professional, published, wrong. One question from a customer's IT lead away from
being very expensive — because for a Swiss shop, data staying in Switzerland isn't
a feature bullet, it's the reason they're talking to you.

Prose has no test suite. Worth chewing on, since prose is what your customer
reads.

## Green is not proof

So chapter one doesn't land where a book with this title is supposed to land.

Owning your stack is still worth doing. Felix made the right call and nothing
later in this book takes that back. A risk you can check beats one you can't, and
a catalogue in your own shape on your own disk is worth real money and real
hassle.

But *owe no one* isn't something you achieve by moving hardware into a building.
It's a claim about recovery. A claim about recovery is worth exactly what you've
tested it against. The vendor's version is backed by a balance sheet, an SLA and a
phone number. Yours is backed by what you've proven — on a stopwatch, twice, from
zero.

Which lands us where the rest of this book lives.

Every failure in these pages was **green** at the moment it mattered. The backup
succeeded. The tests passed. The deploy said healthy. The config validated. The
runbook was complete. The docs were confident.

Nothing malfunctioned. Every system did what it was told, reported success, and
was wrong — because somebody had defined success slightly too narrowly, and that
somebody wasn't thinking about a Saturday with six people in the queue.

Machine-green is a statement about a spec. Human-green is a statement about
reality. The gap between them is where your customer's ability to take money
actually lives, and nothing automatic will ever tell you it has opened.

That gap is what this book is about. The next chapter is about the two of us who
went looking for it — one human, one machine — and a way of working that turned
out to matter more than either.

---

<!--
DRAFT NOTES — Angel, these need your hand, not mine:

1. FELIX, THE PERSON. Still near-anonymous on purpose. He's real and will
   probably read this, so I've invented no biography and no dialogue. There's a
   hole around "What one box buys" that wants ~150 words of real Felix: how you
   met, what he used before, what he said when you explained the box. One true
   remembered line from him beats anything I can write there.

2. THE OPENING NUMBER. 97.8% is from the 500-row sample. If the catalogue
   capture moved it, correct it — the opening leans on it being exact.

3. THE VENDOR SECTION is generic on purpose. If Felix was quoted a specific
   system at a specific price in CHF, put it in. Real francs beat my three
   abstract terms.

4. "A BAD WEEK." The backup and runbook findings were the same day, 2026-08-10.
   Left vague here; chapters 3-5 own those incidents and can carry the real
   dates. Flagged in 00-brief.md as undecided.

5. STILL UNRESOLVED, AND THE CHAPTER SAYS SO: bus factor one is named and not
   answered. The plan's answer — a cold spare plus a runbook someone who isn't
   you can run — isn't built yet. Don't let me write that resolution before it
   exists. That's the exact failure this book is about.
-->

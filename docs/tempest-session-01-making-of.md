https://github.com/akenel/ground-control


 ▐▛███▜▌   Claude Code v2.1.205
▝▜█████▛▘  Opus 4.8 (1M context) · Claude Max
  ▘▘ ▝▝    ~/repos/ground-control

 ⚠ 1 MCP server needs authentication · run /mcp

 ▎ Extended: Fable 5 is included in your weekly limit
 ▎ Through July 12, you can use up to 50% of your weekly usage limit on Fable 5. If you hit your limit, you can continue on Fable 5 with usage credits. Fable 5 draws down usage faster than Opus 4.8. Run /model and select Fable to use it. Learn more

❯ i just lost the last repsonse can you bring it back

I don't have that previous response in my context — this conversation starts fresh for me, and a chat response that wasn't written to a file isn't something I can retrieve from thin air. But let me check the two places it might have been saved before I give up on it.

  Listed 1 directory

Both the memory folder and the scratchpad are esn't in my context window — so there's genuinely
nothing to "bring back." A chat message that wae once it scrolls off; I can't recover it froma previous session.

The good news: if you tell me roughly what it was about, I can regenerate it — usually better the second time, since you
know what you're looking for now. A couple of q

- Tell me the gist — "you were helping me fill u drafted my memory files" / "you wrote out X" — and I'll rebuild it.
- Or paste any fragment you still see on screent from there.

One thing worth doing so this doesn't bite you osophy is write to files, not chat (that's rule#1 in STANDING-RULES.md). If the lost response was something that mattered, the fix is to have me put it in a file next time
— a memory, a draft, wherever it belongs — so i

What was the response about?

✻ Worked for 16s

❯ you were helping me fill in the CLAUDE template

Right — let's pick that back up. Let me re-readexample so I'm guiding you from the actualsource, not my memory of it.

  Read 2 files

Got the template and the example back in front of me. Since I lost whatever you'd already told me, let's rebuild the top of
it fast — these are the blanks that everything h or as little as you want in one go and I'llwrite the filled CLAUDE.md into your project (not chat, so it survives this time):

1. Who you are — your name/handle, and one line on what you're about.
2. Your copilot — what you want to call me in t you want me to behave.
3. The project — what are you building, in a sentence? And the real why behind it.
4. Where it lives — the root folder/path this phe worklist + memory folder in the right place).
5. Code word — the phrase you'll type on a cold start that means "read the worklist and GO." (The example uses ON DECK —
steal it or pick your own.)

If any of that is stuff you already told me befst re-drop it — I'll capture it into the filethis round so we don't lose it again. Which one do you want to start with, or fire them all at once?

✻ Churned for 19s

❯ 1. angel and i am a developer since the cobol days -- i went to mohawk college 3 year computer tech co-op and graduates and
  worked at waste water tech center in burlingtonss control and monitor systems pilot plants it was goverment contract work and we used bollogical phycial and chemical methods to clean the water on an inductrial scale
  for paper mills stell plants oil refiners etc..w unemplyed 2. Tiger or Tig ot Tigs like tig is opposite spelling for git 3. video game like the games we had paid for at the rcade back in the 80s like Tempest my fav 4.
  smae folder and subfolders of root ground-contr

Love it. Tig — opposite of git — I'll take it. shooter is a great, well-scoped first mission.Before I write a single file, one thing I have to get right, because it's the one hard-to-undo choice here:

Right now ground-control/CLAUDE.md is the kit's own onboarding spine (it's committed to git). If I drop your game's
CLAUDE.md at the root, I'd be overwriting that.ct spine live?

● User answered Claude's questions:
· Where should I put your game's CLAUDE.md, worklist, and memory folder? → In a subfolder (Recommended)

Subfolder it is — that keeps your reference kit intact. Let me read the memory-system spec so I set your memory/ folder up
in the exact format the kit teaches, then I'll

  Read 2 files

Perfect — I've got the whole spec in front of mrklist, and memory folder into tig-tempest/.Everything to files, nothing left in chat.

● Write(tig-tempest/CLAUDE.md)
Wrote 90 lines to tig-tempest/CLAUDE.md
# CLAUDE.md — Tig & Angel: the Tempest-lineage arcade shooter

*This file loads every session. It is Tig's permanent memory. Fill every blank, delete what you don't need, ke

---

## RESUME CODE WORD — "ON DECK"

**stop, open `WORKLIST.md`, state the top items, and start executing the first actionable one — do not re-plan
 or re-ask what's already decided.**
… +93 lines

● Write(tig-tempest/WORKLIST.md)
Wrote 29 lines to tig-tempest/WORKLIST.md
# WORKLIST — Tig & Angel (the deck)

*Single source of truth for what's next, in order. Top item is what "ON DECK" starts on.*

---

## ON DECK (do these next, in order)

ols (arrow keys / mouse), enemy behavior, win/lose. Write the answers to a `project` memory so we never re-lit
igate them.
… +22 lines

Now the memory folder — the index plus two starter facts (who you are, and the project's fixed decisions):

● Write(tig-tempest/memory/MEMORY.md)
Wrote 7 lines to tig-tempest/memory/MEMORY.m
# MEMORY — Index

*Loaded every session. One line per memory. The map; the `memory/*.md` files are the territory.*
*Open a memory file only when its line teow.*

- [Who Angel is](angel-who.md) — the captontext about him matters
- [Project: Tempest-lineage arcade shooter](project-tig-tempest.md) — what we're building and the fixed decisio
ns

● Write(tig-tempest/memory/angel-who.md)
Wrote 9 lines to tig-tempest/memory/angel-who.md
---
description: Angel's background — who the captain is, when it matters for tone or context
type: user
---
Angel is the captain. A developer since t 3-year Computer Technology co-op graduat
e. Career: built process-control and monitoring systems for pilot plants at the Wastewater Technology Centre in
 and chemical methods) for clients like p oil refineries. Born 1964-01-09. Current
ly between jobs.

; *Tempest* is his favorite, which is the seed of [[project-tig-tempest]].
… +4 lines

● Write(tig-tempest/memory/project-tig-tempest.md
Wrote 16 lines to tig-tempest/memory/project-tig-tempest.md
---
name: project-tig-tempest
description: What we're building and thepen before designing or coding the game
---

Building a single-screen, vector-style 80s arcade shooter in the lineage of Atari's *Tempest* (1981): the play
er rides the rim of a tube/well and shooem.

- **Tech:** HTML5 `<canvas>` + plain Javpendencies, runs in any browser. Chosen s
o "done" = Angel opens `game/index.html` and plays it (human-green).
… +10 lines

  Searched for 1 pattern

Spine is up and verified on disk. Here's what n

tig-tempest/
├── CLAUDE.md          # your filled spine — code word ON DECK, who you & Tig are, the project, the rules
├── WORKLIST.md        # the deck: 6 ordered itrked "LATER" list
└── memory/
    ├── MEMORY.md          # the index (2 lines
    ├── angel-who.md       # your background
    └── project-tig-tempest.md   # what we're b

A few choices I made so we could move — flag an
- Folder/copilot naming: folder tig-tempest/, game code will live in game/. Easy to rename.
- Tech: HTML5 canvas + plain JavaScript, no buione" means you open a file and play it, not"tests pass."
- I turned today's lost-response incident into DE.md — Rule 1 earned the hard way.

Let me also make sure I resume warm across my s files:

  Wrote 2 memories

That's the recovery done — and this time it's iext compaction. Your lost response didn't justcome back; it's now a proper spine you can reboot from cold with ON DECK.

Here's the thing worth saying plainly: that's the whole method working. A chat message vanished, but because we wrote it
down, it can't vanish again.

Next on the deck is item 1: lock the game feel., the controls, the enemies — hangs off twodecisions. Let me get those from you and then I'll start building the first playable frame you can actually open in a
browser.
Invalid tool parameters

● User answered Claude's questions:
· What shape should the playfield be? (This decision.) → Classic tube/well
· How should the player control the ship? → Mouse

Locked: classic tube/well + mouse control (click to fire). That's the real Tempest. Recording the decisions, then — Rule 2,
execute don't note — I'm building the first plast noting it.

● Update(tig-tempest/memory/project-tig-tempest.m
Added 2 lines
- **Tech:** HTML5 `<canvas>` + plain Jaependencies, runs in any browser. Chosen
so "done" = Angel opens `game/index.html` and plays it (human-green).
- **Home:** `ground-control/tig-tempest files stay untouched).
- **Copilot name:** Tig (git backwards).
- **Playfield:** Classic tube/well — a er rides the rim, enemies climb up from t
he center. (2026-07-09)
- **Controls:** Mouse — ship follows th to fire down the current lane. (2026-07-
09)

**Why:** Pure joy — Angel wants to build the feeling of the arcade cabinets he grew up on. See [[angel-who]].


● Write(tig-tempest/game/index.html)
Wrote 158 lines to tig-tempest/game/index.html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=dev
<title>TIG · TEMPEST — first frame</title>
<style>
  html, body { margin: 0; height: 100%; background: #000; overflow: hidden; }
  body { display: flex; align-items: cen cursor: crosshair; }
  canvas { display: block; }
… +148 lines

Now Rule 4 — prove, don't assume. I can't clickprove the JavaScript has no syntax errors before you open it, so you don't hit a blank screen:

  Ran 1 shell command

JS parses clean. But machine-green isn't the finish line here — you playing it is (Rule 5). Updating the deck to reflect
what's actually done, then handing you the whee

● Update(tig-tempest/WORKLIST.md)
Added 3 lines, removed 6 lines

## ON DECK (do these next, in order)

1. **Lock the game feel** — 3-4 decisions with Angel: playfield shape (classic tube/well vs. flat lane), cont
rols (arrow keys / mouse), enemy behavirs to a `project` memory so we never re-l
itigate them.
2. **First playable frame** — `game/inds the vector playfield and the player's s
hip on the rim. Angel opens it in a browser and *sees* it. (Human-green.)
3. **Movement** — player moves around ten controls.
4. **Shooting** — fire projectiles down the tube; they travel and despawn.
5. **One enemy** — a single enemy spawnward the rim.
6. **Collision + score** — bullet kills enemy, enemy reaching the rim costs a life. Basic score counter.
1. **Angel plays the first frame** — opwser. Confirm: the well looks right, the
yellow ship follows the mouse around the rim, clicking fires down the lane. Report what feels off. (This is t
he human-green gate — nothing else proc
2. **One enemy** — a single enemy spawns at the far end and climbs a lane toward the rim.
3. **Collision + score** — bullet killshing the rim costs a life. Wire up the HU
D counter (already drawn, currently static).

## LATER (parked, not forgotten)


● Update(tig-tempest/WORKLIST.md)
Added 2 lines

## DONE (log — newest first)

- 2026-07-09 — Locked game feel: **classic tube/well** + **mouse control**. Recorded in `memory/project-tig-t
empest.md`.
- 2026-07-09 — First playable frame: `game/index.html` — receding 16-lane well, yellow ship rides the rim fol
lowing the mouse, click fires a project syntax verified. *Awaiting Angel's human
-green.*
- 2026-07-09 — Set up the context spine and the `memory/` folder.

Done — and this is the loop you'll live in evernded:

Recovered → and turned into real progress. Your permanent spine, and we already rowed threeworklist items past it.

What's on disk now:
- tig-tempest/CLAUDE.md, WORKLIST.md, memory/ —
- tig-tempest/game/index.html — a playable first frame: a 16-lane Tempest well receding into the screen, a yellow ship that
rides the rim following your mouse, click to fine

Your move — the human-green gate. Open it and ts session you can just type:

! xdg-open tig-tempest/game/index.html

(the ! runs it right here so the result lands i the file in your file manager.

Watch three things: does the well look right, de cleanly around the rim, does clicking firedown the lane. Tell me what's off — too fast, wrong colors, ship jumps, whatever — and I'll tune it. Nothing else on the
deck moves until you say this frame feels right

When you come back cold tomorrow, just say ON Dt and pick up exactly here. That's the wholepoint — you never re-explain again.

✻ Cogitated for 4m 35s

!  xdg-open tig-tempest/game/index.html
gio: file:///home/angel/repos/ground-control/game/index.html: Error when getting inform
ation for file “/home/angel/repos/ground-control/tig-tempest/game/tig-tempest/game/index.html”: No such file or dire
ctory

Ah — the shell's working directory is already i an earlier step), so the relative path doubledup. Use the absolute path instead:

  Listed 1 directory

Confirmed it's there. Type this (absolute path — works regardless of the shell's current directory):

! xdg-open /home/angel/repos/ground-control/tig-tempest/game/index.html

Then tell me how it plays.

✻ Worked for 8s

!  xdg-open /home/angel/repos/ground-control/tig-tempest/game/index.html
(Bash completed with no output)

That opened clean — no errors, so it should be is the human-green gate, so I'm not callinganything "done" until you tell me what you actually see.

Three checks:
1. The well — do you see a glowing cyan well masmall ring in the center?
2. The ship — as you move the mouse around, does the yellow claw hop from lane to lane along the rim, following you?
3. Firing — when you click, does a pink/magentawn toward the center and vanish?
                                                                                                                            Tell me what's right and what's off — too fast,colors, size, anything. That's what I'll tunenext.                                                                                                                       
✻ Brewed for 5s                                                                                                               
※ recap: We're building your Tempest-style arcade game and just put the first playable frame on screen. Next: open it in your browser and tell me if the well, mouse-controllt. (disable recaps in /config)
                                                                                                                             1. yes looks good 2. yes the mouse movement seerround and shoot from any lane to the middlecircle 3. firing looksand  good but no rapid fire i have to press one click for a few shots can not leave my finger on the mouse button but maybe that is corect . game isvery good first draft and skelton , i like itand brings back good vibes 4. Remember the game exactly and how it worked, but this looks generally like what it was if I recall it. It was kind of this shooting into th, it's very good. Let's keep going, um, and goon to the next steps. You actually tell me the rules of the game and how it works, the official one, so we can make it as
  close to the official game as possible?

Great result for a first frame — and that "briny the human-green signal I was waiting for. Letme answer your rapid-fire question, then lay out how the real game works so we can build toward it.

On rapid fire: what you're feeling is actually close to authentic. In the original you couldn't just hold and spray — there was a cap on how many shots could be on screen g had a natural rhythm. We can add hold-to-firewith a fire-rate limit + on-screen shot cap, which is the faithful version. I'll fold that into the enemy step.

How Tempest (Atari, 1981) actually works

The core loop you already built is the skeleton. Here's what makes it Tempest:

The field. A geometric well shown in perspective. You ride the rim in your claw-shaped "Blaster." Enemies emerge from the far (deep) end and climb the lanes toward you. ill them before they reach the rim.
                                                                                                                             The enemies — this is the heart of it:
- Flipper — the basic foe. Climbs toward you and flips sideways from lane to lane. If it reaches the rim, it can slide along the top and kill you on contact.
- Tanker — climbs, then splits into two Flippers (or Fuseballs/Pulsars in later levels) when shot or when it reaches the
top.
- Spiker — rides a lane spinning out a spike (a growing trail) that stays in the lane. Dangerous during the end-of-level
zoom.
- Fuseball — bounces up and down lanes and skates along the rim; only vulnerable at certain moments. Nasty on the top edge.
- Pulsar — periodically electrifies its whole lt lane when it pulses, you die.

Your tools:
- Fire down a lane (with the on-screen shot cap above).
- Superzapper — a smart-bomb that wipes the scrone weaker use per level — precious, notspammable.

Level flow. Clear the wave, then you zoom down through the tube to the next level. Any spikes the Spikers left will kill you
on the way down unless you've shot them off firbe's shape and color and speeds up. Lose a life when an enemy reaches you on the rim, a Pulsar zaps your lane, or you touch a Fuseball.

Scoring is per-enemy-type, with bonuses — Flippers cheap, Fuseballs/Pulsars worth more.

---
Proposed build order toward the real thing

Each step is one playable improvement you can h

1. Flipper enemy + collision + score + lives — s, flips lane-to-lane; your bolt kills it(+score); it reaching the rim costs a life. Wire the HUD. (This makes it an actual game.)
2. Hold-to-fire with shot cap — authentic firin
3. Superzapper — one screen-wipe per level, on a key.
4. Waves + level zoom — clear the wave, zoom do
5. Spiker + spikes — and the "shoot the spikes before you zoom" danger.
6. Tanker → split, then Fuseball and Pulsar — t
7. Title / attract screen, high scores, sound.

I'm saving the ruleset and this roadmap to files now so we never have to re-derive it, then — unless you want to reorder —
I'll start on step 1, the Flipper.

● Write(tig-tempest/memory/tempest-ruleset.md)
Wrote 26 lines to tig-tempest/memory/tempest-ruleset.md
---
name: tempest-ruleset
description: How the original Tempest (19nce we build toward; open when adding gam
type: reference
---

Design reference for how the arcade origiempest]] stays faithful. (Factual game me
chanics, from general knowledge of the 1981 Atari game.)
**Field:** Geometric well in perspective.aw "Blaster." Enemies emerge at the deep
(far) end and climb lanes toward the rim. Player shoots *down* lanes.
… +23 lines

● Update(tig-tempest/memory/MEMORY.md)
Added 1 line

- [Who Angel is](angel-who.md) — the captain's background; open when context about him matters
- [Project: Tempest-lineage arcade shoot what we're building and the fixed decisi
ons
- [Tempest ruleset](tempest-ruleset.md) ; open when adding gameplay to stay faith
ful

● Update(tig-tempest/WORKLIST.md)
Added 8 lines, removed 12 lines

---

## ON DECK (do these next, in order)
## ON DECK (build order toward the faithful game — see memory/tempest-ruleset.md)

1. **Angel plays the first frame** — open `game/index.html` in a browser. Confirm: the well looks right, the
yellow ship follows the mouse around the lane. Report what feels off. (This is t
he human-green gate — nothing else proceeds until this feels right.)
2. **One enemy** — a single enemy spawn lane toward the rim.
3. **Collision + score** — bullet kills enemy (score up), enemy reaching the rim costs a life. Wire up the HU
D counter (already drawn, currently sta
1. **Flipper + collision + score + lives** — Flipper spawns at the deep end, climbs, flips lane-to-lane; bolt
 kills it (+score); reaching the rim coly static) HUD. *(Makes it an actual game
.)*
2. **Hold-to-fire with shot cap** — autire on a rate limit, max handful of bolts
 on screen.
3. **Superzapper** — one screen-wipe pe
4. **Waves + level zoom** — clear the wave, zoom down the tube to a fresh (new-shape) level.
5. **Spiker + spikes** — spikes grow ine zoom unless shot off.
6. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
7. **Polish** — title/attract screen, h (Web Audio, no deps).

## LATER (parked, not forgotten)

- Multiple enemy types and waves.
- Sound (arcade blips — Web Audio API, still no dependencies).
- Level progression / increasing tube s
- Title screen + "INSERT COIN" attract mode.
- High-score table.

---

## DONE (log — newest first)

Files are current. Now — Rule 2, execute — buil enemy that turns this skeleton into an actualgame. It'll spawn at the deep end, climb the lanes flipping side to side, die to your bolt (+score), and cost you a life if
it reaches the rim. I'm rewriting index.html cl in fragile pieces:

● Write(tig-tempest/game/index.html)
Added 110 lines, removed 37 lines
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=de
<title>TIG · TEMPEST — first frame</title>
<title>TIG · TEMPEST — flippers</title>
<style>
  html, body { margin: 0; height: 100%;hidden; }
  body { display: flex; align-items: center; justify-content: center; cursor: crosshair; }
  canvas { display: block; }
  #hud {
    position: fixed; top: 14px; left: 1
    position: fixed; top: 14px; left: 16px; right: 16px;
    display: flex; justify-content: spa
    font: 14px/1.5 "Courier New", monospace; color: #22d3ee;
    letter-spacing: 2px; text-shadow: 0nts: none;
  }

</style>
</head>
<body>
<div id="hud">SCORE 000000</div>
<div id="hud"><span id="score">SCORE 000000</span><span id="lives">LIVES ♦ ♦ ♦</span></div>
<canvas id="game"></canvas>
<div id="hint">MOVE MOUSE — RIDE THE RIM · CLICK — FIRE DOWN THE LANE</div>
<div id="hint">MOVE MOUSE — RIDE THE RIERS BEFORE THEY REACH YOU</div>
<script>
(() => {
  "use strict";
  const canvas = document.getElementByI
  const ctx = canvas.getContext("2d");
  const hud = document.getElementById("
  const scoreEl = document.getElementById("score");
  const livesEl = document.getElementBy

  const LANES = 16;         // segments
  let cx = 0, cy = 0;       // centre / vanishing point

  resize();

  // --- geometry helpers -------------------------------------------------
  // depth d: 0 = rim (near, where theeep)
  const laneAngle = (i) => (i / LANES) * Math.PI * 2 - Math.PI / 2; // spoke i angle
  const laneMidAngle = (i) => laneAngl  // middle of lane i
  // point at depth d (0 = rim, 1 = far end) along the given angle
  function ptAt(angle, d) {
    const rad = R + (r - R) * d;
    return { x: cx + Math.cos(angle) * * rad };
  }
  const mod = (n, m) => ((n % m) + m)

  // --- state -------------------------------
  let playerLane = 0;       // which lane the ship sits on
  let playerLane = 0;
  let mouseAngle = -Math.PI / 2;
  const bullets = [];       // { lane,
  let bullets = [];         // { lane, d }   d grows 0 -> 1 (rim to deep)
  let enemies = [];         // flipperinks 1 -> 0 (deep to rim)
  let score = 0;
  let lives = 3;
  let gameOver = false;
  let spawnTimer = 60;

  const ENEMY_SPEED = 0.0032;   // cli
  const BULLET_SPEED = 0.02;
  const HIT_DEPTH = 0.06;       // depmy hit

  function reset() {
    bullets = []; enemies = []; score = 0; lives = 3;
    gameOver = false; spawnTimer = 60;
  }

  // --- input ------------------------------------------------------------
  window.addEventListener("mousemove",
    mouseAngle = Math.atan2(e.clientY - cy, e.clientX - cx);
  });
  window.addEventListener("mousedown", () => {
    if (gameOver) { reset(); return; }
    bullets.push({ lane: playerLane, d: 0 });
  });

  function nearestLane(angle) {
    let best = 0, bestDiff = Infinity;
    for (let i = 0; i < LANES; i++) {
      let diff = Math.abs(((laneMidAngle(i) - angle + Math.PI * 3) % (Math.PI * 2)) - Math.PI);
      const diff = Math.abs(mod(laneMiMath.PI * 2) - Math.PI);
      if (diff < bestDiff) { bestDiff = diff; best = i; }
    }
    return best;
  }

  function spawnFlipper() {
    enemies.push({ lane: Math.floor(Math.random() * LANES), d: 1, flipCd: 40 + Math.random() * 40 });
  }

  // --- draw --------------------------------
  function ring(d) {
    ctx.beginPath();
    for (let i = 0; i <= LANES; i++) {
      const p = ptAt(laneAngle(i % LAN
      i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    }
    ctx.closePath(); ctx.stroke();
  }

  function drawWell() {
    // spokes
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = "#1e3a8a";
    ctx.shadowColor = "#3b82f6"; ctx.s

      const o = ptAt(a, 0), inn = ptAt
      ctx.beginPath(); ctx.moveTo(o.x, o.y); ctx.lineTo(inn.x, inn.y); ctx.stroke();
    }
    // far ring
    ctx.strokeStyle = "#1e40af";
    ring(1);
    // rim ring
    ctx.strokeStyle = "#1e40af"; ring(1);
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#22d3ee";
    ctx.shadowColor = "#22d3ee"; ctx.s
    ring(0);
    ctx.strokeStyle = "#22d3ee"; ctx.shadowBlur = 12; ring(0);
    ctx.shadowBlur = 0;
  }
  function ring(d) {
    ctx.beginPath();
    for (let i = 0; i <= LANES; i++) {
      const p = ptAt(laneAngle(i % LAN
      i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
    }
    ctx.closePath(); ctx.stroke();
  }

  function drawPlayer() {
    const a0 = laneAngle(playerLane), a1 = laneAngle(playerLane + 1);
    const o0 = ptAt(a0, 0), o1 = ptAt(
    const i0 = ptAt(a0, 0.12), i1 = ptAt(a1, 0.12);
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#facc15";
    ctx.lineWidth = 3; ctx.strokeStyle
    ctx.shadowColor = "#facc15"; ctx.shadowBlur = 16;
    ctx.beginPath();
    ctx.moveTo(i0.x, i0.y); ctx.lineTo(o0.x, o0.y);
    ctx.lineTo(o1.x, o1.y); ctx.lineTo
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.stroke(); ctx.shadowBlur = 0;
  }

  function drawBullets() {
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#f0abfc";
    ctx.lineWidth = 3; ctx.strokeStyle = "#f0abfc";
    ctx.shadowColor = "#e879f9"; ctx.s
    for (const b of bullets) {
      const a = laneMidAngle(b.lane);

    ctx.shadowBlur = 0;
  }

  // --- loop -------------------------------------------------------------
  // flipper drawn as a spinning "bowt
  function drawEnemies() {
    ctx.lineWidth = 2.5; ctx.strokeSty
    ctx.shadowColor = "#f87171"; ctx.shadowBlur = 12;
    for (const e of enemies) {
      const a0 = laneAngle(e.lane), a1 = laneAngle(e.lane + 1);
      const w = 0.05;
      const near0 = ptAt(a0, Math.max(0, e.d - w)), near1 = ptAt(a1, Math.max(0, e.d - w));
      const far0 = ptAt(a0, Math.min(1Math.min(1, e.d + w));
      ctx.beginPath();
      ctx.moveTo(near0.x, near0.y); ct/ cross
      ctx.moveTo(near1.x, near1.y); ctx.lineTo(far0.x, far0.y);   // cross
      ctx.moveTo(near0.x, near0.y); ct/ rails
      ctx.moveTo(far0.x, far0.y);  ctx.lineTo(far1.x, far1.y);
      ctx.stroke();
    }
    ctx.shadowBlur = 0;
  }

  function drawGameOver() {
    ctx.fillStyle = "#000c"; ctx.fillRs.height);
    ctx.textAlign = "center"; ctx.fillStyle = "#22d3ee";
    ctx.shadowColor = "#22d3ee"; ctx.s
    ctx.font = "48px 'Courier New', monospace";
    ctx.fillText("GAME OVER", cx, cy -
    ctx.font = "18px 'Courier New', monospace"; ctx.fillStyle = "#94a3b8"; ctx.shadowBlur = 0;
    ctx.fillText("SCORE " + String(sco+ 30);
    ctx.fillText("CLICK TO INSERT COIN", cx, cy + 62);
  }

  // --- update ------------------------------
  function update() {
    playerLane = nearestLane(mouseAngl
    for (const b of bullets) b.d += 0.018;
    for (let i = bullets.length - 1; i>= 1) bullets.splice(i, 1);
    hud.textContent = "SCORE " + String(score).padStart(6, "0");
    if (gameOver) return;

    if (--spawnTimer <= 0) { spawnFlip.random() * 60; }

    for (const b of bullets) b.d += BU
    bullets = bullets.filter((b) => b.d < 1);

    for (const e of enemies) {
      e.d -= ENEMY_SPEED;
      if (--e.flipCd <= 0) {
        e.lane = mod(e.lane + (Math.ra);
        e.flipCd = 40 + Math.random() * 40;
      }
    }

    // bullet vs enemy (same lane, overlapping depth)
    for (const e of enemies) {
      for (const b of bullets) {
        if (b.lane === e.lane && Math.
          e.dead = true; b.d = 2; score += 150;
        }
      }
    }
    // enemy reached the rim -> costs a life
    for (const e of enemies) {
      if (e.d <= 0 && !e.dead) { e.dead = true; lives--; if (lives <= 0) gameOver = true; }
    }
    enemies = enemies.filter((e) => !e.dead);
    bullets = bullets.filter((b) => b.

    scoreEl.textContent = "SCORE " + S;
    livesEl.textContent = "LIVES " + (lives > 0 ? "♦ ".repeat(lives).trim() : "—");
  }

  function frame() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, c
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    update();
    drawWell();
    drawEnemies();
    drawBullets();
    drawPlayer();
    if (gameOver) drawGameOver();
    requestAnimationFrame(frame);
  }
  frame();

Now Rule 4 — syntax-check before you open it, s

  Ran 1 shell command

Clean — 202 lines, no errors. It's the same filowser tab (Ctrl+R) — no need to re-run the opencommand.

Here's what's new to test (the human-green gate for step 1):
- Red flipper bowties spawn deep in the well anlane to lane.
- Shoot one — your bolt hits it in its lane → it vanishes, SCORE jumps by 150.
- Let one reach the rim — you lose a life (top-
- Lose all 3 → GAME OVER screen; click to insert a coin and restart.

Let me log it while you play:

● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 1: **Flippers** — r climb & flip lane-to-lane; bolt kills th
em (+150); reaching the rim costs a life; 3 lives → GAME OVER + click-to-restart. HUD (score + lives) now liv
e. JS syntax verified. *Awaiting Angel'
- 2026-07-09 — Locked game feel: **classic tube/well** + **mouse control**. Recorded in `memory/project-tig-t
empest.md`.
- 2026-07-09 — First playable frame: `game/index.html` — receding 16-lane well, yellow ship rides the rim fol
lowing the mouse, click fires a project syntax verified. *Awaiting Angel's human
-green.*
- 2026-07-09 — Set up the context spine and the `memory/` folder.

Reload the tab and take it for a spin. Watch es— right now flippers spawn every ~1.5–2s, climbin ~5s, and flip randomly. Tell me:

- Too easy / too hard / about right?
- Do the red bowties read clearly as enemies ag
- Does shooting them feel satisfying, or do hits feel unreliable (that's the collision tolerance — easy to tune)?

Whatever's off, name it and I'll dial it in. When it feels right, we roll to step 2: hold-to-fire with the authentic shot
cap. And remember — cold start tomorrow, just sdeck and pick up right here.

✻ Worked for 3m 11s

※ recap: We're building a Tempest-style arcade ganow spawn, climb, and can be shot for score orcost a life. Reload the browser tab and tell me if the difficulty and hit feel are right, then we add hold-to-fire. (disable
  recaps in /config)

❯ it was good on difficulty no too hard and not t days and the bowties looked real just like iremember it was fun and shoot was satifify works really really well so far -- lets roll to step 2 now

Step 1 is officially human-green — "felt like the good old days" is exactly the target. Rolling to step 2: hold-to-fire with
the authentic shot cap.

The faithful behavior: hold the button to fire f clicking each time, but you can only have ahandful of bolts in the air at once — so you still can't just carpet a lane, you have to let shots clear. Let me wire it in.

● Update(tig-tempest/game/index.html)
Added 11 lines, removed 1 line
  let lives = 3;
  let gameOver = false;
  let spawnTimer = 60;
  let firing = false;           // mous
  let fireCd = 0;               // frames until next auto-shot

  const ENEMY_SPEED = 0.0032;   // climb per frame
  const BULLET_SPEED = 0.02;
  const HIT_DEPTH = 0.06;       // depth tolerance for a bullet/enemy hit
  const MAX_SHOTS = 8;          // authbolts on screen
  const FIRE_INTERVAL = 7;      // frames between auto-shots while held

  function reset() {
    bullets = []; enemies = []; score =
    gameOver = false; spawnTimer = 60;
    gameOver = false; spawnTimer = 60;
  }

  function tryFire() {
    if (bullets.length >= MAX_SHOTS) ret bolts clear
    bullets.push({ lane: playerLane, d: 0 });
    fireCd = FIRE_INTERVAL;
  }

  // --- input ------------------------------------------------------------
  window.addEventListener("mousemove",
    mouseAngle = Math.atan2(e.clientY - cy, e.clientX - cx);

● Update(tig-tempest/game/index.html)
Added 3 lines, removed 1 line
  });
  window.addEventListener("mousedown",
    if (gameOver) { reset(); return; }
    bullets.push({ lane: playerLane, d
    firing = true; fireCd = 0; tryFire();   // instant first shot, then auto-repeat
  });
  window.addEventListener("mouseup", () => { firing = false; });
  window.addEventListener("blur", () =

  function nearestLane(angle) {
    let best = 0, bestDiff = Infinity;

Now the auto-fire tick in the update loop:

● Update(tig-tempest/game/index.html)
Added 2 lines

    if (--spawnTimer <= 0) { spawnFlip.random() * 60; }

    if (firing && --fireCd <= 0) tryFid by cap + interval

    for (const b of bullets) b.d += BU
    bullets = bullets.filter((b) => b.d < 1);


Syntax-check, then it's yours to test:

  Ran 1 shell command

Clean — 216 lines, no errors. Reload the tab (C

- Hold the mouse button — bolts now stream out f one-per-click.
- Hold on a single lane — you'll hit a ceiling of 8 bolts on screen; firing pauses until some reach the center and clear,
then resumes. That's the authentic constraint —
- A single click should still fire exactly one shot, same as before.

What to feel for:
- Fire rate — right now ~1 shot per 7 frames (ro slow, or right?
- Shot cap of 8 — does it feel like a fair limit, or too stingy / too generous?

Both are one-number tweaks, so just tell me the vibe. Logging it now:

● Update(tig-tempest/WORKLIST.md)
Added 1 line, removed 3 lines

## ON DECK (build order toward the faitt-ruleset.md)

1. **Flipper + collision + score + liveeep end, climbs, flips lane-to-lane; bolt
 kills it (+score); reaching the rim costs a life. Wire the (currently static) HUD. *(Makes it an actual game
.)*
2. **Hold-to-fire with shot cap** — authentic firing feel: hold to fire on a rate limit, max handful of bolts
 on screen.
3. **Superzapper** — one screen-wipe per level on a key.
1. **Superzapper** — one screen-wipe pe
4. **Waves + level zoom** — clear the wave, zoom down the tube to a fresh (new-shape) level.
5. **Spiker + spikes** — spikes grow ine zoom unless shot off.
6. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.

Let me fix the deck numbering and log step 2 as done:

  Read 1 file

● Update(tig-tempest/WORKLIST.md)
Added 6 lines, removed 6 lines

## ON DECK (build order toward the faitt-ruleset.md)

1. **Superzapper** — one screen-wipe pe
4. **Waves + level zoom** — clear the wave, zoom down the tube to a fresh (new-shape) level.
5. **Spiker + spikes** — spikes grow ine zoom unless shot off.
6. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
7. **Polish** — title/attract screen, h (Web Audio, no deps).
1. **Waves + level zoom** — clear the wave, zoom down the tube to a fresh (new-shape) level.
2. **Spiker + spikes** — spikes grow ine zoom unless shot off.
3. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
4. **Polish** — title/attract screen, h (Web Audio, no deps).

---

## DONE (log — newest first)

- 2026-07-09 — Step 1: **Flippers** — r climb & flip lane-to-lane; bolt kills th
em (+150); reaching the rim costs a life; 3 lives → GAME OVER + click-to-restart. HUD (score + lives) now liv
e. JS syntax verified. *Awaiting Angel'
- 2026-07-09 — Step 2: **Hold-to-fire** on a 7-frame cadence with an authentic **8-bolt on-screen cap**; sing
le click still fires one. JS syntax vern-green.*
- 2026-07-09 — Step 1: **Flippers** — red bowtie enemies spawn deep, climb & flip lane-to-lane; bolt kills th
em (+150); reaching the rim costs a lifk-to-restart. HUD (score + lives) now liv
e. Angel human-green ✓ ("felt like the good old days").
- 2026-07-09 — Locked game feel: **clastrol**. Recorded in `memory/project-tig-t
empest.md`.
- 2026-07-09 — First playable frame: `g-lane well, yellow ship rides the rim fol
lowing the mouse, click fires a projectile down the current lane. JS syntax verified. *Awaiting Angel's human
-green.*
- 2026-07-09 — Set up the context spine: `CLAUDE.md`, this worklist, and the `memory/` folder.

Deck's updated and step 2 is logged. Reload and give the new firing a run — tell me if the cadence and the 8-shot cap feel
right, or hand me a number to tweak.

When you're happy, step 3 is the Superzapper — ton that wipes the screen. Just say go (or ONDECK if you're picking this up fresh later).

✻ Churned for 1m 21s

※ recap: We're building a Tempest-style arcade shooter in tig-tempest/. Steps 1 and 2 (flippers, hold-to-fire) are done and
  awaiting your play-test. Next: reload the tab, t, then we start step 3, the Superzapper.(disable recaps in /config)

❯ /rename tempest-GAME-session
  ⎿  Session renamed to: tempest-GAME-session

❯ /color pink
  ⎿  Session color set to: pink

❯ step 3 super zapper but the last check was excellent but almost too easy with the rapid fire feature but i love the feel
  and it feel good to be playing tempest again an

Two things in that message, and I'm acting on bd your note that rapid-fire made it almost tooeasy. Since the auto-fire tilted the balance your way, I'll nudge enemy pressure up a touch at the same time — so the win
still feels earned. And "winning at Tempest aga doing this, so I won't over-correct.

Let me wire in the Superzapper — your SPACE-barscreen, precious and limited — plus a modestdifficulty bump.

● Update(tig-tempest/game/index.html)
Added 2 lines, removed 2 lines
</style>
</head>
<body>
<div id="hud"><span id="score">SCORE 00IVES ♦ ♦ ♦</span></div>
<div id="hud"><span id="score">SCORE 000000</span><span id="zap">ZAP ×2</span><span id="lives">LIVES ♦ ♦ ♦</s
pan></div>
<canvas id="game"></canvas>
<div id="hint">MOVE MOUSE — RIDE THE RIERS BEFORE THEY REACH YOU</div>
<div id="hint">MOVE MOUSE — RIDE THE RIM · CLICK/HOLD — FIRE · SPACE — SUPERZAPPER</div>
<script>
(() => {
  "use strict";

● Update(tig-tempest/game/index.html)
Added 1 line
  const canvas = document.getElementByI
  const ctx = canvas.getContext("2d");
  const scoreEl = document.getElementBy
  const zapEl = document.getElementById("zap");
  const livesEl = document.getElementBy

  const LANES = 16;         // segments

● Update(tig-tempest/game/index.html)
Added 12 lines, removed 1 line
  let spawnTimer = 60;
  let firing = false;           // mouse button held?
  let fireCd = 0;               // fram
  let zaps = 2;                 // superzappers left
  let zapFlash = 0;             // whit

  const ENEMY_SPEED = 0.0032;   // clim
  const ENEMY_SPEED = 0.0040;   // climb per frame (bumped up vs rapid-fire)
  const BULLET_SPEED = 0.02;
  const HIT_DEPTH = 0.06;       // depth tolerance for a bullet/enemy hit
  const MAX_SHOTS = 8;          // authbolts on screen
  const FIRE_INTERVAL = 7;      // frames between auto-shots while held
  const START_ZAPS = 2;         // supeonce waves land)

  function reset() {
    bullets = []; enemies = []; score = 0; lives = 3;
    gameOver = false; spawnTimer = 60;
    zaps = START_ZAPS; zapFlash = 0;
  }

  function tryFire() {

    fireCd = FIRE_INTERVAL;
  }

  function superzap() {
    if (zaps <= 0 || !enemies.length) waste on an empty screen
    zaps--;
    enemies = [];                     limbing the well
    zapFlash = 14;
  }

  // --- input -------------------------------
  window.addEventListener("mousemove", (e) => {
    mouseAngle = Math.atan2(e.clientY

Now the SPACE keydown handler and the difficult

● Update(tig-tempest/game/index.html)
Added 7 lines
  });
  window.addEventListener("mouseup", () => { firing = false; });
  window.addEventListener("blur", () =
  window.addEventListener("keydown", (e) => {
    if (e.code === "Space") {
      e.preventDefault();
      if (gameOver) { reset(); return;
      superzap();
    }
  });

  function nearestLane(angle) {
    let best = 0, bestDiff = Infinity;

● Update(tig-tempest/game/index.html)
Added 1 line, removed 1 line
    playerLane = nearestLane(mouseAngl
    if (gameOver) return;

    if (--spawnTimer <= 0) { spawnFlipper(); spawnTimer = 90 + Math.random() * 60; }
    if (--spawnTimer <= 0) { spawnFlip.random() * 45; }

    if (firing && --fireCd <= 0) tryFid by cap + interval


Now the HUD zap readout and the zap-flash overlay:

● Update(tig-tempest/game/index.html)
Added 1 line
    bullets = bullets.filter((b) => b.d < 1);

    scoreEl.textContent = "SCORE " + String(score).padStart(6, "0");
    zapEl.textContent = "ZAP " + (zaps
    livesEl.textContent = "LIVES " + (lives > 0 ? "♦ ".repeat(lives).trim() : "—");
  }


● Update(tig-tempest/game/index.html)
Added 5 lines
    drawEnemies();
    drawBullets();
    drawPlayer();
    if (zapFlash > 0) {
      ctx.fillStyle = "rgba(255,255,255," + (zapFlash / 14 * 0.6).toFixed(3) + ")";
      ctx.fillRect(0, 0, canvas.width,
      zapFlash--;
    }
    if (gameOver) drawGameOver();
    requestAnimationFrame(frame);
  }

  Ran 1 shell command

Clean — 241 lines, no errors. Reload (Ctrl+R) and try step 3 plus the rebalance:

Superzapper:
- New ZAP ×2 readout in the HUD (top center).
- Press SPACE with enemies on screen → the whole well flashes white and every climbing flipper is wiped. Counter drops to
×1, then ×2 → — when spent.
- It won't fire on an empty screen (so you can't waste it), and it's only 2 per game for now — that becomes per-level once
we build waves, which is the authentic version.

Difficulty nudge (to offset rapid-fire):
- Flippers now spawn a bit more often and climb a little faster. Should restore some bite without breaking the "winning
feels good" vibe.

Feel for two things: does the zapper feel like ash strong enough? too strong?), and is the newpace back to "earned win" territory or did I overshoot? Both are one-number tweaks.

Logging it:

● Update(tig-tempest/WORKLIST.md)
Added 2 lines, removed 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 2: **Hold-to-fire** authentic **8-bolt on-screen cap**; sing
le click still fires one. JS syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 3: **Superzapper** lippers, white flash, 2 per game (→ per-l
evel once waves land), HUD "ZAP ×n". Plus difficulty rebalance to offset rapid-fire: faster spawns (65–110f)
+ climb (0.0040). JS syntax verified. **
- 2026-07-09 — Step 2: **Hold-to-fire** on a 7-frame cadence with an authentic **8-bolt on-screen cap**; sing
le click still fires one. Angel human-gtoo easy" → difficulty bumped in step 3).
- 2026-07-09 — Step 1: **Flippers** — red bowtie enemies spawn deep, climb & flip lane-to-lane; bolt kills th
em (+150); reaching the rim costs a lifk-to-restart. HUD (score + lives) now liv
e. Angel human-green ✓ ("felt like the good old days").
- 2026-07-09 — Locked game feel: **clastrol**. Recorded in `memory/project-tig-t
empest.md`.
- 2026-07-09 — First playable frame: `g-lane well, yellow ship rides the rim fol
lowing the mouse, click fires a projectile down the current lane. JS syntax verified. *Awaiting Angel's human
-green.*

Deck's updated, step 3 logged. Reload and put t me if the flash and the new pace feel right, or hand me a number to dial.

Next on the deck when you're ready is step 4: waves + the level zoom — clear the screen, then dive down the tube to a
fresh-shaped well. That's also where the Superzic per-level refill. Say go, or ON DECK to pickthis up cold later.

✻ Sautéed for 2m 4s

❯ go, step 4 waves and level zoom

On it — step 4: waves + the level zoom. This is the one that turns "endless survival" into an actual Tempest campaign: each
level is a finite wave, clear it and you dive d-colored well, difficulty ramps, and theSuperzapper refills to its authentic per-level charge. Several edits coming.

First, the new state and constants:

● Update(tig-tempest/game/index.html)
Added 4 lines
  let fireCd = 0;               // frames until next auto-shot
  let zaps = 2;                 // supe
  let zapFlash = 0;             // white-flash frames after a zap
  let level = 1;                // curr
  let toSpawn = 0;              // flippers left to spawn this wave
  let zooming = false;          // divils?
  let zoomT = 0;                // zoom progress 0 -> 1

  const ENEMY_SPEED = 0.0040;   // climb per frame (bumped up vs rapid-fire)
  const BULLET_SPEED = 0.02;

● Update(tig-tempest/game/index.html)
Added 3 lines, removed 1 line
  const HIT_DEPTH = 0.06;       // depty hit
  const MAX_SHOTS = 8;          // authentic cap: only a handful of bolts on screen
  const FIRE_INTERVAL = 7;      // frameld
  const START_ZAPS = 2;         // superzappers per game (per-level once waves land)
  const START_ZAPS = 2;         // supe of each level
  const ZOOM_FRAMES = 75;       // length of the between-level tube dive
  const WAVE_SIZE = (lvl) => 5 + lvl * for a level

  function reset() {
    bullets = []; enemies = []; score = 0; lives = 3;

Now rewrite reset() and add the level-flow functions (wave setup, zoom start/finish, tube color, and the zoom draw):

● Update(tig-tempest/game/index.html)
Added 26 lines, removed 3 lines
  const WAVE_SIZE = (lvl) => 5 + lvl * 2;   // flippers in the wave for a level

  function reset() {
    bullets = []; enemies = []; score
    gameOver = false; spawnTimer = 60; firing = false; fireCd = 0;
    zaps = START_ZAPS; zapFlash = 0;
    score = 0; lives = 3; gameOver = false; firing = false; fireCd = 0;
    zapFlash = 0; level = 1; zooming =
    startWave();
  }

  // begin the wave for the current `l
  function startWave() {
    bullets = []; enemies = [];
    toSpawn = WAVE_SIZE(level);
    spawnTimer = 45;
    zaps = START_ZAPS;            // per-level refill — authentic
  }

  function startZoom() {
    zooming = true; zoomT = 0; firing = false; bullets = [];
    level++;                      // dhe dive
  }

  function finishZoom() {
    zooming = false;
    startWave();
  }

  // tube hue shifts each level (startlts stay distinct
  function tubeColor(light) {
    return "hsl(" + ((190 + (level - 1light + "%)";
  }

  function tryFire() {
    if (bullets.length >= MAX_SHOTS) ret bolts clear
    bullets.push({ lane: playerLane, d: 0 });

Now the rim color in drawWell uses the per-level hue:

● Update(tig-tempest/game/index.html)
Added 20 lines, removed 1 line
    }
    ctx.strokeStyle = "#1e40af"; ring(
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = "#22d3ee"; ctx.shadowBlur = 12; ring(0);
    ctx.strokeStyle = tubeColor(60); ctx.shadowColor = tubeColor(60); ctx.shadowBlur = 12; ring(0);
    ctx.shadowBlur = 0;
  }

  // between-level tube dive: rings rush outward from the centre past the rim
  function drawZoom(t) {
    const COUNT = 16;
    ctx.lineWidth = 2;
    for (let k = 0; k < COUNT; k++) {
      const d = 1 - (((t * 1.6 + k / Cr) -> -0.4 (past rim)
      const intensity = Math.max(0.08, 1 - Math.abs(d) * 0.7);
      ctx.strokeStyle = "hsla(" + ((19+ ", 85%, 60%, " + intensity.toFixed(3) +
 ")";
      ctx.shadowColor = tubeColor(60);
      ring(d);
    }
    ctx.shadowBlur = 0;
    ctx.textAlign = "center"; ctx.fill
    ctx.font = "28px 'Courier New', monospace";
    ctx.shadowColor = tubeColor(60); c
    ctx.fillText("LEVEL " + level, cx, cy);
    ctx.shadowBlur = 0;
  }

  function drawPlayer() {
    const a0 = laneAngle(playerLane), );
    const o0 = ptAt(a0, 0), o1 = ptAt(a1, 0);

Now the core: rewrite update() for wave-based spawning, zoom handling, and level-scaled difficulty:

● Update(tig-tempest/game/index.html)
Added 22 lines, removed 8 lines
  }

  // --- update -----------------------------------------------------------
  function updateHud() {
    scoreEl.textContent = "LVL " + level + "  SCORE " + String(score).padStart(6, "0");
    zapEl.textContent = "ZAP " + (zaps
    livesEl.textContent = "LIVES " + (lives > 0 ? "♦ ".repeat(lives).trim() : "—");
  }

  function update() {
    playerLane = nearestLane(mouseAngle);
    updateHud();
    if (gameOver) return;

    if (--spawnTimer <= 0) { spawnFlipper(); spawnTimer = 65 + Math.random() * 45; }
    if (zooming) {                    he next level
      zoomT += 1 / ZOOM_FRAMES;
      if (zoomT >= 1) finishZoom();
      return;
    }

    if (firing && --fireCd <= 0) tryFid by cap + interval
    if (toSpawn > 0 && --spawnTimer <= 0) {          // feed the wave
      spawnFlipper(); toSpawn--;
      spawnTimer = Math.max(24, 60 - level * 3) + Math.random() * 35;
    }

    for (const b of bullets) b.d += BU
    bullets = bullets.filter((b) => b.d < 1);
    if (firing && --fireCd <= 0) tryFie, gated by cap + interval

    const climb = ENEMY_SPEED * (1 + (er each level
    for (const b of bullets) b.d += BULLET_SPEED;
    for (const e of enemies) {
      e.d -= ENEMY_SPEED;
      e.d -= climb;
      if (--e.flipCd <= 0) {
        e.lane = mod(e.lane + (Math.ra);
        e.flipCd = 40 + Math.random() * 40;

    enemies = enemies.filter((e) => !e.dead);
    bullets = bullets.filter((b) => b.

    scoreEl.textContent = "SCORE " + S;
    zapEl.textContent = "ZAP " + (zaps > 0 ? "×" + zaps : "—");
    livesEl.textContent = "LIVES " + ().trim() : "—");
    // wave cleared (all spawned, none left) -> dive to the next level
    if (!gameOver && toSpawn <= 0 && em();
  }

  function frame() {

Finally, frame() draws the tunnel dive during the zoom instead of the normal well:

● Update(tig-tempest/game/index.html)
Added 8 lines, removed 4 lines
  function frame() {
    ctx.fillStyle = "#000"; ctx.fillRe.height);
    update();
    drawWell();
    drawEnemies();
    drawBullets();
    drawPlayer();
    if (zooming) {
      drawZoom(zoomT);
    } else {
      drawWell();
      drawEnemies();
      drawBullets();
      drawPlayer();
    }
    if (zapFlash > 0) {
      ctx.fillStyle = "rgba(255,255,255," + (zapFlash / 14 * 0.6).toFixed(3) + ")";
      ctx.fillRect(0, 0, canvas.width,

  Ran 1 shell command

Clean — 307 lines, no errors. Reload (Ctrl+R) ahis is the biggest jump yet:

The campaign loop:
- The HUD now shows LVL 1 next to your score. Each level is a finite wave of flippers (7 on level 1, growing each level).
- Clear the wave → you dive: rings rush outwardshes, and you arrive in a fresh well in a newcolor.
- Each level, flippers spawn faster and climb fefills to ×2 — the authentic per-level charge.
- Lose all 3 lives → GAME OVER, click to insert a coin (back to level 1).

What to feel for:
- Does the zoom/dive read as "flying down the tonger/punchier?
- Is the difficulty ramp per level too steep, too gentle, or nicely escalating?
- Does clearing a wave feel like a satisfying bt dive?

All tunable numbers. Logging step 4:

● Update(tig-tempest/WORKLIST.md)
Added 3 lines, removed 4 lines

## ON DECK (build order toward the faithful game — see memory/tempest-ruleset.md)

1. **Waves + level zoom** — clear the wave, zoom down the tube to a fresh (new-shape) level.
2. **Spiker + spikes** — spikes grow ine zoom unless shot off.
3. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
4. **Polish** — title/attract screen, h (Web Audio, no deps).
1. **Spiker + spikes** — spikes grow in lanes and kill you during the zoom unless shot off. (Ties directly in
to the zoom we just built.)
2. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
3. **Polish** — title/attract screen, h (Web Audio, no deps).

---


● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 4: **Waves + level 2 flippers), clear → tunnel-dive transiti
on ("LEVEL n") → fresh well in a per-level hue. Per-level difficulty ramp (spawn + climb speed) and Superzapp
er refill. HUD shows LVL. JS syntax vern-green.*
- 2026-07-09 — Step 3: **Superzapper** — SPACE wipes all on-screen flippers, white flash, 2 per game (→ per-l
evel once waves land), HUD "ZAP ×n". Plfset rapid-fire: faster spawns (65–110f)
+ climb (0.0040). JS syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 2: **Hold-to-fire** authentic **8-bolt on-screen cap**; sing
le click still fires one. Angel human-green ✓ ("excellent... almost too easy" → difficulty bumped in step 3).
- 2026-07-09 — Step 1: **Flippers** — r climb & flip lane-to-lane; bolt kills th
em (+150); reaching the rim costs a life; 3 lives → GAME OVER + click-to-restart. HUD (score + lives) now liv
e. Angel human-green ✓ ("felt like the

Deck's updated, step 4 logged. Give it a real pels deep you can get and whether the ramp keepspulling you in.

When you surface, tell me how the dive and the difficulty curve feel, and I'll tune. Next on the deck is step 5: the Spiker
— the enemy that leaves lethal spikes in the lao the zoom you just got (shoot the spikes downbefore you dive, or they cost you). Say go, or ON DECK to pick this up cold later.

✻ Churned for 3m 12s

※ recap: We're building your browser-based Tempest game in tig-tempest/, and just finished step 4 (waves plus the
  between-level tube dive). Reload the game and pe how the dive and difficulty ramp feel so I can tune before starting step 5, the Spiker.

❯ go, step 5 the spiker and i check the levels made it to level 4 and got killed game over so difficulty is bang on just
  bowties on all leveles and the super zapper seemoved to next level would be nice if not sofdast give me a second to breath but its bang on tigs

Level 4 with just bowties and the ramp landing "bang on" — that's a great sign. Two things in your message, both going in:

1. Give you a second to breathe — I'll lengthen the dive and add a short STAND BY breather after each wave clears (which
also gives you time to slide to a safe lane — r
2. Step 5: the Spiker — the enemy that rides a lane laying down a lethal spike; if you dive out with a tall spike on your
lane, it costs you. So you shoot spikes down beight into that breather.

Several edits. First, new state:

● Update(tig-tempest/game/index.html)
Added 4 lines, removed 1 line
  let zaps = 2;                 // supe
  let zapFlash = 0;             // white-flash frames after a zap
  let level = 1;                // curr
  let toSpawn = 0;              // flippers left to spawn this wave
  let toSpawn = 0;              // enem
  let zooming = false;          // diving down the tube between levels?
  let zoomT = 0;                // zoom
  let spikes = [];              // per-lane spike tip depth (1 = none, smaller = taller)
  let clearHold = 0;            // "STAa wave clears
  let hurtFlash = 0;            // red flash frames when the player takes a hit

  const ENEMY_SPEED = 0.0040;   // climb per frame (bumped up vs rapid-fire)
  const BULLET_SPEED = 0.02;

Constants — longer dive, breather, and spike tu

● Update(tig-tempest/game/index.html)
Added 5 lines, removed 2 lines
  const MAX_SHOTS = 8;          // authbolts on screen
  const FIRE_INTERVAL = 7;      // frames between auto-shots while held
  const START_ZAPS = 2;         // supe of each level
  const ZOOM_FRAMES = 75;       // length of the between-level tube dive
  const WAVE_SIZE = (lvl) => 5 + lvl * for a level
  const ZOOM_FRAMES = 110;      // length of the between-level tube dive (longer = calmer)
  const CLEAR_HOLD = 75;        // "STAclears
  const WAVE_SIZE = (lvl) => 5 + lvl * 2;   // enemies in the wave for a level
  const SPIKE_ERODE = 0.09;     // how  knocks back
  const SPIKE_DANGER = 0.45;    // spike tip below this depth is lethal on the dive

  function reset() {
    score = 0; lives = 3; gameOver = fa 0;

Now wire spikes into reset, startWave, and add tZoom:

● Update(tig-tempest/game/index.html)
Added 10 lines, removed 3 lines

  function reset() {
    score = 0; lives = 3; gameOver = f= 0;
    zapFlash = 0; level = 1; zooming = false; zoomT = 0;
    zapFlash = 0; hurtFlash = 0; level= 0;
    startWave();
  }

  // begin the wave for the current `l
  function startWave() {
    bullets = []; enemies = [];
    spikes = new Array(LANES).fill(1);   // fresh tube, no spikes
    clearHold = 0;
    toSpawn = WAVE_SIZE(level);
    spawnTimer = 45;
    zaps = START_ZAPS;            // per-level refill — authentic
    spawnTimer = 70;                   enemy
    zaps = START_ZAPS;                   // per-level refill — authentic
  }

  function startZoom() {
    // crashing into a tall spike on your lane costs a life
    if (spikes[playerLane] < SPIKE_DAN
      lives--; hurtFlash = 12;
      if (lives <= 0) { gameOver = tru
    }
    zooming = true; zoomT = 0; firing
    level++;                      // display the new level during the dive
  }

Now the spawn function grows a Spiker variant (

● Update(tig-tempest/game/index.html)
Added 8 lines, removed 2 lines
    return best;
  }

  function spawnFlipper() {
    enemies.push({ lane: Math.floor(MalipCd: 40 + Math.random() * 40 });
  function spawnEnemy() {
    const spiker = level >= 2 && Math.kers from level 2
    enemies.push({
      type: spiker ? "spiker" : "flipp
      lane: Math.floor(Math.random() * LANES),
      d: 1,
      flipCd: 40 + Math.random() * 40,
    });
  }

  // --- draw -------------------------------------------------------------

Now the heart of it — rewriting update() for the breather, spiker movement/spike-laying, and spike erosion, plus two small
helpers:

● Update(tig-tempest/game/index.html)
Added 35 lines, removed 9 lines
    livesEl.textContent = "LIVES " + ().trim() : "—");
  }

  function fireAndMoveBullets() {
    if (firing && --fireCd <= 0) tryFie, gated by cap + interval
    for (const b of bullets) b.d += BULLET_SPEED;
  }

  // bolts travelling down a lane knoc
  function erodeSpikes() {
    for (const b of bullets) {
      if (b.d > 1) continue;
      const top = spikes[b.lane];
      if (top < 1 && b.d >= top) { spikes[b.lane] = Math.min(1, top + SPIKE_ERODE); b.d = 2; }
    }
  }

  function update() {
    playerLane = nearestLane(mouseAngl
    updateHud();

      return;
    }

    if (clearHold > 0) {              eather: move + shoot spikes
      fireAndMoveBullets();
      erodeSpikes();
      bullets = bullets.filter((b) => b.d < 1);
      if (--clearHold <= 0) startZoom(
      return;
    }

    if (toSpawn > 0 && --spawnTimer <=ve
      spawnFlipper(); toSpawn--;
      spawnEnemy(); toSpawn--;
      spawnTimer = Math.max(24, 60 - level * 3) + Math.random() * 35;
    }

    if (firing && --fireCd <= 0) tryFie, gated by cap + interval
    fireAndMoveBullets();

    const climb = ENEMY_SPEED * (1 + (level - 1) * 0.12);   // faster each level
    for (const b of bullets) b.d += BU
    for (const e of enemies) {
      e.d -= climb;
      if (--e.flipCd <= 0) {
      const sp = e.type === "spiker" ?kers a touch slower
      e.d -= climb * sp;
      if (e.type === "spiker") {
        spikes[e.lane] = Math.min(spikes[e.lane], e.d);      // extend spike behind it
      } else if (--e.flipCd <= 0) {
        e.lane = mod(e.lane + (Math.random() < 0.5 ? -1 : 1), LANES);
        e.flipCd = 40 + Math.random()
      }

    // bullet vs enemy (same lane, overlapping depth)
    for (const e of enemies) {
      for (const b of bullets) {
        if (b.lane === e.lane && Math.
          e.dead = true; b.d = 2; score += 150;
        if (!e.dead && b.d <= 1 && b.ld - e.d) < HIT_DEPTH) {
          e.dead = true; b.d = 2; score += e.type === "spiker" ? 200 : 150;
        }
      }
    }

    for (const e of enemies) {
      if (e.d <= 0 && !e.dead) { e.dead = true; lives--; if (lives <= 0) gameOver = true; }
    }

    erodeSpikes();
    enemies = enemies.filter((e) => !e.dead);
    bullets = bullets.filter((b) => b.

    // wave cleared (all spawned, nonevel
    if (!gameOver && toSpawn <= 0 && enemies.length === 0) startZoom();
    // wave cleared (all spawned, none
    if (!gameOver && toSpawn <= 0 && enemies.length === 0) clearHold = CLEAR_HOLD;
  }

  function frame() {

Now the visuals — Spikers get their own look, sther shows a prompt. Rewriting drawEnemies tobranch by type and adding the spike/stand-by draws:

● Update(tig-tempest/game/index.html)
Added 52 lines, removed 13 lines
    ctx.shadowBlur = 0;
  }

  // flipper drawn as a spinning "bowt
  function drawEnemies() {
    ctx.lineWidth = 2.5; ctx.strokeSty
    ctx.shadowColor = "#f87171"; ctx.shadowBlur = 12;
    for (const e of enemies) {
      const a0 = laneAngle(e.lane), a1 = laneAngle(e.lane + 1);
      const w = 0.05;
      const near0 = ptAt(a0, Math.max(0, e.d - w)), near1 = ptAt(a1, Math.max(0, e.d - w));
      const far0 = ptAt(a0, Math.min(1Math.min(1, e.d + w));
  // green zig-zag spikes growing up the lanes from the deep end
  function drawSpikes() {
    ctx.lineWidth = 2; ctx.strokeStyle = "#a3e635";
    ctx.shadowColor = "#84cc16"; ctx.s
    for (let i = 0; i < LANES; i++) {
      const top = spikes[i];
      if (top >= 1) continue;                       // no spike here
      const a = laneMidAngle(i), tip =
      ctx.beginPath();
      ctx.moveTo(near0.x, near0.y); ct/ cross
      ctx.moveTo(near1.x, near1.y); ctx.lineTo(far0.x, far0.y);   // cross
      ctx.moveTo(near0.x, near0.y); ct/ rails
      ctx.moveTo(far0.x, far0.y);  ctx.lineTo(far1.x, far1.y);
      for (let s = 0; s <= steps; s++)
        const d = 1 + (tip - 1) * (s / steps);
        const p = ptAt(a + (s % 2 ? 0.
        s === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y);
      }
      ctx.stroke();
    }
    ctx.shadowBlur = 0;
  }

  function drawEnemies() {
    for (const e of enemies) {
      const a0 = laneAngle(e.lane), a1 0.05;
      if (e.type === "spiker") {
        // bright green diamond
        const top = ptAt(laneMidAngle(e.lane), Math.max(0, e.d - w));
        const bot = ptAt(laneMidAngle();
        const lft = ptAt(a0, e.d), rgt = ptAt(a1, e.d);
        ctx.fillStyle = "#4ade80"; ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.moveTo(top.x, top.y); ctx.
        ctx.lineTo(bot.x, bot.y); ctx.lineTo(lft.x, lft.y); ctx.closePath();
        ctx.fill(); ctx.shadowBlur = 0
      } else {
        // red flipper "bowtie" spanni
        const near0 = ptAt(a0, Math.max(0, e.d - w)), near1 = ptAt(a1, Math.max(0, e.d - w));
        const far0 = ptAt(a0, Math.min, Math.min(1, e.d + w));
        ctx.lineWidth = 2.5; ctx.strokeStyle = "#ef4444";
        ctx.shadowColor = "#f87171"; c
        ctx.beginPath();
        ctx.moveTo(near0.x, near0.y);
        ctx.moveTo(near1.x, near1.y); ctx.lineTo(far0.x, far0.y);
        ctx.moveTo(near0.x, near0.y);
        ctx.moveTo(far0.x, far0.y);  ctx.lineTo(far1.x, far1.y);
        ctx.stroke(); ctx.shadowBlur =
      }
    }
  }

  function drawStandBy() {
    ctx.textAlign = "center"; ctx.fill
    ctx.font = "20px 'Courier New', monospace";
    ctx.shadowColor = tubeColor(60); c
    ctx.fillText("STAND BY", cx, cy - R * 0.62);
    ctx.font = "13px 'Courier New', mo3e635";
    ctx.fillText("SHOOT ANY SPIKES ON YOUR LANE", cx, cy - R * 0.62 + 22);
    ctx.shadowBlur = 0;
  }

  function drawGameOver() {
    ctx.fillStyle = "#000c"; ctx.fillRs.height);
    ctx.textAlign = "center"; ctx.fillStyle = "#22d3ee";

Now render spikes, the stand-by prompt, and the red hurt flash in frame():

● Update(tig-tempest/game/index.html)
Added 7 lines
      drawZoom(zoomT);
    } else {
      drawWell();
      drawSpikes();
      drawEnemies();
      drawBullets();
      drawPlayer();
      if (clearHold > 0) drawStandBy()
    }
    if (zapFlash > 0) {
      ctx.fillStyle = "rgba(255,255,255," + (zapFlash / 14 * 0.6).toFixed(3) + ")";
      ctx.fillRect(0, 0, canvas.width,
      zapFlash--;
    }
    if (hurtFlash > 0) {
      ctx.fillStyle = "rgba(255,40,40,Fixed(3) + ")";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      hurtFlash--;
    }
    if (gameOver) drawGameOver();
    requestAnimationFrame(frame);
  }

  Ran 1 shell command

Clean — 398 lines, no errors. Reload (Ctrl+R) a

The breather (your "second to breathe"):
- The dive is now noticeably longer/calmer, and after you clear a wave you get a STAND BY pause before it starts — a beat to
reposition.

The Spiker (step 5):
- From level 2, ~30% of the wave are green diamonds instead of red bowties. They ride a single lane and leave a green
zig-zag spike growing up behind them.
- Shoot spikes down — fire into a spiked lane and each bolt knocks the spike back. During the STAND BY breather it even
prompts you: "shoot any spikes on your lane."
- The catch: if you dive out with a tall spike on your current lane, you crash into it — screen flashes red, you lose a
life. So either clear your lane's spike or sliddive.
- Spikers are worth 200 (vs. 150 for flippers) and move a touch slower.

What to feel for:
- Do the green spikes read clearly against the lippers?
- Is the spike danger fair — enough warning + time to shoot them or dodge — or does it feel like a cheap death?
- Does the STAND BY breather land at the right

Logging step 5:

● Update(tig-tempest/WORKLIST.md)
Added 2 lines, removed 3 lines

## ON DECK (build order toward the faithful game — see memory/tempest-ruleset.md)

1. **Spiker + spikes** — spikes grow in lanes and kill you during the zoom unless shot off. (Ties directly in
to the zoom we just built.)
2. **Bestiary** — Tanker (splits), then Fuseball and Pulsar.
3. **Polish** — title/attract screen, h (Web Audio, no deps).
1. **Bestiary** — Tanker (climbs, splits into two flippers when shot/at top), then Fuseball and Pulsar.
2. **Polish** — title/attract screen, h (Web Audio, no deps).

---


● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 5: **Spiker + spikelvl 2+, ~30%) lay green zig-zag spikes up
 their lane; bolts erode spikes; a tall spike on your lane at the dive = red-flash life loss. Plus **STAND BY
 breather** after each wave + longer/casecond to breathe"). Spiker = 200 pts. JS
 syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 4: **Waves + level 2 flippers), clear → tunnel-dive transiti
on ("LEVEL n") → fresh well in a per-level hue. Per-level difficulty ramp (spawn + climb speed) and Superzapp
er refill. HUD shows LVL. JS syntax vern-green.*
- 2026-07-09 — Step 3: **Superzapper** — SPACE wipes all on-screen flippers, white flash, 2 per game (→ per-l
evel once waves land), HUD "ZAP ×n". Plfset rapid-fire: faster spawns (65–110f)
+ climb (0.0040). JS syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 2: **Hold-to-fire** authentic **8-bolt on-screen cap**; sing
le click still fires one. Angel human-green ✓ ("excellent... almost too easy" → difficulty bumped in step 3).

Deck's updated, step 5 logged. Reload and go find those green spikers — see if the spike threat adds tension without feeling
cheap, and whether the STAND BY breather gives

When you surface, tell me how the spikes read aair, and I'll tune the numbers (erode strength,danger threshold, breather length — all one-liners).

Next on the deck is the last big gameplay piece — step 6: the bestiary — the Tanker (climbs, then splits into two flippers
when you shoot it), then the Fuseball and Pulsah (title screen, high scores, sound). Say go for the Tanker, or ON DECK to pick this up fresh tomorrow — I'll read the deck and land right here.

✻ Cooked for 4m 52s

❯ go, step 6 the tanker -- feels good - I did the hard refresh to get the pulsars and i love the lok and feel bang on and
  challenging

Level with spikers looking "bang on and challen the Tanker — the enemy that climbs looking like one target, but when you shoot it, it cracks open into two flippers. Suddenly one kill becomes two new threats, so you
learn to shoot tankers early, deep in the well,ng it now.

First, tankers enter the spawn mix from level 3

● Update(tig-tempest/game/index.html)
Added 16 lines, removed 7 lines
  }

  function spawnEnemy() {
    const spiker = level >= 2 && Math.random() < 0.3;   // ~30% spikers from level 2
    enemies.push({
      type: spiker ? "spiker" : "flipper",
      lane: Math.floor(Math.random() *
      d: 1,
      flipCd: 40 + Math.random() * 40,
    });
    const r = Math.random();
    let type = "flipper";
    if (level >= 3) {
      if (r < 0.20) type = "tanker";                 // 20% tankers from level 3
      else if (r < 0.48) type = "spike
    } else if (level >= 2 && r < 0.30) {
      type = "spiker";                 on level 2
    }
    enemies.push({ type, lane: Math.fl: 1, flipCd: 40 + Math.random() * 40 });
  }

  // a shot tanker cracks open into two flippers
  function splitTanker(list, e) {
    const d = Math.min(0.85, e.d + 0.02);
    list.push({ type: "flipper", lane:.random() * 20 });
    list.push({ type: "flipper", lane: mod(e.lane + 1, LANES), d, flipCd: 12 + Math.random() * 20 });
  }

  // --- draw --------------------------------
  function ring(d) {
    ctx.beginPath();

Now the movement loop — tankers climb steadily

● Update(tig-tempest/game/index.html)
Added 2 lines, removed 2 lines

    const climb = ENEMY_SPEED * (1 + (level - 1) * 0.12);   // faster each level
    for (const e of enemies) {
      const sp = e.type === "spiker" ? 0.75 : 1;             // spikers a touch slower
      const sp = e.type === "spiker" ? 0.85 : 1;
      e.d -= climb * sp;
      if (e.type === "spiker") {
        spikes[e.lane] = Math.min(spikes[e.lane], e.d);      // extend spike behind it
      } else if (--e.flipCd <= 0) {
      } else if (e.type === "flipper" && --e.flipCd <= 0) {
        e.lane = mod(e.lane + (Math.ra);
        e.flipCd = 40 + Math.random() * 40;
      }

Now the collision loop cracks tankers into flipded after filtering:

● Update(tig-tempest/game/index.html)
Added 5 lines, removed 1 line
    }

    // bullet vs enemy (same lane, ove
    const born = [];                                   // flippers spawned by cracked tankers
    for (const e of enemies) {
      for (const b of bullets) {
        if (!e.dead && b.d <= 1 && b.ld - e.d) < HIT_DEPTH) {
          e.dead = true; b.d = 2; score += e.type === "spiker" ? 200 : 150;
          e.dead = true; b.d = 2;
          score += e.type === "spiker" ? 200 : e.type === "tanker" ? 100 : 150;
          if (e.type === "tanker") spl
        }
      }
    }


    erodeSpikes();
    enemies = enemies.filter((e) => !e.dead);
    if (born.length) enemies.push(...b
    bullets = bullets.filter((b) => b.d < 1);

    // wave cleared (all spawned, none left) -> breather, then dive

Finally, the Tanker's look — a chunky amber block, visibly tougher than the others:

● Update(tig-tempest/game/index.html)
Added 16 lines
        ctx.moveTo(top.x, top.y); ctx.lineTo(rgt.x, rgt.y);
        ctx.lineTo(bot.x, bot.y); ctx.sePath();
        ctx.fill(); ctx.shadowBlur = 0;
      } else if (e.type === "tanker")
        // chunky amber block — cracks into two flippers when shot
        const tw = 0.07;
        const n0 = ptAt(a0, Math.max(0, e.d - tw)), n1 = ptAt(a1, Math.max(0, e.d - tw));
        const f0 = ptAt(a0, Math.min(1ath.min(1, e.d + tw));
        ctx.fillStyle = "#f59e0b"; ctx.strokeStyle = "#fde68a"; ctx.lineWidth = 2;
        ctx.shadowColor = "#f59e0b"; c
        ctx.beginPath();
        ctx.moveTo(n0.x, n0.y); ctx.li
        ctx.lineTo(f1.x, f1.y); ctx.lineTo(f0.x, f0.y); ctx.closePath();
        ctx.fill(); ctx.stroke();
        ctx.beginPath();                                   // split seam down the middle
        const mn = ptAt(laneMidAngle(e);
        const mf = ptAt(laneMidAngle(e.lane), Math.min(1, e.d + tw));
        ctx.moveTo(mn.x, mn.y); ctx.li);
        ctx.shadowBlur = 0;
      } else {
        // red flipper "bowtie" spanning its lane
        const near0 = ptAt(a0, Math.maa1, Math.max(0, e.d - w));

  Ran 1 shell command

Clean — 427 lines, no errors. Reload (Ctrl+R) aTanker:

The Tanker (step 6a):
- From level 3, ~20% of the wave are chunky amber blocks with a seam down the middle — climbing steadily, no flipping.
- Shoot one and it cracks open into two red fliediately start flipping toward you. So one shotspawns two new threats.
- The lesson it teaches: kill tankers deep, eare close — pop one near the rim and you've gottwo flippers in your face with no room.
- Tanker itself is only worth 100 (the danger istill 150.

What to feel for:
- Do the amber blocks read as distinct from the red flippers and green spikers (three clear silhouettes now)?
- Does the split feel like a satisfying "uh-oh"
- Is level 3+ still fair, now that a wave can multiply on you?

Logging it:

● Update(tig-tempest/WORKLIST.md)
Added 1 line, removed 1 line

## ON DECK (build order toward the faitt-ruleset.md)

1. **Bestiary** — Tanker (climbs, split/at top), then Fuseball and Pulsar.
1. **Bestiary cont.** — Fuseball (bounces lanes + rim, only vulnerable at moments) and Pulsar (electrifies it
s lane; lethal if you're on it during t
2. **Polish** — title/attract screen, high-score table, arcade sound (Web Audio, no deps).

---

● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 6a: **Tanker** — ammbs without flipping; shot → **splits int
o two flippers** at that spot. Tanker 100 pts. Three distinct enemy silhouettes now (red bowtie / green diamo
nd / amber block). JS syntax verified. .*
- 2026-07-09 — Step 5: **Spiker + spikes** — green diamond enemies (lvl 2+, ~30%) lay green zig-zag spikes up
 their lane; bolts erode spikes; a tallve = red-flash life loss. Plus **STAND BY
 breather** after each wave + longer/calmer dive (Angel: "give me a second to breathe"). Spiker = 200 pts. JS
 syntax verified. *Awaiting Angel's hum
- 2026-07-09 — Step 4: **Waves + level zoom** — finite waves (5+lvl×2 flippers), clear → tunnel-dive transiti
on ("LEVEL n") → fresh well in a per-le ramp (spawn + climb speed) and Superzapp
er refill. HUD shows LVL. JS syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 3: **Superzapper** lippers, white flash, 2 per game (→ per-l
evel once waves land), HUD "ZAP ×n". Plus difficulty rebalance to offset rapid-fire: faster spawns (65–110f)
+ climb (0.0040). JS syntax verified. **

Deck's updated, step 6a logged. Reload and climer tankers cracking into flippers gives you that good "oh no, here we go" jolt without tipping into unfair.

When you surface, tell me how the three enemy types read together and whether the split feels right. I split the bestiary
into two beats so you can human-green each — nend the Pulsar, the two trickiest foes (one thatskates the rim and dodges your shots, one that electrifies your lane). That finishes the enemy roster; after it, it's pure
polish — title screen, high scores, and arcade pick this up fresh later.

✻ Churned for 2m 38s

❯ go, step 6b the fuseball and pulsar i made it ti forgot about the super zap but next time iwill be ready

Level 5 and it "feels real good" — you're deep in now. Time to complete the roster: step 6b, the Fuseball and the Pulsar —
the two trickiest foes. The Fuseball skates then flashes; the Pulsar electrifies your wholelane and fries you if you're standing on it when it peaks. (And ha — the Superzapper will feel a lot more tempting once
these two show up.)

Several edits. First, both enter the spawn mix  own fields:

● Update(tig-tempest/game/index.html)
Added 17 lines, removed 5 lines
  function spawnEnemy() {
    const r = Math.random();
    let type = "flipper";
    if (level >= 3) {
      if (r < 0.20) type = "tanker";   from level 3
      else if (r < 0.48) type = "spiker";            // 28% spikers
    if (level >= 5) {
      if (r < 0.14) type = "pulsar";
      else if (r < 0.28) type = "fuseb
      else if (r < 0.44) type = "tanker";
      else if (r < 0.64) type = "spike
    } else if (level >= 4) {
      if (r < 0.16) type = "fuseball";
      else if (r < 0.34) type = "tanker";
      else if (r < 0.56) type = "spike
    } else if (level >= 3) {
      if (r < 0.20) type = "tanker";
      else if (r < 0.48) type = "spiker";
    } else if (level >= 2 && r < 0.30)
      type = "spiker";                               // 30% spikers on level 2
      type = "spiker";
    }
    enemies.push({ type, lane: Math.fl: 1, flipCd: 40 + Math.random() * 40 });
    const e = { type, lane: Math.floor(Math.random() * LANES), d: 1, flipCd: 40 + Math.random() * 40 };
    if (type === "fuseball") { e.drift e.armored = false; e.armorCd = 30 + Math
.random() * 20; }
    if (type === "pulsar") { e.pulse = e.zappedThisPulse = false; }
    enemies.push(e);
  }

  // a shot tanker cracks open into tw

Now the movement loop — Fuseballs skate and cyc and drift:

● Update(tig-tempest/game/index.html)
Added 28 lines, removed 2 lines
    fireAndMoveBullets();

    const climb = ENEMY_SPEED * (1 + (er each level
    const SPEED = { spiker: 0.75, tanker: 0.85, fuseball: 0.5, pulsar: 0.7 };
    for (const e of enemies) {
      const sp = e.type === "spiker" ? 0.75 : e.type === "tanker" ? 0.85 : 1;
      e.d -= climb * sp;
      e.d -= climb * (SPEED[e.type] || 1);
      if (e.type === "spiker") {
        spikes[e.lane] = Math.min(spikes[e.lane], e.d);      // extend spike behind it
      } else if (e.type === "fuseball"
        if (--e.driftCd <= 0) {                              // skate to a neighbouring lane
          e.lane = mod(e.lane + (Math.ES);
          e.driftCd = 18 + Math.random() * 22;
        }
        if (--e.armorCd <= 0) {                              // flicker between armoured / vulnerable
          e.armored = !e.armored;
          e.armorCd = (e.armored ? 25 : 40) + Math.random() * 15;
        }
      } else if (e.type === "pulsar") {
        e.pulse = (e.pulse + 0.06) % (rge toward the next zap
        if (--e.flipCd <= 0) {
          e.lane = mod(e.lane + (Math.ES);
          e.flipCd = 50 + Math.random() * 40;
        }
      } else if (e.type === "flipper" && --e.flipCd <= 0) {
        e.lane = mod(e.lane + (Math.ra);
        e.flipCd = 40 + Math.random() * 40;
      }
    }

    // pulsar electrifies its lane — lethal if you're standing on it at the peak
    for (const e of enemies) {
      if (e.type !== "pulsar") continue;
      const hot = Math.sin(e.pulse) >
      if (hot && !e.zappedThisPulse && playerLane === e.lane) {
        lives--; hurtFlash = 12; e.zap
        if (lives <= 0) gameOver = true;
      }
      if (!hot) e.zappedThisPulse = false;
    }

    // bullet vs enemy (same lane, ove
    const born = [];                                   // flippers spawned by cracked tankers
    for (const e of enemies) {

Now the collision loop — armored Fuseballs shruies score higher:

● Update(tig-tempest/game/index.html)
Added 3 lines, removed 1 line
    }

    // bullet vs enemy (same lane, ove
    const POINTS = { spiker: 200, tanker: 100, fuseball: 250, pulsar: 300, flipper: 150 };
    const born = [];                  spawned by cracked tankers
    for (const e of enemies) {
      for (const b of bullets) {
        if (!e.dead && b.d <= 1 && b.lane === e.lane && Math.abs(b.d - e.d) < HIT_DEPTH) {
          if (e.type === "fuseball" &&vulnerable while armoured
          e.dead = true; b.d = 2;
          score += e.type === "spiker"? 100 : 150;
          score += POINTS[e.type] || 150;
          if (e.type === "tanker") spl
        }
      }

Finally, the visuals — a crackling Fuseball anda warning bolt down its lane:

● Update(tig-tempest/game/index.html)
Added 31 lines
        const mf = ptAt(laneMidAngle(e);
        ctx.moveTo(mn.x, mn.y); ctx.lineTo(mf.x, mf.y); ctx.stroke();
        ctx.shadowBlur = 0;
      } else if (e.type === "fuseball") {
        // crackling energy ball — brile when armoured
        const c = ptAt(laneMidAngle(e.lane), e.d);
        const col = e.armored ? "#7c3a
        ctx.strokeStyle = col; ctx.shadowColor = col; ctx.shadowBlur = e.armored ? 6 : 16; ctx.lineWidth = 2
;
        const spokes = 6, len = R * 0.035;
        ctx.beginPath();
        for (let s = 0; s < spokes; s++) {
          const ang = (s / spokes) * M
          const r2 = len * (0.5 + 0.7 * Math.abs(Math.sin(e.d * 22 + s)));
          ctx.moveTo(c.x, c.y); ctx.li, c.y + Math.sin(ang) * r2);
        }
        ctx.stroke(); ctx.shadowBlur =
      } else if (e.type === "pulsar") {
        const a = laneMidAngle(e.lane)
        if (s > 0.3) {                                     // electrified lane — warn the player
          const inten = (s - 0.3) / 0.
          ctx.strokeStyle = "rgba(56,189,248," + (0.3 + 0.6 * inten).toFixed(2) + ")";
          ctx.shadowColor = "#38bdf8"; ctx.lineWidth = 2;
          ctx.beginPath();
          for (let k = 0; k <= 8; k++)
            const p = ptAt(a + (k % 2 ? 0.045 : -0.045), k / 8);
            k === 0 ? ctx.moveTo(p.x,
          }
          ctx.stroke(); ctx.shadowBlur
        }
        const body = ptAt(a, e.d);
        ctx.fillStyle = s > 0.75 ? "#e0f2fe" : "#0ea5e9";
        ctx.shadowColor = "#38bdf8"; c
        ctx.beginPath(); ctx.arc(body.x, body.y, R * 0.022, 0, Math.PI * 2); ctx.fill();
        ctx.shadowBlur = 0;
      } else {
        // red flipper "bowtie" spanni
        const near0 = ptAt(a0, Math.max(0, e.d - w)), near1 = ptAt(a1, Math.max(0, e.d - w));

  Ran 1 shell command

Clean — 498 lines, no errors. Reload (Ctrl+R) and push to levels 4–5 to meet the last two foes:

The Fuseball (level 4+):
- A crackling energy ball that skates lane to lerable (bright pink) and armored (dim purple) —bolts pass right through it while it's purple. You have to time your shot for the bright phase. Worth 250.

The Pulsar (level 5+):
- A blue orb that charges up and electrifies itcyan lightning bolt crackle down the lane,brightening as it peaks. If you're standing on that lane at the peak, you get zapped (red flash, lose a life). Slide off a
lit lane. Worth 300.

That's the full bestiary — five distinct enemiete and threat:
- 🔴 Flipper (bowtie) · 🟢 Spiker (diamond) · 🟠 Tanker (block) · 🟣 Fuseball (crackle) · 🔵 Pulsar (orb + bolt)

What to feel for:
- Does the Fuseball's armored flicker read cleaike timing not a glitch?
- Does the Pulsar give you enough warning to get off its lane, or is the zap a cheap death?
- With all five loose at level 5, is it thrilliwn rates are all tunable.)

Logging step 6b:

● Update(tig-tempest/WORKLIST.md)
Added 1 line, removed 2 lines

## ON DECK (build order toward the faithful game — see memory/tempest-ruleset.md)

1. **Bestiary cont.** — Fuseball (bounces lanes + rim, only vulnerable at moments) and Pulsar (electrifies it
s lane; lethal if you're on it during t
2. **Polish** — title/attract screen, high-score table, arcade sound (Web Audio, no deps).
1. **Polish** — title/"INSERT COIN" att, arcade sound (Web Audio, no deps). *(Fu
ll bestiary now done — this is the last stretch.)*

---


● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 6b: **Fuseball + Pulsar** — Fuseball (lvl 4+): crackling ball, skates lanes, flickers arm
ored (bolt-proof) / vulnerable, 250 ptss its whole lane (cyan bolt warning); let
hal if you're on it at the peak, 300 pts. **Full 5-enemy bestiary done.** JS syntax verified. *Awaiting Angel
's human-green.*
- 2026-07-09 — Step 6a: **Tanker** — amber block (lvl 3+, ~20%), climbs without flipping; shot → **splits int
o two flippers** at that spot. Tanker 1silhouettes now (red bowtie / green diamo
nd / amber block). JS syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 5: **Spiker + spikelvl 2+, ~30%) lay green zig-zag spikes up
 their lane; bolts erode spikes; a tall spike on your lane at the dive = red-flash life loss. Plus **STAND BY
 breather** after each wave + longer/casecond to breathe"). Spiker = 200 pts. JS
 syntax verified. *Awaiting Angel's human-green.*
- 2026-07-09 — Step 4: **Waves + level 2 flippers), clear → tunnel-dive transiti
on ("LEVEL n") → fresh well in a per-level hue. Per-level difficulty ramp (spawn + climb speed) and Superzapp
er refill. HUD shows LVL. JS syntax vern-green.*

Let me update the project's current situation ses accurately:

● Update(tig-tempest/CLAUDE.md)
Added 3 lines, removed 3 lines

Keep this short and true. Update it when reality changes.

- **Location:** `ground-control/tig-tempest/`
- **Location:** `ground-control/tig-temhtml` (canvas + plain JS, ~500 lines, no
deps).
- **Mission:** Build a playable 80s-arct of **Tempest** (Angel's favorite).
- **Status:** Day one. Spine and worklist just set up. No game code yet.
- **Open fronts:** (1) decide the exactlayable frame on screen, (3) core movemen
t + shooting loop.
- **Status:** Fully playable. Core looppper + **all 5 enemies** (Flipper, Spiker
, Tanker, Fuseball, Pulsar) done and human-green'd through level 5. Difficulty tuned "bang on."
- **Open fronts:** Just **polish** leftt screen, high-score table, arcade sound
(Web Audio, no deps). See `WORKLIST.md`.

---


Deck's updated, step 6b logged, and the spine n cold-start tomorrow and land exactly here.

Reload and put the last two enemies through the worth naming: the game is now fully playable,with the complete Tempest bestiary. Everything past this is polish, not gameplay.

When you surface, tell me how the Fuseball's armor-timing and the Pulsar's zap warning feel — those are the two most tunable
of the bunch, and I want them thrilling, not ch

Next on the deck is the final stretch — step 7:IN attract screen, a high-score table so yourruns mean something, and arcade sound (blips and zaps via Web Audio, still zero dependencies). That's what turns it from "a
great prototype" into "a cabinet you'd drop a qECK to pick it up fresh — Tig'll read the deckand be right here.

✻ Worked for 3m 14s

※ recap: We're building a playable Tempest-style arcade game in tig-tempest/game. The full 5-enemy bestiary is done and
  human-green through level 5, so only polish rem title/INSERT COIN screen, high-score table, and arcade sound.

❯ go, step 7 polish -- the game is challenging and i love it feels good and works fine good responses

Final stretch — step 7: polish. Title/attract screen, a high-score table so your runs count, and arcade sound. Let me first
read the current tail of the file to see exactlo I wire the new title state in cleanly:

  Searched for 1 pattern, read 1 file

Now I understand the setup — and I found a lateg: there's no title state, so the game currently auto-triggers a wave-clear on the very first frame (it actually dives to level 2 before you touch anything). Adding a
proper title screen fixes that cleanly, because title until you click, then start fresh atlevel 1.

Here's the plan for step 7, all in this one file: title/attract screen, high-score table (saved in your browser), and arcade
sound (synthesized with Web Audio — no files, ns.

First, new state and element refs:

● Update(tig-tempest/game/index.html)
Added 2 lines
  const scoreEl = document.getElementBy
  const zapEl = document.getElementById("zap");
  const livesEl = document.getElementBy
  const hudEl = document.getElementById("hud");
  const hintEl = document.getElementByI

  const LANES = 16;         // segments
  let cx = 0, cy = 0;       // centre / vanishing point

  Read 1 file

● Update(tig-tempest/game/index.html)
Added 4 lines, removed 1 line
  let enemies = [];         // flippers: { lane, d, flipCd }  d shrinks 1 -> 0 (deep to rim)
  let score = 0;
  let lives = 3;
  let gameOver = false;
  let mode = "title";           // "title" | "play" | "over"
  let ticks = 0;                // globn)
  let muted = false;
  let lastRank = -1;            // rankthe high-score table
  let spawnTimer = 60;
  let firing = false;           // mous
  let fireCd = 0;               // frames until next auto-shot

Now update reset() (drop the old gameOver, it's mode-driven now) and add the audio + high-score helpers right after it:

● Update(tig-tempest/game/index.html)
Added 53 lines, removed 2 lines
  const SPIKE_ERODE = 0.09;     // how much of a spike a single bolt knocks back
  const SPIKE_DANGER = 0.45;    // spithal on the dive

  function reset() {
    score = 0; lives = 3; gameOver = false; firing = false; fireCd = 0;
  function startGame() {
    score = 0; lives = 3; firing = false; fireCd = 0;
    zapFlash = 0; hurtFlash = 0; level= 0;
    lastRank = -1; mode = "play";
    startWave();
    sfx.start();
  }

  function endGame() {
    mode = "over"; firing = false;
    recordScore(score, level);
    sfx.gameover();
  }

  // --- high scores (saved in the bro--------
  const HS_KEY = "tig_tempest_highscores";
  function loadScores() {
    try { return JSON.parse(localStorage.getItem(HS_KEY)) || []; } catch (e) { return []; }
  }
  let highScores = loadScores();
  function recordScore(s, lvl) {
    const entry = { s, lvl };
    highScores.push(entry);
    highScores.sort((a, b) => b.s - a.s);
    highScores = highScores.slice(0, 8
    lastRank = highScores.indexOf(entry);          // -1 if it didn't make the table
    try { localStorage.setItem(HS_KEY, } catch (e) {}
  }
  const topScore = () => (highScores[0

  // --- sound (synthesized, no assets--------
  let actx = null;
  function tone(freq, dur, type, vol,
    if (muted) return;
    try {
      if (!actx) actx = new (window.AudioContext || window.webkitAudioContext)();
      if (actx.state === "suspended")
      const o = actx.createOscillator(), g = actx.createGain(), t = actx.currentTime;
      o.type = type || "square";
      o.frequency.setValueAtTime(freq, t);
      if (slideTo) o.frequency.exponen, t + dur);
      g.gain.setValueAtTime(vol || 0.06, t);
      g.gain.exponentialRampToValueAtT
      o.connect(g); g.connect(actx.destination);
      o.start(t); o.stop(t + dur);
    } catch (e) {}
  }
  const sfx = {
    fire:     () => tone(720, 0.07, "s
    hit:      () => tone(200, 0.12, "sawtooth", 0.07, 70),
    zap:      () => { tone(880, 0.35, 40, 0.35, "square", 0.06, 60); },
    dive:     () => tone(180, 0.5, "sine", 0.08, 900),
    hurt:     () => tone(320, 0.3, "sq
    start:    () => { tone(440, 0.1, "square", 0.07); tone(660, 0.1, "square", 0.07); },
    gameover: () => { tone(300, 0.5, "
  };

  // begin the wave for the current `level`
  function startWave() {
    bullets = []; enemies = [];

Now wire sound into the actions and swap the old gameOver flag for the mode/endGame() flow. Starting with startZoom,
tryFire, and superzap:

● Update(tig-tempest/game/index.html)
Added 3 lines, removed 2 lines
  function startZoom() {
    // crashing into a tall spike on your lane costs a life
    if (spikes[playerLane] < SPIKE_DAN
      lives--; hurtFlash = 12;
      if (lives <= 0) { gameOver = tru
      lives--; hurtFlash = 12; sfx.hurt();
      if (lives <= 0) { endGame(); ret
    }
    zooming = true; zoomT = 0; firing
    level++;                      // display the new level during the dive
    sfx.dive();
  }

  function finishZoom() {

● Update(tig-tempest/game/index.html)
Added 2 lines
    if (bullets.length >= MAX_SHOTS) return;   // shot cap — must let bolts clear
    bullets.push({ lane: playerLane, d
    fireCd = FIRE_INTERVAL;
    sfx.fire();
  }

  function superzap() {

    zaps--;
    enemies = [];                     limbing the well
    zapFlash = 14;
    sfx.zap();
  }

  // --- input ------------------------------------------------------------

Now the input handlers become mode-aware (title → start, over → back to title) with an M mute toggle:

● Update(tig-tempest/game/index.html)
Added 5 lines, removed 2 lines
    mouseAngle = Math.atan2(e.clientY - cy, e.clientX - cx);
  });
  window.addEventListener("mousedown", () => {
    if (gameOver) { reset(); return; }
    if (mode === "title") { startGame(); return; }
    if (mode === "over") { mode = "tit
    firing = true; fireCd = 0; tryFire();   // instant first shot, then auto-repeat
  });
  window.addEventListener("mouseup", () => { firing = false; });
  window.addEventListener("blur", () =
  window.addEventListener("keydown", (e) => {
    if (e.code === "KeyM") { muted = !ggle
    if (e.code === "Space") {
      e.preventDefault();
      if (gameOver) { reset(); return; }
      if (mode === "title") { startGam
      if (mode === "over") { mode = "title"; return; }
      superzap();
    }
  });

Now update the gameplay loop — gate it to play →endGame() swap with the remaining sound hooks:

● Update(tig-tempest/game/index.html)
Added 1 line, removed 1 line
  function update() {
    playerLane = nearestLane(mouseAngle);
    updateHud();
    if (gameOver) return;
    if (mode !== "play") return;

    if (zooming) {                    he next level
      zoomT += 1 / ZOOM_FRAMES;

● Update(tig-tempest/game/index.html)
Added 2 lines, removed 2 lines
      if (e.type !== "pulsar") continue;
      const hot = Math.sin(e.pulse) >
      if (hot && !e.zappedThisPulse && playerLane === e.lane) {
        lives--; hurtFlash = 12; e.zap
        if (lives <= 0) gameOver = true;
        lives--; hurtFlash = 12; sfx.hue;
        if (lives <= 0) endGame();
      }
      if (!hot) e.zappedThisPulse = false;
    }

● Update(tig-tempest/game/index.html)
Added 5 lines, removed 2 lines
      for (const b of bullets) {
        if (!e.dead && b.d <= 1 && b.lane === e.lane && Math.abs(b.d - e.d) < HIT_DEPTH) {
          if (e.type === "fuseball" &&vulnerable while armoured
          e.dead = true; b.d = 2;
          e.dead = true; b.d = 2; sfx.
          score += POINTS[e.type] || 150;
          if (e.type === "tanker") spl
        }

    }
    // enemy reached the rim -> costs
    for (const e of enemies) {
      if (e.d <= 0 && !e.dead) { e.dea<= 0) gameOver = true; }
      if (e.d <= 0 && !e.dead) {
        e.dead = true; lives--; hurtFl
        if (lives <= 0) endGame();
      }
    }

    erodeSpikes();

● Update(tig-tempest/game/index.html)
Added 1 line, removed 1 line
    bullets = bullets.filter((b) => b.d < 1);

    // wave cleared (all spawned, none left) -> breather, then dive
    if (!gameOver && toSpawn <= 0 && ed = CLEAR_HOLD;
    if (mode === "play" && toSpawn <= 0 && enemies.length === 0) clearHold = CLEAR_HOLD;
  }

  function frame() {

Now the screens themselves — the title/attract ver with the high-score table:

● Update(tig-tempest/game/index.html)
Added 58 lines, removed 7 lines
    ctx.shadowBlur = 0;
  }

  function drawTitle() {
    ctx.save();                        attract well behind the title
    ctx.translate(cx, cy); ctx.rotate(ticks * 0.0025); ctx.translate(-cx, -cy);
    drawWell();
    ctx.restore();
    ctx.fillStyle = "#000a"; ctx.fillRs.height);
    ctx.textAlign = "center";

    ctx.fillStyle = "#22d3ee"; ctx.shadowColor = "#22d3ee"; ctx.shadowBlur = 24;
    ctx.font = "bold 60px 'Courier New
    ctx.fillText("T E M P E S T", cx, cy - 66);
    ctx.font = "15px 'Courier New', mo ctx.fillStyle = "#64748b";
    ctx.fillText("T I G   ·   an arcade tribute", cx, cy - 36);

    if (Math.floor(ticks / 30) % 2 === 0) {      // blinking coin prompt
      ctx.fillStyle = "#facc15"; ctx.shadowBlur = 16;
      ctx.font = "24px 'Courier New', monospace";
      ctx.fillText("CLICK TO INSERT CO
      ctx.shadowBlur = 0;
    }
    ctx.fillStyle = "#94a3b8"; ctx.font = "13px 'Courier New', monospace";
    ctx.fillText("MOVE — MOUSE     FIR SPACE", cx, cy + 52);
    ctx.fillStyle = "#475569";
    ctx.fillText("M — MUTE" + (muted ?);
    if (topScore() > 0) {
      ctx.fillStyle = "#22d3ee"; ctx.fnospace";
      ctx.fillText("HIGH SCORE   " + String(topScore()).padStart(6, "0"), cx, cy + 104);
    }
  }

  function drawScoreTable(topY) {
    ctx.textAlign = "center"; ctx.fontpace";
    ctx.fillStyle = "#64748b"; ctx.fillText("— HIGH SCORES —", cx, topY);
    for (let i = 0; i < highScores.len
      const h = highScores[i], isNew = i === lastRank;
      ctx.fillStyle = isNew ? "#facc15
      ctx.fillText(
        String(i + 1).padStart(2, " ")art(6, "0") + "   LVL " + h.lvl + (isNew
? "  <" : ""),
        cx, topY + 26 + i * 20);
    }
  }

  function drawGameOver() {
    ctx.fillStyle = "#000c"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.textAlign = "center"; ctx.fill
    ctx.shadowColor = "#22d3ee"; ctx.shadowBlur = 20;
    ctx.font = "48px 'Courier New', mo
    ctx.fillText("GAME OVER", cx, cy - 10);
    ctx.font = "18px 'Courier New', mo4a3b8"; ctx.shadowBlur = 0;
    ctx.fillText("SCORE " + String(score).padStart(6, "0"), cx, cy + 30);
    ctx.fillText("CLICK TO INSERT COIN
    ctx.textAlign = "center";
    ctx.fillStyle = "#ef4444"; ctx.shadowBlur = 20;
    ctx.font = "46px 'Courier New', monospace";
    ctx.fillText("GAME OVER", cx, cy -
    ctx.shadowBlur = 0;
    ctx.fillStyle = "#e2e8f0"; ctx.fonspace";
    ctx.fillText("SCORE " + String(score).padStart(6, "0") + "   ·   LEVEL " + level, cx, cy - 98);
    if (lastRank === 0) {
      ctx.fillStyle = "#facc15"; ctx.font = "16px 'Courier New', monospace";
      ctx.fillText("★  NEW HIGH SCORE
    }
    drawScoreTable(cy - 44);
    if (Math.floor(ticks / 30) % 2 === 0) {
      ctx.fillStyle = "#64748b"; ctx.fnospace";
      ctx.fillText("CLICK TO CONTINUE", cx, cy + 150);
    }
  }

  // --- update -----------------------------------------------------------

Finally, frame() — drive the mode machine, tick the clock, and toggle the DOM HUD/hint per screen:

● Update(tig-tempest/game/index.html)
Added 8 lines, removed 1 line
  }

  function frame() {
    ticks++;
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, canvas.width, canvas.height);
    update();

    hudEl.style.display = mode === "ti
    hintEl.style.display = mode === "play" ? "" : "none";

    if (mode === "title") { drawTitle(); requestAnimationFrame(frame); return; }

    if (zooming) {
      drawZoom(zoomT);
    } else {

      ctx.fillRect(0, 0, canvas.width, canvas.height);
      hurtFlash--;
    }
    if (gameOver) drawGameOver();
    if (mode === "over") drawGameOver();
    requestAnimationFrame(frame);
  }
  frame();

Let me add the mute key to the in-game hint, th

● Update(tig-tempest/game/index.html)
Added 1 line, removed 1 line
<body>
<div id="hud"><span id="score">SCORE 000000</span><span id="zap">ZAP ×2</span><span id="lives">LIVES ♦ ♦ ♦</s
pan></div>
<canvas id="game"></canvas>
<div id="hint">MOVE MOUSE — RIDE THE RI — SUPERZAPPER</div>
<div id="hint">MOVE MOUSE — RIDE THE RIM · CLICK/HOLD — FIRE · SPACE — SUPERZAPPER · M — MUTE</div>
<script>
(() => {
  "use strict";

  Ran 1 shell command

Clean — 621 lines, no errors, and zero stale gaigration is complete). Reload (Ctrl+R) — andthis reload is special, because it's the first time the game opens the way it should:

Title / attract screen:
- A slowly spinning well behind a big T E M P Ee," a blinking INSERT COIN, the controls, andyour HIGH SCORE.
- Also fixes that first-frame bug — the game noean at level 1.

Sound (all synthesized, no files):
- pew on fire, a crunch on each kill, a big sweep on the Superzapper, a rising whoosh on the level dive, a buzz when you're
hit, a start jingle, and a game-over tone.
- Press M anytime to mute.

High-score table (saved in your browser):
- On game over you now see GAME OVER, your scorscores, and if you cracked the top it highlights your new entry in gold with ★ NEW HIGH SCORE ★. Beat your best and it says so. Scores persist across sessions via
localStorage.

What to check:
- Does the title screen feel like a real cabinet you want to drop a coin into?
- Are the sounds satisfying or annoying — anytha one-line tweak; the fire blip especially,since it's the most frequent.)
- Play a full run to GAME OVER and confirm the  and your first score should still be listed.

Logging the final step and marking the mileston

● Update(tig-tempest/WORKLIST.md)
Added 5 lines, removed 2 lines

---

## ON DECK (build order toward the faithful game — see memory/tempest-ruleset.md)
## ON DECK

1. **Polish** — title/"INSERT COIN" att, arcade sound (Web Audio, no deps). *(Fu
ll bestiary now done — this is the last stretch.)*
*The faithful build is complete — core , full 5-enemy bestiary, title screen, hi
gh scores, and sound are all in. From here it's polish-to-taste and whatever Angel wants next. Ideas parked b
elow.*

1. **Tuning pass (optional)** — dial soke danger to taste after more play.
2. **Nice-to-haves** — bonus lives at score thresholds, a real attract-mode demo, more tube shapes (open/fan
tubes), enemy variety per level, pause

---

## DONE (log — newest first)

● Update(tig-tempest/WORKLIST.md)
Added 1 line

## DONE (log — newest first)

- 2026-07-09 — Step 7: **Polish** — title/attract screen (spinning well, blinking INSERT COIN, controls, high
 score), **synthesized arcade sound** (gameover, M to mute), **high-score table*
* saved to localStorage (top 8, new-entry highlight). Introduced a `mode` state machine (title/play/over) — a
lso fixed a latent first-frame auto-divat lvl 1). JS syntax verified, no stale r
efs. *Awaiting Angel's human-green.* **← faithful build complete.**
- 2026-07-09 — Step 6b: **Fuseball + Purackling ball, skates lanes, flickers arm
ored (bolt-proof) / vulnerable, 250 pts. Pulsar (lvl 5+): electrifies its whole lane (cyan bolt warning); let
hal if you're on it at the peak, 300 ptne.** JS syntax verified. *Awaiting Angel
's human-green.*
- 2026-07-09 — Step 6a: **Tanker** — ammbs without flipping; shot → **splits int
o two flippers** at that spot. Tanker 100 pts. Three distinct enemy silhouettes now (red bowtie / green diamo
nd / amber block). JS syntax verified. .*
- 2026-07-09 — Step 5: **Spiker + spikes** — green diamond enemies (lvl 2+, ~30%) lay green zig-zag spikes up
 their lane; bolts erode spikes; a tallve = red-flash life loss. Plus **STAND BY
 breather** after each wave + longer/calmer dive (Angel: "give me a second to breathe"). Spiker = 200 pts. JS
 syntax verified. *Awaiting Angel's hum

● Update(tig-tempest/CLAUDE.md)
Added 2 lines, removed 2 lines

- **Location:** `ground-control/tig-tempest/` — game in `game/index.html` (canvas + plain JS, ~500 lines, no
deps).
- **Mission:** Build a playable 80s-arcade tube shooter in the spirit of **Tempest** (Angel's favorite).
- **Status:** Fully playable. Core looppper + **all 5 enemies** (Flipper, Spiker
, Tanker, Fuseball, Pulsar) done and human-green'd through level 5. Difficulty tuned "bang on."
- **Open fronts:** Just **polish** leftt screen, high-score table, arcade sound
(Web Audio, no deps). See `WORKLIST.md`.
- **Status:** Feature-complete. Core lozapper + **all 5 enemies** (Flipper, Spik
er, Tanker, Fuseball, Pulsar) + **title screen, high scores, synthesized sound** — all done. Difficulty tuned
 "bang on" through level 5.
- **Open fronts:** None required. Optional tuning + nice-to-haves parked in `WORKLIST.md` (bonus lives, more
tube shapes, pause, attract demo).

---


Deck's updated, step 7 logged, and the spine now reads "feature-complete." Here's the moment worth marking:

The game is done. In one session you went from a lost chat message to a fully playable, faithful Tempest tribute — the
receding well, mouse-on-the-rim control, hold-tt cap, the Superzapper, waves with thelevel-dive, all five enemies, and now a title screen, saved high scores, and arcade sound. No dependencies, one HTML file,
opens in any browser.

And it never once lived only in chat. Every stecision in memory/, the whole shape in CLAUDE.md. That's the thing the kit was really teaching, and you just felt it work across seven build steps.

Your last human-green pass: play a full run to GAME OVER, then a second run, and confirm your first score is still sitting
in the table. Tell me how the sound and the tite two most taste-dependent pieces and theeasiest to tune.

When you're happy, this is a natural place to commit — I can put the whole tig-tempest/ game in as a clean commit whenever
you say the word (you're on main, so I'd branch

And the payoff you've been building toward: tom DECK — Tig reads the deck and lands exactlyhere, no re-explaining. Nicely done, Angel. 🕹️

✻ Worked for 6m 16s

※ recap: We built a complete Tempest-style arcade game in tig-tempest/game/index.html, finishing step 7 (title screen, high
  scores, sound). Next: reload the browser, play save, then commit when you're happy.

❯ [Image #1] very good tigs commit it -- lesson lound control repo and you can build real stufffast and never loose control -- The Tempest. In literature, tempests are frequently used as literary devices to mirror the
  internal turmoil of characters >> Technology: Iity world, TEMPEST (an acronym originallystanding for Telecommunications Electronics Material Protected from Emanating Spurious Transmissions) refers to the
  investigation and shielding of devices to preveed data through electromagnetic radiation. --just in case you wanted a little more context for this concept of programming via claude LLMs and in the age of vibe coders
  with zero programming skills -- just saying for
[Image #1]

That screenshot is a thing of beauty — SCORE 010650, LEVEL 6, ★ NEW HIGH SCORE ★, the table saved your run, and the whole
thing frozen over the well with the enemies sti is working exactly as designed.Congratulations, Angel — that's a real game.

And that double meaning of TEMPEST is perfect: the storm that mirrors inner turmoil, and the cybersecurity acronym for
shielding against leaked emanations. A fitting omeone who set up process-control systems andnow steers an AI copilot without ever losing control of what it emits. Noted and appreciated.

Let me capture the lesson, then commit. First the durable takeaways go into files:

● Update(tig-tempest/CLAUDE.md)
Added 1 line
When something bites, write the lesson here in one line so it never bites twice.

- 2026-07-09 — A chat response that isn't written to a file is gone at the next compaction. First real proof
of Rule 1: everything that matters goests because a lost response taught it.)*
- 2026-07-09 — Start fresh with a Ground Control spine and you can build real stuff fast and never lose contr
ol. Proof: a full, faithful Tempest trienemies, sound, high scores) built in one
 session — steered by Angel, rowed by Tig, every step logged to files. The method scales from a lost message
to a finished game without the human ev

---


● Write(tig-tempest/memory/method-works.md)
Wrote 13 lines to tig-tempest/memory/method-
---
description: The Ground Control method prte-to-files built a full game fast; recal
l when Angel doubts the process or starts a new build
---

ou can build real stuff fast and never lo

(7 build steps, ~620 lines, 5 enemies, wa, title screen, high scores, synthesized
sound). Angel steered ("go, step N"), Tig rowed and verified each step, and every decision/step went to files (
with zero programming skills," Angel's eneering.
… +12 lines

● Update(tig-tempest/memory/MEMORY.md)
Added 1 line
- [Who Angel is](angel-who.md) — the captain's background; open when context about him matters
- [Project: Tempest-lineage arcade shoot what we're building and the fixed decisi
ons
- [Tempest ruleset](tempest-ruleset.md) ; open when adding gameplay to stay faith
ful
- [The method works](method-works.md) —  built a full game fast without losing co
ntrol; recall on new builds or process doubt

Now the commit. You're on main, so I'll branch first, then commit the whole game:

  Ran 2 shell commands

Git has no identity configured in this repo. Let me match the existing commits' author so it's consistent, then retry:

  Ran 1 shell command

The existing commits are all Angelo Kenel <angel.kenel@gmail.com>. I'll set that as the repo-local identity (not global) so
this commit matches, then commit:

  Ran 1 shell command

Done — committed as 8f737ae on a new branch tigntouched). Let me confirm exactly what landed:

  Ran 1 shell command

Committed clean. Here's the final state:

Commit 8f737ae on branch tig-tempest-game (main
- Authored as Angelo Kenel <angel.kenel@gmail.com> — matching your existing history
- 8 files, 845 insertions — the game (game/indeull spine (CLAUDE.md, WORKLIST.md, and all 5memory files)

Your lesson made it into the permanent record too — it's in CLAUDE.md's LESSONS and in a new memory/method-works.md, in your
own words: "Start fresh with a Ground Control ruff fast and never lose control." That's thethesis of the whole kit, and you just proved it end-to-end — a lost message became a finished, high-score-tracking arcade
game in one session, with you steering every stwheel.

Where things stand:
- The work is committed and safe on its own branch.
- If you want it on main, just say so and I'll e it as a branch — your call.
- If you ever want it online, this is a single static file — it'd drop straight onto GitHub Pages or Netlify with zero
config.

And the payoff you built toward: next session, g reads the deck, sees the build is complete,and picks up wherever you point — a tuning pass, GitHub Pages, or a brand-new project on the same spine.

Real engineering judgment steering a fast copilot. That's the method. Well played, Angel. 🕹️

✻ Cogitated for 2m 11s

❯ merge it to main and this is the repo https://github.com/akenel/ground-control -- any questions tips or tricks tigs ?

On it — merging to main now, then I'll check the remote so we can get it up to github.com/akenel/ground-control.

  Merged tig-tempest-game

Merged to main cleanly (fast-forward, no conflicts), and origin is exactly your repo: github.com/akenel/ground-control.git.
Main is now one commit ahead of the remote. Sin, let me push it up:

  Pushed to main

It's live — pushed to main on github.com/akenel tribute is now public, sitting right alongsidethe kit it was built with. The game file is at:

https://github.com/akenel/ground-control/blob/main/tig-tempest/game/index.html

Let me tidy the now-merged branch and check what tooling you've got for the best next trick:

  Ran 1 shell command

All cleaned up — merged branch deleted, main is your single source of truth, and here's a bonus: gh is installed and you're
already authenticated as akenel. That unlocks tu.

The one trick worth doing next: make it playabl

Right now people can read your game's code on G — clicking the file shows source, not a running game. Because it's a single self-contained HTML file, GitHub Pages will host it as a real playable website for free. You'd
get a link like:

https://akenel.github.io/ground-control/tig-tem

…that anyone can click and play, no install. Sile it in one command and add a "▶ Play" link toyour README so visitors find it. Want me to turn that on? (It publishes a public web page from the repo — your call, so I'll
wait for the word.)

A few more tips & tricks, peer to peer

- The spine is your real asset, not the game. t filled-in example you can copy for the nextproject — cp -r, wipe the WORKLIST, keep the shape. You've got a personal template now.
- ON DECK still works cold. Next session, that  the deck — a tuning pass, Pages, or somethingnew.
- Small commits beat big ones. We shipped this one session, but going forward, commit perhuman-green'd step — your history becomes a changelog you can actually read.
- The ! prefix is your friend. For anything intdeploy prompt), type ! <command> here so theoutput lands in our chat and I can see it.                                                                                  
One genuine question back to you: do you want to keep evolving this game (bonus lives, new tube shapes, an attract-mode demo — all parked in the WORKLIST), or is Tempest "dt ON DECK starts a fresh build on the samespine? Either's a great answer — I just want the deck pointing the right way for tomorrow.

Hell of a session, Angel. 🕹️

✻ Cooked for 1m 23s

❯ yes turn on pages and add the play link

On it — enabling Pages and reading the README so I can add the Play link where it fits:

  Read 1 file, ran 1 shell command

Pages is enabled — GitHub confirmed the site at https://akenel.github.io/ground-control/. Now adding the Play link to the
README:

● Update(README.md)
Added 8 lines
   └─► worked-example ───► proof it wor
```

## ▶ Built with this method — play it

This repo eats its own cooking. [**TIG · Tempest**](https://akenel.github.io/ground-control/tig-tempest/game/
) is a complete arcade game — a faithfu — built in a **single session** using no
thing but the spine in this kit: a human steering, an AI copilot rowing, every step written to files.

**[▶ Play it in your browser →](https://akenel.github.io/ground-control/tig-tempest/game/)**

Then read its [context spine](tig-tempest/CLAUDE.md) and [build log](tig-tempest/WORKLIST.md) to see the meth
od's fingerprints on a real thing.

## The one rule that makes it all work

> **Write to files, not chat.** Chat is next compaction. Files are stone. Anythi
ng that matters goes into a file your copilot reads next session, or it never happened.

Now commit and push so the Play link goes live:

  Pushed to main

Pushed — commit e76ec73 is live. Let me check that the Pages site has finished building so I can hand you a working link,
not a 404:

  Ran 1 shell command

It's live and already serving — I probed the ac0. (The build status still says "building"because that's the rebuild from the README push catching up; the game itself is up now.)

🕹️ Your game is on the internet

- ▶ Play: https://akenel.github.io/ground-control/tig-tempest/game/
- Repo: https://github.com/akenel/ground-contro
- README Play button: live within a minute, once this last build finishes

Anyone you send that first link to can play your Tempest tribute in their browser — no install, no account, on desktop or
phone. Send it to someone and watch them get to

Where this session landed

From a lost chat message to a publicly playablegame with a live URL — in one sitting:

- ✅ Full game built in 7 human-green'd steps (
- ✅ Filled-in Ground Control spine (CLAUDE.md, WORKLIST.md, memory/)
- ✅ Committed, merged to main, pushed to your
- ✅ GitHub Pages on, README pointing at the playable link
- ✅ Every decision and lesson written to files

And the README now eats its own cooking: the kit by its own method. That's a stronger pitchthan any paragraph could make.

Next ON DECK picks up from here — whether that's polishing the game (bonus lives, new tube shapes), taking it further, or
starting a brand-new build on the same spine. Wds the deck and goes.

Steer, I row. That was a great flight, Angel.

✻ Churned for 1m 51s

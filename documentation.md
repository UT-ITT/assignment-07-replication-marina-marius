# Documentation

This is the complete development chronicle for Assignment 7:
Every decision, every detour and every bug that made us swear at pyglet, all in one scroll. In the same spirit as [`README.md`](README.md): a braindump, not a polished lab report, because that's how the two weeks (*inoffically 1 1/2 weeks) actually happened.

This file now also **absorbs** [`implementation/README.md`](implementation/README.md) (the code-structure braindump) and [`implementation/bugs.md`](implementation/bugs.md) (the full bug diary) so everything a grader, or future-us, needs to understand *what we built, why we built it that way, and what still hurts* lives in one place. Both original files are left untouched at their old paths for anyone who wants the per-folder version.

Table of contents:
- **I.** The Prophecy: Paper Selection & Sources (>ᴗ•)
- **II.** The Grimoire: Architecture & Code Structure
- **III.** The Build Log: Implementation Decisions
- **IV.** Setup: How to Reproduce This Quest
- **V.** Bug Alarm: The Full Diary of Suffering *wiu wiu wiu*
- **VI.** Sources: Assets & Tools
- **VII.** Limitations: What Remains Unconquered
- **VIII.** Farewell

---

## I. The Prophecy: Paper Selection & Sources

For the Paper selection we looked for papers that have the following attributes:
- doable in two weeks
- an interesting interaction technique
- a sufficient technique (not too easy and not too hard)
- possibility to make a creative/funny replication for our beloved tutors (>ᴗ•)

With these categories we selected 10 papers and discussed their advantages and disadvantages. The winner is ...... not one but two papers??? (O.O)

- **Harmonionz: Rescue The Planet:** A Voice Visualizing Game that Matches Pitch with Color (pitch-to-color mapping in a collaborative voice game) by Kim et al., 2021
- **Color Singer:**  Composing Music via the Construction of LEGO Blocks with Various Colors (color-to-pitch mapping using LEGO and a light sensor) by Lu et al., 2024

> A shoutout goes to the "interactive paper tearing" paper (Lejemble et al., 2015) because it is so funny and hilarious. Unforunately not posible in the "two weeks" since *whisper* dont tell anyone, but we also have multiple other courses *whisper* (Now you need to *gasp*).

But why now two Papers? Lets give you some Background first of the other papers that got killed one by one during our conquest process...

### The unloved unchoosen Papers
From our initial pool, we quickly realized that many papers failed our "two weeks, one laptop, zero lab hardware and not being able to recycle much of old ITT assignments" test:
- Some systems relied on special hardware setups, like multi-touch tables or custom sensors that we didn't build in the ITT course.
- Others were complex full games / systems with multiple scenes, narrative structures, custom audio pipelines, or machine learning components that would be hard to replicate in 1–2 weeks.
- A few were "this is super cool, but probably a whole project course on its own" in terms of implementation detail.

**For Example:**
The paper tearing simulation with sound models realistic tear geometry and procedural tearing sounds based on hand motion and cone-shaped deformations of paper.
- Super cool, super funny, but too much (╥﹏╥)
- So the judges ruled and the verdict was: "Love you, but you belong in my private side-projects folder, not in the 2-week ITT graveyard."

**The rest of the fallen, for the record** (full PDFs live in [`unchoosen_papers/papers/`](unchoosen_papers/papers/)):
| Paper | Why it didn't make the cut |
|---|---|
| Lejemble et al., 2015: *Interactive procedural simulation of paper tearing with sound* | Gorgeous, but a full physics + procedural-audio project on its own |
| Hagerer et al., 2017: *VoicePlay: An affective sports game operated by speech emotion recognition* | Needed emotion-recognition models/training data we didn't have two weeks for |
| Wu and Rank, 2015: *Spatial Audio Feedback for Hand Gestures in Games* | Cool gesture angle, but hinges on spatial-audio hardware setups we don't have |
| Kim et al., 2023: *Bubbleu: Exploring AR Game Design with Uncertain AI-based Interaction* | AR headset dependency, not reproducible with "one laptop" |
| McPherson and Gierakowski, 2013: *The Space Between the Notes: Adding Expressive Pitch Control to the Piano Keyboard* | Requires custom piano-keyboard hardware modifications |
| Costanza, Shelley and Robinson, 2003: *Introducing Audio D-Touch: A Tangible User Interface for Music Composition and Performance* | Tangible-marker + camera rig, more hardware build than interaction-technique replication |
| Huang et al., 2026: *Not Human, Funnier: How Machine Identity Shapes Humor Perception in Online AI Stand-up Comedy* | No real interaction technique to replicate, more of a perception study |
| Weinberg et al., 2025: *Why So Serious: Exploring Timely Humorous Comments in AAC Through AI-Powered Interfaces* | Same issue, study-shaped rather than technique-shaped |

Now my fellow readers, we reached the storytime of: "the Prophecy of the two choosen Papers"

### The choosen Paper(s)
Once upon a time, in the far-away kingdom of ITT,<br>
two humble students set out on a quest:<br>

>_Find a paper that is doable in two weeks and still impresses the local tutor-wizards_<br>

They searched the lands of CHI, PLAY, and mysterious PDF scrolls,<br>
fought off dragons named "required hardware" and "way too many user studies",<br>
and finally discovered two magical artifacts:<br>
- The Harmonionz scroll, which whispered the secret of turning voice pitch into color and making players sing to save a planet.
- The Color Singer relic, forged from LEGO blocks and light sensors, which could turn rainbow-colored bricks into actual music.<br>

The prophecy spoke of a rare alignment:
> "When pitch meets color and color meets pitch,
> two papers shall stand where one assignment is required."

So the brave students proposed a daring spell:
- Take the Harmonionz magic and build a pitch => color prototype
- Extend it with a color => pitch ritual, inspired by Color Singer, to show that the same cross-modal magic can be cast in both directions

But alas, in this land no hero may choose their own destiny.<br>
For above them sits the Council of Tutors, wise wizards of replication,<br>
who hold the ultimate power to proclaim:<br>

- "Yes, this is a noble replication + extension!"
=> and Harmonionz becomes the Chosen One.

- Or: "Nay, thou hast strayed too far from the original scroll!"
=> and Color Singer is crowned as the official quest paper, with a pure color-to-pitch implementation and fewer side-quests.

And so, our heroes have carefully explained both paths, placed their candidate scrolls on the altar of the Discoed Chat, now patiently awaiting the judgment of the tutor-wizards.

### The verdict, at last

The Council spoke, and **Harmonionz was crowned the Chosen One**. And so our heroes got to work forging their own small kingdom: <br>
A two-player realm where 
- **Player One, the Singer**, wields their voice as magic: pitch becomes color, color unlocks gates and a held note charms shields and treasure chests into obedience
- while **Player Two, the Support**, wields a pinch of the hand as their sceptre, dragging shields into place, clicking crystals awake and aiming a gun at whatever flies at them. 

Neither hero can finish the quest alone: <br>
The overworld leads to a dungeon of color-matched combat, which leads to a treasure chamber of color-matched chests, which finally frees the dragon at the end. Full mechanical detail of that kingdom is in Section III below and the entire "how we actually built it" gore is in Section V.

_The prophecy is fulfilled. What follows is the record of how it was built, decision by decision, bug by bug._

PS: If you wanna extend your medieval tongue, cast following links into the world wide webs:
(https://www.etymonline.com/search?q=unfortunately)
(https://thehistoryofengland.co.uk/resource/glossary-of-medieval-terms/)

---

## II. The Grimoire: Architecture & Code Structure

*(merged from [`implementation/README.md`](implementation/README.md))*

### Why the files inflation?!
Since a lot of code was being duplicated and it's better to have own files for stuff for debugging purposes, structure and clean code (not like last assignment, it hurt really our soul but for 4 points we wouldn't split everything .... but for 25?! HELL YEAH).

Once the file count crept past 15 flat files, we grouped them into packages so the folder is still readable at a glance instead of one giant BUCHSTABENSUPPE list:
- `states/`: the 5 screens + `state_manager.py`, which does the actual switching between them
- `entities/`: things that act every frame: players, enemy, shield
- `input/`: the raw device readers (`audio_input.py`, `gesture_tracking.py`), no game logic, just exposes current values
- `world/`: everything the map contains or displays: tilemap, gate, interactables, hud, buttons

Advantages:
- **overview**: `ls` on `implementation/` now shows 4 folders + `main.py` + `config.py` instead of +20 files mixed together
- **grep-ability**: "where's the enemy logic" -> `entities/`, no guessing between +20 flat filenames
- **import clarity**: `from world.gate import Gate` tells you exactly what kind of thing you're pulling in, a bare `from gate import Gate` doesn't
- **merge conflicts**: two people working on e.g. `states/state_dungeon.py` and `entities/enemy.py` almost never touch the same file by accident

The `__init__.py` files in each package are (currently) just a super fancy comment. They make Python treat `states/`, `entities/`, `input/`, `world/` as importable packages (`from states.state_manager import ...`) instead of just random folders. They don't need any code in them to work, we just used them to document what each package is for (did this so it doesn't look thaaat empty haha).

### Screens
(logic mostly copied from Assignment 6: gesture_application, Melanie & Marina and then duplicated into corresponding files since everything is kinda the same)

| # | State | What happens |
|---|---|---|
| 0 | Start menu | P2 clicks a button, P1 colors the button, like a tutorial |
| 1 | Overworld | Walk to the dungeon gate and open it |
| 2 | Dungeon | Combat against enemies |
| 3 | Treasure chamber | Solve the color-matching chest puzzle outside the dungeon |
| 4 | Game over / won | Displayed depending on where you die, or after state 3 if passed |

---

## III. The Build Log: Implementation Decisions

How did we implement all of that?

### Audio and Color Mapping
**Audio**: We used a microphone to capture the audio input from the user. The audio is then processed to extract the pitch and frequency information, which is used to determine the corresponding color or musical note.

**Color Mapping**: We implemented a mapping between pitch and color, allowing users to see visual representations of the audio input. The mapping is based on the frequency of the audio signal, with different frequencies corresponding to different colors. It follows the implementation of the Harmonionz paper, where specific frequency ranges are associated with specific colors. During the coding, it was very hard to actually hold a pitch (and therefore color), so we decided to reduce the time to hold the pitch to 0.5 seconds, which is a lot easier to achieve for the user.

**Shield modes**: The shield can be steered by P1's voice in two ways P2 picks between via a HUD button — coloring it (hold a steady pitch around 2s, same lock logic as the gate) or growing it (scream louder, tracked as a `_size_peak` over a 3s window). This lets one voice input control multiple properties without needing separate instruments.

### Gesture Recognition
We used mediapipe to implement gesture recognition as in previous assignments. For the game it was not exact enough, so we patched it: instead of feeding the raw pinch signal straight into the game logic, we turn a detected pinch into an actual OS-level mouse click (press on pinch, release on release), with the cursor position smoothed via an EMA to stop the visible shaking from noisy per-frame landmarks. This also meant we could reuse pyglet's existing `on_mouse_press`/`on_mouse_drag`/`on_mouse_release` handlers, so the gems and gates don't care whether they got clicked by a real mouse or a pinch (same code path either way).

The trickiest part was that a single pinch-distance threshold made the pinch check flicker true/false whenever fingers jittered near the line, which fired press/release/press/release instead of one clean "held" click. We fixed it with two thresholds instead of one: entering a pinch requires the fingers to get closer together, while leaving it tolerates them drifting a bit further apart before letting go. That little bit of hysteresis was enough to make dragging feel stable (>ᴗ•)

### Sounds
As for every good game, we needed sounds. Not only because we didn't want to learn for our other exams, but for the feedback for our beloved tutors. We play a click sound when the fingers connect and disconnect, so the user "feels" the pinch gesture.
Additionally, a sound is played when the user hits the crystal correctly. Adding sound was rather easy (Thanks Pyglet on letting that slide *side eye*).

Background music was created by us and was purely because Machine Learning is hard and music is not. ♪(๑ᴖ◡ᴖ๑)♪

---

## IV. Setup: How to Reproduce This Quest

*(new section, because the grading rubric demands a rebuildable ritual, not just vibes)*

1. **Summon a Python environment** (3.10+ recommended) and install the dependencies:
   ```
   pip install -r requirements.txt
   ```
2. **Gather your hardware**: a working webcam (for the mediapipe hand/pinch tracking) and a working microphone (for the pitch/volume tracking). No special sensors, no lab hardware, per our own paper-selection rules.
3. **Enter the dungeon folder**:
   ```
   cd implementation
   python main.py
   ```
4. **Controls**:
   - P1 (Singer): `WASD` to move, sing/hum into the mic to color gates, shields, gems and chests.
   - P2 (Support): `arrow` keys to move, pinch in front of the webcam to click/drag (acts like a real OS mouse click), `L` to toggle the gun.
5. Use `quick.py` if you want to jump straight to a specific state (e.g. `treasure`) for testing instead of replaying the whole start-menu -> overworld -> dungeon walk every time.

If the camera refuses to start: it's almost certainly not your fault, see the webcam haiku in Section V.

---

## V. Bug Alarm: The Full Diary of Suffering *wiu wiu wiu...call an ambulance (but nor for us... wait.. definetly for us)*(╥﹏╥)

*(merged in full from [`implementation/bugs.md`](implementation/bugs.md), kept verbatim so the "challenges encountered + how we solved them" record stays intact)*

A living diary of everything that made us swear at pyglet while building out the game (start menu -> overworld -> dungeon -> treasure chamber -> end screen, phases 1 through 3, plus whatever broke in between while actually playtesting it). In the same spirit as the rest of this document: braindump, not a bugtracker with tickets (ง -_-)ง

### Phase 0: Prepstage

**Nowhere sprites**
So a problem we encountered was how to use tilemaps. Since in e.g. Unity you have a Tilemap editor (just load your stuff in the right format and voila you can "draw" your map as you wish and put "objects" in and collision etc.). We totally forgot that we use pyglet ( ._.)

So we searched in the world wide webs and came across this gem: https://www.mapeditor.org

> "Tiled is a 2D level editor that helps you develop the content of your game. Its primary feature is to edit tile maps of various forms, but it also supports free image placement as well as powerful ways to annotate your level with extra information used by the game. Tiled focuses on general flexibility while trying to stay intuitive."

And with that we solved our Tilemap problem, only problem left is to learn how to use it (  ._.)

**bug alarm**

### The Tilemap Armageddon

**WHY WHY WHY**
<br>
So apparently when you have "infinite" on, pyglet can't handle that, but _nuh uuuuh_ we needed to uncheck it in Tiled but that would be too easy (something with the sprite layout was wrong so it took 30 minutes to fix that with shitty random online threads) and in the end the creator of the tiles was just too lazy to put water tiles under the wave tiles so we colored random tiles that were not in the layer and that's why we couldn't select the whole map, shift the offset, uncheck infinite and use it in pyglet.
<br>
Lesson learned -> using a real game engine with sprite editor in future, no more pyglet.
<br>
Also, because of ratio, we added 6 additional tile columns left and right on each side ._.
<br>

### Phase 1: Start Menu + Overworld

(Filled in as we actually hit things, not written in advance like some kind of jesters heehehehehe)

**The gesture cursor lies to you**<br>
`gesture_tracking.py`'s `cursor_x`/`cursor_y` are camera-frame coordinates dressed up as screen coordinates, NOT pyglet-window coordinates. If you naively compare them against a button's pixel position you will hit things that aren't there and miss things that are.<br>
**The Fix:** Don't touch `cursor_x`/`cursor_y` at all for hit-testing. The pinch already drags a real OS mouse cursor and does a real OS click, so pyglet's own mouse events already arrive in correctly-mapped window coordinates for free. Moral of the story: let the OS do the coordinate math, it's better at it than we are (╥﹏╥)

**"Click and drag" is one word away from being free**<br>
Turns out pyglet's `on_mouse_drag` only fires while a button is physically held, which is exactly what a held pinch produces. So `Pushable` didn't need any custom gesture-drag-detection logic, it just listens like a bog standard mouse drag and gets pinch support as a side effect. Found this out completely by accident.

**A Haiku About Webcam Pain** (Yes, a literal haiku so you get the joke)<br>
*Webcam will not start*<br>
*Five times I open the port*<br>
*Now it hates me, great*<br>

**The bug:** "Before phase 2 our webcam doesn't start at all". We noticed our `gesture_tracking.py` was scanning camera indices, opening and releasing each one just to see if it exists, then double-checking, then opening a *third* time for the tracking thread. We were doing up to 5+ real `AVFoundation` capture-session open/release cycles back to back. AVFoundation's session teardown isn't instant, so slamming it leaves the camera in a "nope, not now" state. Classic case of "it works" ≠ "it works when you do it five times in a row real quick".<br>
**The Fix:** Ripped out the scanning and confirm-reopen entirely. `select_camera()` now just asks for an index (default 0) and returns it, opening the camera exactly once.<br>

**The pinch that clicked absolutely nothing**<br>
**The bug:** Terminal happily prints `pinch=True` when you pinch, but nothing happens in the game. Turns out `hand_loop()` maps the hand landmark into screen coordinates using a hardcoded 1920x1080 canvas glued to the top-left corner of the desktop (0, 0). Our game window definitely wasn't at (0, 0). The click was real, but it landed on phantom coordinates.
**The Fix:** `hand_loop()` now takes `origin_x`/`origin_y` in addition to `window.width`/`window.height`. We feed it `window.get_location()` so it knows where the actual game is.

### Phase 2: Dungeon Combat

**A shield glued to the dungeon's center tile**<br>
`shield.py` originally just planted itself at a fixed center coordinate and never moved again. P1 could be standing in a corner and the shield would still be chilling in the middle of the room doing absolutely nothing for them. Added `Shield.follow(x, y)` and called it every frame with P1's position.<br>

**"C is P2's key" needs to be true at the routing level**<br>
P2's gun toggle (`C`) was quietly funneling straight into `Player1.handle_key_press`, vanishing into a no-op with zero feedback. Gave `Player2` its own handler and split the dispatch explicitly. Failing silently is the worst kind of bug to chase later. Update 2: we changed (`C`) to (`L`) since it would be too much hassle (an understatement, because it was freaking annoying haha) for P1 to also initiate that, so P2 now does it themselves.<br>

**Testing bullets through obstacles is a coin flip**<br>
Our P2-shoots-an-enemy test kept failing. Spent a bit convinced our math was wrong before realizing the bullet died exactly on top of a static obstacle block. Not a bug, just a test that accidentally drew a straight line through a wall. Moved the obstacles out of the way for that test.<br>

**An already-dead bullet trying to update itself**<br>
Call `Projectile.destroy()` and then call `.update(dt)` before it's filtered out of the list and pyglet throws an `AttributeError` because the vertex list is gone. Cheap fix: `update()` just returns immediately if `self.alive` is already `False`.<br>

**P1 quietly redecorating itself**<br>
**The bug:** `Player1.update()` had leftover code that changed P1's color based on audio pitch. Once `Gate` and `Shield` got their own live-color tracking, nothing looked at P1's color anymore. It just kept flickering through the palette purely so anyone watching could go "wait why is P1 changing colors, nothing's even nearby".<br>
**The Fix:** Deleted the audio-reactive line and unused imports. P1's rectangle is just `config.P1_COLOR` now, full stop.<br>

**Hint labels assuming you already knew who does what**<br>
Strings like "sing its color" or "drag the crystal" are completely ambiguous when two players are staring at one screen. Every one of those strings now explicitly says `P1:` or `P2:` up front.<br>

**"Hardcoding the easy note" made things harder**<br>
We thought forcing the tutorial to use the lowest frequency bucket (`config.SHIELD_COLORS[0]`) would be a nice gimmick so P1 wouldn't have to hunt for a high note. EXCEPT that lowest bucket is 500-1125Hz, which is actually kind of high for natural speaking voices. Forcing literally every single attempt to require exactly that one bucket meant if it was your worst range, you were stuck every single time.<br>
**The Fix:** Reverted to `random.choice(config.SHIELD_COLORS)`.<br>

**The button/gate that never said what to sing**<br>
Players had to reverse-engineer the target purely from a live-updating swatch with no label and it would look "stuck" on a color instead of honestly saying "nothing detected right now" when P1 stopped singing. Added `config.SHIELD_COLOR_NAMES` so text hints can say "P1: sing GREEN", and resetting the color to a shared gray (`PITCH_SILENCE_COLOR`) when nothing is detected.<br>

**The tornado that only spun up because macOS wasn't looking closely enough**<br>
Found this one doing a full-repo audit. Code loaded frames from `"assets/tornado/"` (lowercase), but the folder on disk was `assets/Tornado` (capital T). APFS (macOS's default filesystem) is case-insensitive, so it worked fine for us. It would have hard-crashed the moment this ran on Linux.<br>
**The Fix:** Pointed the calls to the real casing, `assets/Tornado`.<br>

**The gate gets a sprite and preps for melody**<br>
The gate finally got a looping sprite instead of rendering off a base rectangle. Also left the color-matching logic behind a clean `_lock()` method so it could later be swapped for a short sung note sequence check without breaking everything downstream.<br>

**The entry gate that ate itself**<br>
**The bug:** Walking into the dungeon's entry crystal to start the fight threw an `AttributeError`. If P2 had already walked in, and then P1's entry completed the pair, `Gate.try_enter` fired `on_unlock` synchronously. `_start_combat` sets `self.gate = None` immediately, but the very next line then tried to call `self.gate.try_enter` on nothing.<br>
**The Fix:** Read `self.gate` into a local variable once at the top and use that local for every call in the block instead of re-reading `self.gate` after each one.<br>

**Walking into an unlocked gate did nothing**<br>
We required pixel-perfect overlap between the player's bottom-left corner and the gate's pixel box. Players only ever step in 64px jumps, so exactly *one* tile satisfied that point check. Missing it by even one step meant walking straight through the gate forever. Swapped the point check for an actual rect-vs-rect overlap.<br>

**The crystal isn't a door**<br>
The dungeon's entry crystal quietly inherited the walk-in-together mechanic from doors. Gave `Gate` a `walk_in_required` flag. When `False`, coloring it triggers the unlock immediately.<br>

**The gem stopped freezing mid-sing, and learned to be dragged**<br>
Gems froze on a single frame while listening to P1 sing. Rewrote it to swap looping color folders. Also bolted on `Chest`'s drag pattern, so coloring it unlocks dragging.<br>

**Pinching could click a gem but couldn't drag it (Rounds 1 & 2)**<br>
Holding a pinch to drag did absolutely nothing. macOS treats a moved-while-button-down cursor as `kCGEventLeftMouseDragged` (type 6), but we were constantly posting plain `kCGEventMouseMoved`. `on_mouse_drag` literally never fired.<br>
**Fix 1:** Swapped to posting the proper event type.<br>
**Fix 2:** The drag event fired, but always carried `delta=(0,0)`. Synthetic OS events don't carry native deltas, so we explicitly computed and injected `delta_x`/`delta_y` into the event fields.<br>

**P1 and P2 stopped being plain colored squares**<br>
Real 16x20 pixel-art sprites landed! `GridActor` now loads idle and walk cycle frames based on the current movement direction. P2's pinch-highlight lost its old brightness trick and now drops the blue channel so it doesn't wash out the art.<br>

**The overworld got walls**<br>
Added real per-tile collision via Tiled's `blocks` layer. Almost blocked the whole map initially because the `water` layer was a full-map base layer sitting underneath all the land. Had to search for new nearest-open-spots for all hardcoded spawns/gems because they landed inside solid walls.<br>

**Tilemap animations**<br>
Animated tiles (fire, water) only showed their first static frame. Built a `pyglet.image.Animation` cached per-gid so they actually loop forever now.<br>

**Dungeon collision, capped enemies, right-sized players**<br>
Players looked oversized, so we shrank `PLAYER_RENDER_SCALE` down to 0.5. Gave the dungeon real wall collision too, which immediately ate our hardcoded bullet obstacles. Capped combat enemies at exactly 3 instead of randomly rolling up to 10.<br>

**The enemy stopped being a colored square too**<br>
Enemies are now an animated 4-frame flying bat loop. Had to pass `anchor_center=False` to the animation loader because the physics hitboxes are bottom-left anchored, otherwise hits would visually miss.<br>

**Bullets never actually knew the dungeon had walls**<br>
Bullets flew straight through actual stone walls that players couldn't cross. `_resolve_bullets` now checks `self.tilemap.is_walkable()` against a box centered on the bullet.<br>

**The collision box was the size of the tile**<br>
Players kept getting stuck even on walkable tiles because the 64px invisible box was huge compared to the tiny 16x20 sprite. Shrank the collision box down to match the real character's rendering dimensions.<br>

**Shield loses its stopwatch, gun learns to sing**<br>
Cut the shield's duration timer entirely. Now it just tracks a `_size_peak` for 3 seconds. Also gave the gun the exact same hold-steady-for-2s color-locking treatment as the shield instead of its old manual toggle.<br>

**One bullet speed wasn't enough**<br>
Split `config.BULLET_SPEED` into `PLAYER_BULLET_SPEED` and `ENEMY_BULLET_SPEED` so P2 shoots faster than what's coming back at them.<br>

**The missing floor tiles were never a Tiled problem**
Marius noticed `earth_floor` tiles missing. Not a Tiled bug, just Pyglet batching sprites from the same texture together with zero draw order, causing layers to interleave randomly. Created distinct ordered child groups for every layer.
**PLOTWIST:** <br>
IT IS A TILED BUG! But not because of Tiled directly but because how Tiled works (We think). So I could change the position of a broken sprite by deleting in pyglet that sprite(coloring??) and redrawing it BUT this helped to push it kinda only down. So now we think that Pyglet + Tiled has same weird unusual edge case why 3 Tiles disappear and we can't fanthom why exactly. So this is still an issue and since time is running against us it is an issue for our future selfs if we ever touch this repo again. Sucks to be you future Marius and Marina (˶˃𐃷˂˶) <br>

**P2's gun was secretly a hitscan-on-enemy click**<br>
The gun wasn't free-aiming. It looped every enemy and only fired if the pinch landed *exactly* inside a hitbox rect. Dropped the loop and just let P2 shoot a projectile aimed straight at the clicked point.<br>

**The gate needed multiple pinches**<br>
The gate visibly jumped 30px when clicked. The idle loop was center-anchored, but the listening image was bottom-left anchored. So the *rendered* gate drifted away from its invisible click target. Fixed anchors so `sprite.x/y` are identical across states.<br>

**Bullets now actually point where they're going**<br>
Stole the `atan2` math from the Steering Law assignment to rotate sprites toward their travel direction. Just had to reverse it for Pyglet's y-up space (`-degrees(atan2(vy, vx))`).<br>

**Unwinding Group 1 one layer at a time**<br>
Split the dungeon collision into 4 specific named layers (`walls_top`, `walls`, etc.), which forced us to move yet another hardcoded obstacle that got swallowed by `walls_back`.<br>

**Gate walk-in box shrinkage**<br>
Used the new `collision_box()` for gate entries so players don't trigger the walk-in from 55px outside the sprite.<br>

**The shield's pinch-to-listen step was missing entirely**<br>
You couldn't drag the shield after changing colors. The real bug was that the shield needed a `listening` flag so P1 screaming before P2 pinched it would do nothing. You now have to explicitly pinch to arm it before singing.<br>

### Phase 3: Treasure Chamber + End-State Metrics

**Deciding what counts as a "pitch attempt"**<br>
Defined one "attempt" as one sample per frame where P1 is actively singing during a *real* color-match check (Gate/Chest locks). The Shield and Gun were left out since they just live-track with no fixed target.<br>

**The chest slot markers are fully transparent**<br>
The chest markers were drawn with an `(0,0,0,0)` color fill. Just flagged it for review before assuming it looks right.<br>

**The treasure chamber finally gets its own room**<br>
Swapped the flat rectangle background for an actual `treasure.tmx` tilemap. Moved the 3 target slots directly in front of the fenced dragon, left-to-right.<br>

**The slot markers were the last spoiler**<br>
Slot markers were drawn in the chest's actual `target_color`. We swapped them to a flat black outline so they only say "a chest goes here", forcing you to actually sing to find the answer.<br>

**Colors weren't actually random**<br>
We randomized chest colors, which meant two chests could easily share a color. That broke the puzzle logic because the solve order assumed the first chest physically lived on the left. Added an independent shuffle for the slots too.<br>

**Snapping into place was itself the tell**<br>
A chest only snapped when dropped near its *correct* slot. Drop it anywhere else and nothing happened. That basically told you the answer immediately without actually guessing.<br>
**The Fix:** Chests now snap to *any* marked slot when dropped close enough, right or wrong. If it's the wrong slot, `_reset_wrong()` bounces the chest back to its spawn point, uncolored, and P1 has to sing it all over again like a peasant.<br>

**Dragging after coloring didn't work if the pinch never let go**<br>
**The bug:** Pinch and drag didn't work right after a chest's color locked in. `on_mouse_press` only set `grabbed = True` if the chest was *already* colored when the press event fired. If you hold the pinch continuously while singing, there is no second press event, so `grabbed` never flips.<br>
**The Fix:** Added `Chest.note_still_pressed(x, y)`. If the chest just locked its color, isn't grabbed, and the point is still inside it, it auto-grabs it right then instead of waiting for a press event that a continuous hold will never produce.<br>

**The reveal waits for all 3**<br>
Instead of telling you immediately if a chest drop was correct, you have to place all 3 chests first. If any are wrong, it scatters the whole group to new random coordinates.<br>

**The start/end screens Downloads landmine**<br>
**The bug:** `startscreen.tmx` and `endscreen.tmx` crashed on load with a `FileNotFoundError` pointing to `../../../../../Downloads/...`. Tiled saves image paths relative to where the `.tmx` lived at the time. These two were clearly built straight out of a Downloads folder and the PNGs never moved over. It would have broken instantly for anyone else. Dataset drama making a comeback!<br>
**The Fix:** Copied the 20 distinct images into `assets/chamber/` and rewrote the paths down to plain filenames.<br>

**One font, everywhere**<br>
Forced everything to use `Play-Regular.ttf`. Also shoved the Start/End screen buttons down to `y=100` so they aren't awkwardly sitting on top of everything else.<br>

**Player collision shrunk again & Shield continuous grab**<br>
Shrunk the player collision box again to exactly 19.2x19.2 across all maps regardless of scale. Also applied the exact same continuous-hold `note_still_pressed` fix we built for `Chest` to the `Shield`.<br>

**Quick.py**<br>
Added a small `quick.py` script to directly load states (like `treasure`) so we can skip the start menu and dungeon walk cycles during testing. This script felt so liberating because we just wanted to see if e.g. the tilemap looks good and needed to do eeeeeverything again and again and again.... now we got PTSD.<br>

**dungeon.tmx's "3 blank spots"**
Spent forever investigating 3 "blank spots". Turns out there were no missing tiles; it was just a deliberate stylistic choice to use clean `Floor` tiles in the boss room instead of the speckled `earth_floor`. There are still 3 spots that swapped location after "ficing" it, but we can't seem to find them maybe Monday is a better day.... moday wasn't a better day but as stated earlier that is a problem of potentially future Marius and Marina ദ്ദി(ᵔᗜᵔ) <br>

**Shield buttons renew, not retire**<br>
Buttons originally became permanently disabled one-shots after locking. Rewrote it so P2 can pinch the button again to redo the scream/sing window instead of being locked out forever.<br>

**Treasure chest puzzle: right guesses stick now**<br>
Scattering *every* chest back to square one on a wrong guess made it impossible if chests had duplicate colors. Changed the logic to permanently lock in any chest placed in its correct slot, only scattering the wrong ones (as it should have been like some fixes ago, but because of changing stuff it broke and needed to be fixed again).

**Dungeon combat cleanup & Gem deletion crash**<br>
Mid-flight enemy bullets would just freeze in the air when the phase flipped to cleared. We added cleanup to destroy them properly.
*However*, deleting the start-combat gem synchronously inside `on_update` caused an immediate `AttributeError` on the very next line because `self.gem` was suddenly `None`. We had to add fresh `is not None` guards to protect mid-frame self-deletions.<br>

---

## VI. Sources — Assets & Tools

*(merged from [`implementation/README.md`](implementation/README.md))*

### Assets
- dungeon: https://free-game-assets.itch.io/free-2d-top-down-pixel-dungeon-asset-pack
- chapell: https://craftpix.net/download/100511/
- dungeon2: https://craftpix.net/download/80859/
- ruin: https://craftpix.net/download/107610/
- https://kenney.nl/assets/tiny-dungeon
- https://opengameart.org/content/gem-icons-0
- projectiles: https://pimen.itch.io/magical-animation-effects
- tornado: https://foozlecc.itch.io/pixel-magic-sprite-effects
- characters: https://zerie.itch.io/tiny-rpg-character-asset-pack, https://oboropixel.itch.io/characters-animations-asset-pack, https://pixelserial.itch.io/rpg-top-down-character-asset-pack
- player: https://farm-animal.itch.io/character-pack
- enemies + dungeon: https://pixel-poem.itch.io/dungeon-assetpuck
- controller + keyboard: https://vryell.itch.io/controller-keyboard-icons
- treasure: https://pixelserial.itch.io/rpg-pixel-art-chests
- gems: https://drxwat.itch.io/pixel-art-diamond
- portal/gate: https://pixelnauta.itch.io/pixel-dimensional-portal-32x32
- bat: https://purplecatgamestudio.itch.io/bootiful-beasts
<br>
Our best friend for sprite cutting: https://ezgif.com/sprite-cutter

<br>

Since some assets weren't pre-cut, and of course Tiled was not intuitive (and honestly we didn't want to invest too much time to learn Tiled perfectly), we did what all great developers do: we googled "online free sprite cutter". This was easy and intuitive to use:
1. Select "Sprite sheet cutter"
2. Upload Image
3. Select cutting method "By number of columns/rows"
4. Insert those numbers by counting (obviously)
5. Click Cut
6. Then export it!
<br>
This saved us sooooo much time since we have so many sprites haha.
<br>

**Disclaimer:** As you can see (while looking at the sources) some sprites have multiple colors (red, green, blue, yellow) and may even differ from the original. You probably think nothing about it, but we'll tell you anyways! We used a not-pirated version of Lightroom to change the colors into the colors of our pitches:
1. Import all sprites into the super-fully-legal Lightroom copy
2. Go into Develop Settings
3. Do some color-theory magic on one image
4. Select all images (first the already color-graded one)
5. Apply synchronize (now all have the same color grading)
6. Export it to the chosen folder (IMPORTANT: as PNG for transparent background!!)

---

## VII. Limitations: What Remains Unconquered

Even a fulfilled prophecy leaves cursed corners in the map. No wise kingdom hides its curses from the Council, so since no knight, wizard, or student volunteered to read this decree aloudthe court jester has been dragged in front of the tutor-wizards to do it instead. He clears his throat, unrolls the scroll, and begins:

> "Hear ye, hear ye, wizard-tutors most wise! Before ye raise the grading-sceptre, know that this kingdom, though noble, is not without its **lingering hexes**:"

- **The One-Laptop Curse.** Both heroes share a single webcam, a single microphone and a single keyboard, upon a single laptop-throne. There is no long-distance sorcery (read: no networked multiplayer), and the microphone-oracle can only hear one voice at a time, should both heroes sing at once, the oracle grows confused and the pitch-magic falters.
- **The Fickle Oracle Curse.** The pitch-to-color prophecy only speaks clearly with a decent microphone-crystal. A raspy voice, a noisy tavern, or a naturally "unsingy" throat all make the color-magic harder to hold. The curse persists, only weakened (see the "Hardcoding the easy note" incident in Section V for the full tale).
- **The Shy Hand Curse.** The hand-reading familiar (mediapipe) needs good light and a hand that stays within view of its crystal ball. If the hand wanders off-screen, the pinch-magic grows unreliable and there is no backup spell if the webcam-crystal refuses to wake at all (see the AVFoundation haiku, that camera hated us long before this curse was written down). It worked eerily well on our own devices, so we humbly await word from lands without Mac-shaped thrones.
- **A handful of minor gremlins**: the treasure chamber's slot-markers were sealed with a fully invisible ink and never properly re-inked, and the dungeon map still hides 3 "blank tiles" whose true location we lost somewhere around 2am (see Section V for the full ghost story).
- **No royal test suite guards the whole quest.** A few individual trials are tested (e.g. "does the arrow strike the beast"), but no single spell verifies the entire start-menu -> overworld -> dungeon -> treasure -> end journey end to end; most of that verification was two tired students playtesting it themselves, repeatedly, at odd hours.
- **The Fullscreen Curse was left unbroken on purpose** (see [`toDo`](toDo): "scaling fullscreen (the absolute last thing todo)"), partly because it doesn't touch the core interaction technique, and partly because it is, as usual, a suspiciously Mac-specific curse.
- **No external-microphone blessing was ever cast.** It was noted on our pre-showcase scroll as a nice-to-have, but the game still assumes the laptop's built-in ear.

The jester lowers the scroll and, sensing the wizard-tutors' stares, decides this is the moment for a joke:

> **Jester:** "Why did the knight refuse to sing at the gate?"
> **Jester (answering himself, since no one else will):** "Because every time he held the note, the tutors said his execution was a little... *pitchy*."
>
> *(silence)*
>
> "...Please don't behead me for that one, wise wizards. I only replicate jokes, I did not invent the pun."

None of the curses above stop the core interaction technique from working pitch-to-color and pinch-to-click both function exactly as the prophecy demanded, but a longer quest (more than two weeks, fewer other exams) would smooth out every edge listed above.

---

## VIII. Farewell

And so, dear reader, this concludes the chronicle of our two-week quest: from a pile of 10 candidate scrolls, through a prophecy that split into two, down to a kingdom of singing crystals and pinching heroes. May your webcam start on the first try and may your shield always be the right color when the bullet arrives.

_~Marius & Marina, July 2026_
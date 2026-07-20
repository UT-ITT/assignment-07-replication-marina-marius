[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/JPHbh57K)

# Hear Ye, Hear Ye (｡•̀ᴗ-)✧

Gather round, weary traveler, for this is the **final README of the ITT semester**. No more assignments after this one. No more `git commit -m "pls work"` at 2am. Just this scroll, one last dungeon and a dragon waiting for its treasure.

Read on, for the quest is documented below in four parts: the **prophecy** (what this repo is), the **inventory** (what's inside it), the **herald's proclamation** (how to actually play the thing) and the **riddles** (because a proper medieval scroll never lets you leave without answering something first).

---

## I. The Prophecy: What is this repository?

This repo is our submission for **Assignment 7: Replicating Interaction Techniques** (25P) see [`assignment-07-Replication.pdf`](assignment-07-Replication.pdf) for the original decree from the Council of Tutors.

**The chosen paper:**
> Kim et al. (2021): *"Harmonionz: Rescue The Planet — A Voice Visualizing Game that Matches Pitch with Color"*

(scroll available at [`assets/paper/`](assets/paper/), alongside its almost-chosen twin, *Color Singer*, which lost the coin flip but is honored forever in [`documentation.md`](documentation.md))

**The MVP, in one incantation:** a local two-player, Pokémon-style pyglet game where **P1 sings** (pitch -> color, à la Harmonionz) and **P2 gestures** (mediapipe pinch -> OS mouse click/drag). Neither player can win alone:
- P1 colors gates, shields, chests and dungeon runes with their voice
- P2 drags, clicks and aims with a pinch. 
Together they cross the overworld, survive a dungeon and crack a treasure-chest puzzle to free the dragon at the end. Full quest log of *why* every decision happened lives in [`documentation.md`](documentation.md).

---

## II. The Inventory: What's in this chest?

| Path | What you'll find |
|---|---|
| [`implementation/`](implementation/) | The actual game. Run `python main.py` from inside this folder once `requirements.txt` is installed. Start menu -> overworld -> dungeon -> treasure chamber -> end screen. |
| [`implementation/documentation.md`](implementation/documentation.md) | Braindump on *how* the code is structured (`states/`, `entities/`, `input/`, `world/`) and *why* we split it that way. |
| [`implementation/bugs.md`](implementation/documentation.md) | A living diary of every bug that made us swear at pyglet. Phase 1 through 3, haiku about webcam pain included free of charge. |
| [`documentation.md`](documentation.md) | The full paper-selection saga, told medieval-style, plus the implementation write-up (audio/color mapping, gesture recognition, sound). |
| [`assets/paper/`](assets/paper/) | The chosen paper (Harmonionz) and its runner-up (Color Singer). |
| [`unchoosen_papers/`](unchoosen_papers/) | The graveyard of papers that didn't survive the "two weeks, one laptop, zero lab hardware" test. RIP paper-tearing simulation, we hardly knew ye (╥﹏╥) |
| [`figures/`](figures/) | Documentation figures. |
| [`Presentation.pdf`](Presentation.pdf) | The slides for the July 21st live demo. |
| [`requirements.txt`](requirements.txt) | `numpy`, `sounddevice`, `opencv-python`, `mediapipe`, `pyglet`, `pytmx`, summon these before summoning the game. |
| [`toDo`](toDo) | Our raw pre-showcase scratch notes, half in German, kept as-is for authenticity hehe. |

---

## III. The Herald's Proclamation: How to Play

*A herald steps onto the tavern table, unrolls a scroll far too long for the room, and clears his throat.*

> "HEAR YE, HEAR YE, good tutors and passersby! The Prophecy told you *what* this kingdom is, the Inventory told you *where* its treasures lie, now let the Herald tell you *how* to survive it, lest ye wander the overworld confused forever!"

### The Two Heroes, and their arts

| Hero | Moves by | Special arts |
|---|---|---|
| **P1, the Singer** | one tile at a time, WASD | Sing or hum into the mic to color gates/chests/shields; `E` to interact, `F` to summon the shield |
| **P2, the Support** | one tile at a time, arrow keys | Pinch in front of the webcam (acts as a real click/drag, mouse also works), `L` toggles the gun |

### The Five Halls, decreed in order

| Hall | What the Herald commands thee to do |
|---|---|
| **0:  Start Menu** | P2 pinches/clicks the start rune to wake it. P1 sings the requested color to charm it. P2 pinches it once more to pass through, a tutorial in disguise. |
| **1:  Overworld** | Walk to the dungeon's entry crystal. P1 sings its assigned color (or short melody) until it locks in, the crystal glows true and the dungeon awaits. |
| **2:  Dungeon** | Up to 3 foes descend. P1 summons the shield (`F`) and sings it into the *same color* as an incoming bolt to block it. P2 draws the gun (`L`), colors it the same singing way and and pinches an enemy to fire a matching-colored shot. Match colors correctly and the beast falls; mismatch, and *thou* takes the hit. Clear the hall to proceed, lose all 3 hearts, and it's game over. |
| **3: Treasure Chamber** | Three chests await, each needing its own sung color. P1 sings a chest true, P2 drags it onto its marked slot. Guess wrong and it bounces back uncolored, a peasant's fate. Place all three correctly and the dragon finally yields its hoard. |
| **4: End Screen** | Victory or defeat, the Herald reads thy final tally: time spent on the quest, pitches sung true versus attempted, bolts fired. Click/press onward to return to the Start Menu and try again. |

> *A herald's secret aside, whispered only to those on a tight schedule:* pressing `Enter` mid-hall skips to the next one early, and `O` in the dungeon ends the run in defeat, showcase shortcuts for when time is short, not part of the true quest. Use sparingly and tell no one. (¬‿¬)

With this decree, the cast is complete: a Prophecy, an Inventory, a Herald and still, one trial remains before you may leave this scroll.

---

## IV. The Riddles: a quiz before you pass

A proper medieval gatekeeper never lets you through without a trial. Answer honestly (to yourself, we can't actually check):

**Riddle the First:** *"I have no body, yet I have pitch. I have no hands, yet I open gates. What am I?"*
> Hover... no wait, this is markdown, there's no hover. It's **P1's voice**. Sing to it, it colors the world.

**Riddle the Second:** *"Two hands make a pinch, the pinch makes a click, the click drags a crystal, but who commands the pinch?"*
> **P2**, via mediapipe and a lot of hysteresis thresholds so the pinch stops flickering true/false like a haunted lightswitch. Ask [`documentation.md`](documentation/bugs.md) about it, it has *feelings* on the matter.

**Riddle the Third:** *"Why does the dragon guard treasure chests instead of gold?"*
> Because gold doesn't need to be sung into the correct color first. Duh.

**Bonus pop quiz** (◕‿◕✿): *How many capture-session open/release cycles does it take to make AVFoundation hate you?* Answer: **five**. We know because we did it by accident. See the haiku in [`documentation.md`](implementation/documentation.md) for the full tragedy.

---

## V. Farewell

And so, dear reader, tutors, classmate, or future-us doing spring cleaning. This marks the final scroll of ITT 2026. It has been an honor to swear at pyglet, hunt down a case-sensitive folder named `Tornado`, and teach two grown students how to sing to a crystal in front of a webcam.

Thus concludes the chronicle. Go forth, run `main.py`, sing badly, pinch confidently and may your shield always be the right color when the bullet arrives. (๑•̀ㅂ•́)و✧

_~ Marius & Marina, July 2026_

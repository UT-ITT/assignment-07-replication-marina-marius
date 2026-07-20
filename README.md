[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/JPHbh57K)

# Hear Ye, Hear Ye (｡•̀ᴗ-)✧

Gather round, weary traveler, for this is the **final README of the ITT semester**. No more assignments after this one. No more `git commit -m "pls work"` at 2am. Just this scroll, one last dungeon and a dragon waiting for its treasure.

Read on, for the quest is documented below in three parts: the **prophecy** (what this repo is), the **inventory** (what's inside it) and the **riddles** (because a proper medieval scroll never lets you leave without answering something first).

---

## I. The Prophecy: What is this repository?

This repo is our submission for **Assignment 7: Replicating Interaction Techniques** (25P) see [`assignment-07-Replication.pdf`](assignment-07-Replication.pdf) for the original decree from the Council of Tutors.

**The chosen paper:**
> Kim et al. (2021) — *"Harmonionz: Rescue The Planet — A Voice Visualizing Game that Matches Pitch with Color"*

(scroll available at [`assets/paper/`](assets/paper/), alongside its almost-chosen twin, *Color Singer*, which lost the coin flip but is honored forever in [`documentation.md`](documentation.md))

**The MVP, in one incantation:** a local two-player, Pokémon-style pyglet game where **P1 sings** (pitch -> color, à la Harmonionz) and **P2 gestures** (mediapipe pinch -> OS mouse click/drag). Neither player can win alone:
-  P1 colors gates, shields, chests and dungeon runes with their voice
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

## III. The Riddles: a quiz before you pass

A proper medieval gatekeeper never lets you through without a trial. Answer honestly (to yourself, we can't actually check):

**Riddle the First:** *"I have no body, yet I have pitch. I have no hands, yet I open gates. What am I?"*
> Hover... no wait, this is markdown, there's no hover. It's **P1's voice**. Sing to it, it colors the world.

**Riddle the Second:** *"Two hands make a pinch, the pinch makes a click, the click drags a crystal, but who commands the pinch?"*
> **P2**, via mediapipe and a lot of hysteresis thresholds so the pinch stops flickering true/false like a haunted lightswitch. Ask [`documentation.md`](documentation/bugs.md) about it, it has *feelings* on the matter.

**Riddle the Third:** *"Why does the dragon guard treasure chests instead of gold?"*
> Because gold doesn't need to be sung into the correct color first. Duh.

**Bonus pop quiz** (◕‿◕✿): *How many capture-session open/release cycles does it take to make AVFoundation hate you?* Answer: **five**. We know because we did it by accident. See the haiku in [`documentation.md`](implementation/documentation.md) for the full tragedy.

---

## IV. Farewell

And so, dear reader, tutors, classmate, or future-us doing spring cleaning. This marks the final scroll of ITT 2026. It has been an honor to swear at pyglet, hunt down a case-sensitive folder named `Tornado`, and teach two grown students how to sing to a crystal in front of a webcam.

Thus concludes the chronicle. Go forth, run `main.py`, sing badly, pinch confidently and may your shield always be the right color when the bullet arrives. (๑•̀ㅂ•́)و✧

_~ Marius & Marina, July 2026_

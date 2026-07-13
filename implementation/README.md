your implementation goes here

# braindump

## why the files inflation?!
since a lot of code is being duplicated and its better to have own files for stuff for debugging purposes, structure and clean code (not like last assignment, it hurt really my soul but for 4 points I wouldn't split everything .... but for 25?! HELL YEAH)

once the file count crept past 15 flat files, we grouped them into packages so the folder is still readable at a glance instead of one giant BUCHSTABENSUPPE list:
- `states/`: the 5 screens + `state_manager.py`, which does the actual switching between them
- `entities/`:things that act every frame: players, enemy, shield
- `input/`: the raw device readers (audio_input.py, gesture_tracking.py), no game logic, just exposes current values
- `world/`: everything the map contains or displays: tilemap, gate, interactables, hud, buttons

advantages:
- **overview**: `ls` on `implementation/` now shows 4 folders + `main.py` + `config.py` instead of 20 files mixed together
- **grep-ability**: "where's the enemy logic" -> `entities/`, no guessing between 20 flat filenames
- **import clarity**: `from world.gate import Gate` tells you exactly what kind of thing you're pulling in, a bare `from gate import Gate` doesn't
- **merge conflicts**: two people working on e.g. `states/state_dungeon.py` and `entities/enemy.py` almost never touch the same file by accident

the `__init__.py` files in each package are (currently) just a super fancy comment. The files makes Python treat `states/`, `entities/`, `input/`, `world/` as importable packages (`from states.state_manager import ...`) instead of just random folders. They don't need any code in them to work, we just used them to document what each package is for (did this so it doesn't look thaaat empty haha).

## screens
(logic mostly copied from Assignment 6 (gesture_application Melanie & Marina) and then duplicated into corresponding files since everything is kinda the same)
0: Start menu (continue by P2 clicking a button and P1 coloring the button) like a tutorial
1: In the world and you have to get to the dungeon gate and open it
2: Inside the dungeon with the enemies
3: Outside the dungeon at the treasury (solve puzzle)
4: Game over or game won screen (is displayed depending on where you die or after 3 if passed)
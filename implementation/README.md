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

## nowhere sprites 
Sooo a problem we encountered was how to use tilemaps. Since in e.g. unite you have. atilemap editor (just load your stuff in in the right format and voila you can "draw" your map as you wish and put "objects" in and collision etc.). We totally forgot that we use pyglet ._.

so we searched in the world wide webs and came across this gem: https://www.mapeditor.org

> "Tiled is a 2D level editor that helps you develop the content of your game. Its primary feature is to edit tile maps of various forms, but it also supports free image placement as well as powerful ways to annotate your level with extra information used by the game. Tiled focuses on general flexibility while trying to stay intuitive."

And with that we solved our Tilemap problem, only problem left is to learn how to use it ._. 

**bug alarm**

WHY WHY WHY 

so apparently when you have infinite on than pyglet cant handle that, but nuh uuuuh I needed to uncheck it in titled but that would be too easy (something with the sprite layout was wrong so it took 30 minutes to fix that with shitty random online threads) and in the end the creater of the tiles was just to lazy to put water tiles under the wave tiles so e colored random tiles that were not in the layer and thats why i couldnt select the whole map shift the offset just to uncheck infinite and use it in pyglet

lesson learned -> using a real game engine with sprite editor in future no more pyglet

+ because of ratio I added left and right on each side 6 additional tile columns ._.

TODO: 
- for the other tilemaps too ahhh
- didn't test treasure chamber or game over screen since its 1 am and I make rn more mistakes haha

## sources

### assets
- dungeon: https://free-game-assets.itch.io/free-2d-top-down-pixel-dungeon-asset-pack
- chapell: https://craftpix.net/download/100511/
- dungeon2: https://craftpix.net/download/80859/
- ruin: https://craftpix.net/download/107610/
- https://kenney.nl/assets/tiny-dungeon
- https://opengameart.org/content/gem-icons-0
- projectiles: https://pimen.itch.io/magical-animation-effects?__cf_chl_tk=WPC4MVda3nuvSvSu0.jML0moKodloZaz7RZJ98iUr3Y-1784286481-1.0.1.1-W2BH6zjARJbeqOtL_VRFk_JVZhwMaEBySsNUOToDago
- tornado: https://foozlecc.itch.io/pixel-magic-sprite-effects
- characters: https://zerie.itch.io/tiny-rpg-character-asset-pack
https://oboropixel.itch.io/characters-animations-asset-pack?download
https://pixelserial.itch.io/rpg-top-down-character-asset-pack?download
enemies + dungeon: https://pixel-poem.itch.io/dungeon-assetpuck
controller + keyboard: https://vryell.itch.io/controller-keyboard-icons
- treasure: https://pixelserial.itch.io/rpg-pixel-art-chests/download/eyJpZCI6MzQyNzI1OCwiZXhwaXJlcyI6MTc4NDI5NDIzNn0%3d%2evmdwQ1cZ2frwB%2bsrXRcKRwwKGOg%3d
- gems: https://drxwat.itch.io/pixel-art-diamond
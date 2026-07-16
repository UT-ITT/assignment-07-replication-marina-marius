**Game idea:**
A local two-player, Pokémon-style 2D pyglet game where players explore a tile-based overworld together. Player 1 uses their voice to control multiple properties of a shield and to unlock gates through pitch-matching and short sung melodies, while Player 2 uses hand-gesture input (via mediapipe) to select which voice property is currently active, position the shield, and interact with puzzle objects in the world. Success in the dungeon requires both players' actions to align in real time correct color, correct size/charge, **and** correct position creating a genuine two-player interdependence.

| Player | Mechanic | Input | Effect |
|---|---|---|---|
| **Player 1 (Singer)** | Grid movement | Keyboard (WASD) | Walks one tile at a time around the overworld |
| | Gate opening | Sing to match target pitch/color | Gate glows toward target color; holding correct pitch ~2s unlocks it |
| | Melody gate (final gate) | Sing a short 2-4 note sequence, compared to a target pattern | Gate unlocks if sung note order (and rough timing) matches the target melody |
| | Shield coloring | Sing to match enemy projectile color | Sets the shield's current color to match incoming projectile type |
| | Shield size | Volume/loudness | Louder = physically bigger shield, easier for P2 to land in position |
| | Shield charge/durability | Sustain duration (holding pitch steady) | Longer hold = more hits the shield can absorb before breaking |
| **Player 2 (Support)** | Grid movement | Keyboard (arrow keys) | Walks independently around the overworld |
| | Hand cursor | Mediapipe fingertip tracking | Visible on-screen cursor shows where P2 is "pointing" |
| | Voice-mode selection | Pinch/click on on-screen button overlay (Color / Size / Charge / Melody icons) | Determines which shield property P1's voice currently controls; unselected properties hold their last value |
| | Shield positioning | Pinch-and-drag gesture | Drags the shield to the correct spot to block an incoming projectile |
| | Object interaction | Pinch/click gesture on interactable tile | Pushes blocks, pulls levers, opens secondary paths |
| **General/World** | Dungeon entry | — | Requires P1's color-matched gate to be unlocked |
| | Mode overlay | — | Small persistent UI panel showing the currently active voice-controlled property, set by P2 |
| | Combat resolution | — | Projectile blocked only if shield color, size/charge, **and** position are all sufficient |
| | Puzzle elements | — | Movable blocks/levers only P2 can trigger, needed to progress |
| | Co-op win condition | — | Final stone/core requires both players' actions together to clear the dungeon |

## rough gameplay

Gameplay:

Startmenu:

Shows textbox with information about the game

start button:
- Player 2 needs to click on it with hand gesture to “activate the mechanism”
- button listens (to audio)
- Player 1 sings in requested pitch to color button
- button chnages calor if it is correct
- Player 2 needs to click on it again to switch to next state → state_overworld

state_overworld:
- player 1 and player 2 appera as game sprites in the map and can walk (only where no collision is)
- can interact with interactible objects (when player1 or 2 is touching the collision of object a interact box will apperar obove object with either a text that tells what to do: to activate player 2 needs to click the interactible object: either audio input from player 1 is needed or by clicking the object becomes movable and player 2 can pull or push by clicking on it (hand gesture) 
- e.g. gate is an interactible object where aplayer 1 needs to match the pitch to color the christal object if the color is reached it is locked and gate gets triggered and opens
- generally while singing the interactible object should switch colors to the corresponding pitch until the goal pitch is reached and that color is locked and no audio input needed anymore
after unlocking gate by clicking on it the state changes to next state → state_dungeon

state_dungeon:
- same mechanism as before (for gate until coloring kristal) to start combat phase
- random number enemies 3-10 will get spawned
- if key f gets hit a shield object appears in front of player 1 (movable object) with clicking on hud overlay by player 2 he starts the audio input for player 2 to do the 3 shield states 
- enemies shoot colored bullets and shield needs to be same color as bullets to absorb the bullets
- if player gets hit they lose a heart (hp bar each player has 3 heart sprites) if enemy get hit a heart sprite gets deleted if all 3 heart sprite get hit of one of the players → game over state
-   player 2 can shoot bullets and bullet color need to be same as enemy to kill enemy 1 bullet hit and enemy is deleted/dead/disappear
- shooting is triggered by key c. to change color audio input needs to hit the pitch ladder (each pitch other color) to lock a color player 2 needs to click on hud overlay gun button 
- to shoot to target p2 needs to click on enemy (if object is between enemy and bullt path, bulltet gets deleted.
- to change color again player 1 needs to click on see again
after all enemies are dead players need to go to end of dngeon and do again same mechanism of singing to color christal and go to next state → state_treasure

state_treasure:
- room full of chests and they need to be colored and moved in the right order (same mechanisms to color and push/pull as before for player 1 and 2
- after last correct treasure is pushed with the right color to the right spot all removable objects get deleted and a big diamond sprite appears for 10 seconds then next state → state_end 

state_end:
- if state end is reached by losing all three lives of at least one player = game over logic: time of playing since clicking start button of startmenu until time of dying, a text and restart button to state → state_startmenu
- if state end is reached after state_treaseare = game won logic: text, time of playing since clicking start button of startmenu until time reaching state_end, bullet shoot count, correct pitches out of sum of pitch tries nd restart button to state → state_startmenu
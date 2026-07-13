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
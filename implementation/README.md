# The Tavern Song of the Quartermasters Ledger

*(sung to whatever tune you like, the bard never wrote one down)*

> Gather round, ye weary dev, set down thy mouse and mead,<br>
> The sagas of our battles live in scrolls ye do not need <br>
> For **[`documentation.md`](../documentation.md)** holds the prophecy entire,<br>
> and **[`documentation.md`](bugs.md)** the diary of every pyglet-fire.<br>
> But *this* scroll here, dear traveler, is a humbler thing by far:<br>
> just a ledger of the armory what each file is and where they are (>ᴗ•)

No prophecy here, no bug-haiku, no council of tutors just an honest quartermaster's inventory of every file in `implementation/`, grouped by what part of the kingdom it belongs to, so "where's the enemy logic" takes you three seconds instead of thirty.

---

## The Root Chamber: top-level files

| File | What it does |
|---|---|
| `main.py` | The throne room. Boots the window, wires up audio/gesture input threads, registers all 5 states with the `StateManager`, runs the game loop. |
| `config.py` | The royal rulebook: every shared constant (window size, colors, speeds, hitboxes, pitch buckets) lives here so tuning happens in one place instead of five. |
| `pitch_color.py` | The Harmonionz spell itself: maps a raw frequency to a note and a color bucket. Core interaction technique lives here. |
| `audio_settings.py` | Shared music/SFX volume state, with a tiny listener system so sliders can live-update playing sound. |
| `quick.py` | The teleportation scroll: jump straight into any state (e.g. `treasure`) for testing without replaying the whole quest every time. |
| `idea.md` | The original design doc / game-mechanics table written before a single line of code existed. |
| `hand_landmarker.task` | Mediapipe's pretrained hand-landmark model file, not code, just the crystal ball itself. |
| `assets/` | Every sprite, tile, sound and font the kingdom uses. |

---

## `states/`: The Five Halls (screens)

| File | What it does |
|---|---|
| `state_manager.py` | The castle steward: holds whichever screen (0–4) is currently active and handles switching between them. |
| `state_startmenu.py` | Hall 0: the tutorial: P2 clicks the start button, P1 sings it the right color to advance. |
| `state_overworld.py` | Hall 1: walk-around world, leads to the dungeon gate. |
| `state_dungeon.py` | Hall 2: combat: enemies, shield, gun, projectiles. |
| `state_treasure.py` | Hall 3: the chest-coloring puzzle outside the dungeon. |
| `state_end.py` | Hall 4: game over / game won screen with run stats. |
| `game_stats.py` | The scoreboard that survives every `set_state()` call (lives on the manager, not any one screen): tracks time played, pitch accuracy, shots fired. |

---

## `entities/`: The Living Things

| File | What it does |
|---|---|
| `grid_actor.py` | Shared "walk exactly one tile, then wait" movement (Pokémon-style stepping) used by both players. |
| `player_singer.py` | P1: WASD to walk, E to interact, F to summon the shield. |
| `player_gesture.py` | P2: arrow keys to walk, hand-tracking does the pinch/click/drag. |
| `enemy.py` | Enemy spawning, animated bat sprite, projectile-firing AI. |
| `projectile.py` | Bullets (enemy and player), straight-line flight, wall/hit collision. |
| `shield.py` | P1's shield: grows with volume, changes color with a held pitch, blocks matching-color bullets. |
| `gun.py` | P2's gun: toggled with `L`, colored the same way the shield is, free-aims at the clicked point. |
| `sprite_anim.py` | Shared helper: load N numbered PNG frames into a cached, centered `pyglet.image.Animation`. |

---

## `input/`: The Sensory Organs

| File | What it does |
|---|---|
| `audio_input.py` | Reads the microphone, extracts live frequency/volume: no game logic, just exposes current values. |
| `gesture_tracking.py` | Runs mediapipe hand tracking, turns a detected pinch into a real OS mouse click/drag. |

---

## `world/`: The Realm Itself

| File | What it does |
|---|---|
| `tilemap.py` | Loads and renders the 3 `.tmx` maps (overworld, dungeon, treasure chamber), plus collision/walkability checks. |
| `interactable.py` | Base class for anything P1/P2 can interact with: one mother-class instead of copy-pasted logic per object. |
| `gate.py` | Color-matched (or melody-matched) crystal gates that unlock doors and start combat. |
| `gem.py` | Sing-to-color, drag-to-slot object: same trick as `gate.py`/`chest.py` on an animated sprite. |
| `chest.py` | Treasure chamber chests: sing the right color, drag onto the marked slot, solved. |
| `hud.py` | The dungeon overlay: buttons P2 clicks to pick what P1's voice currently controls. |
| `buttons.py` | Generic clickable button widgets used across screens. |
| `music.py` | One shared looping background-music player, swaps tracks cleanly between states. |

---

## One riddle for the road

*"I have five halls but no doors of my own, I am consulted before every journey, yet I never joins the quest myself. What am I?"*
> This very file. A map is not the territory, dear reader go play the actual game in `main.py`. (◕‿◕✿)

---

## 🍺 Outro: Last Call at the Tavern

> So raise your mug, o weary coder, the ledger's told its tale,<br>
> Every file has found its shelf, every module found its rail.<br>
> If ye seek the *why* behind it the doc and diary await,<br>
> But if ye only seek the *where* this humble scroll's your gate.<br>
> Now close the tab, go run `main.py`, and may your gates all glow the right hue. ⚔️(๑•̀ㅂ•́)و

_~Marius & Marina, July 2026_

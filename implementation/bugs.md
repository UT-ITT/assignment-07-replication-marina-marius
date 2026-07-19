# bugs.md

A living diary of everything that made us swear at pyglet while building out the game (start menu -> overworld -> dungeon -> treasure chamber -> end screen, phases 1 through 3, plus whatever broke in between while actually playtesting it). In the same spirit as the README: braindump, not a bugtracker with tickets. (ง -_-)ง

## Phase 1: Start Menu + Overworld

(Filled in as we actually hit things, not written in advance like some kind of liar hehe)

### The gesture cursor lies to you
`gesture_tracking.py`'s `cursor_x`/`cursor_y` are camera-frame coordinates dressed up as screen coordinates, NOT pyglet-window coordinates. If you naively compare them against a button's pixel position you will hit things that aren't there and miss things that are. 
**The Fix:** Don't touch `cursor_x`/`cursor_y` at all for hit-testing. The pinch already drags a real OS mouse cursor and does a real OS click, so pyglet's own mouse events already arrive in correctly-mapped window coordinates for free. Moral of the story: let the OS do the coordinate math, it's better at it than we are (╥﹏╥)

### "Click and drag" is one word away from being free
Turns out pyglet's `on_mouse_drag` only fires while a button is physically held, which is exactly what a held pinch produces. So `Pushable` didn't need any custom gesture-drag-detection logic, it just listens like a bog standard mouse drag and gets pinch support as a side effect. Found this out completely by accident.

### A Haiku About Webcam Pain (Yes, a literal haiku so you get the joke)
*Webcam will not start*<br>
*Five times I open the port*<br>
*Now it hates me, great*<br>

**The bug:** "Before phase 2 our webcam doesn't start at all". We noticed our `gesture_tracking.py` was scanning camera indices, opening and releasing each one just to see if it exists, then double-checking, then opening a *third* time for the tracking thread. We were doing up to 5+ real `AVFoundation` capture-session open/release cycles back to back. AVFoundation's session teardown isn't instant, so slamming it leaves the camera in a "nope, not now" state. Classic case of "it works" ≠ "it works when you do it five times in a row real quick".
**The Fix:** Ripped out the scanning and confirm-reopen entirely. `select_camera()` now just asks for an index (default 0) and returns it, opening the camera exactly once.

### The pinch that clicked absolutely nothing
**The bug:** Terminal happily prints `pinch=True` when you pinch, but nothing happens in the game. Turns out `hand_loop()` maps the hand landmark into screen coordinates using a hardcoded 1920x1080 canvas glued to the top-left corner of the desktop (0, 0). Our game window definitely wasn't at (0, 0). The click was real, but it landed on phantom coordinates.
**The Fix:** `hand_loop()` now takes `origin_x`/`origin_y` in addition to `window.width`/`window.height`. We feed it `window.get_location()` so it knows where the actual game is.

## Phase 2: Dungeon Combat 

### A shield glued to the dungeon's center tile
`shield.py` originally just planted itself at a fixed center coordinate and never moved again. P1 could be standing in a corner and the shield would still be chilling in the middle of the room doing absolutely nothing for them. Added `Shield.follow(x, y)` and called it every frame with P1's position. 

### "C is P2's key" needs to be true at the routing level
P2's gun toggle (`C`) was quietly funneling straight into `Player1.handle_key_press`, vanishing into a no-op with zero feedback. Gave `Player2` its own handler and split the dispatch explicitly. Failing silently is the worst kind of bug to chase later. Update 2: we changed (`C`) to (`L`) since it would be to much hassle (an understatement because it was freaking annoying haha) for P1 to also initiate that so P2 now does it themselves.

### Testing bullets through obstacles is a coin flip
Our P2-shoots-an-enemy test kept failing. Spent a bit convinced our math was wrong before realizing the bullet died exactly on top of a static obstacle block. Not a bug, just a test that accidentally drew a straight line through a wall. Moved the obstacles out of the way for that test.

### An already-dead bullet trying to update itself
Call `Projectile.destroy()` and then call `.update(dt)` before it's filtered out of the list and pyglet throws an `AttributeError` because the vertex list is gone. Cheap fix: `update()` just returns immediately if `self.alive` is already `False`.

### P1 quietly redecorating itself
**The bug:** `Player1.update()` had leftover code that changed P1's color based on audio pitch. Once `Gate` and `Shield` got their own live-color tracking, nothing looked at P1's color anymore. It just kept flickering through the palette purely so anyone watching could go "wait why is P1 changing colors, nothing's even nearby". 
**The Fix:** Deleted the audio-reactive line and unused imports. P1's rectangle is just `config.P1_COLOR` now, full stop.

### Hint labels assuming you already knew who does what
Strings like "sing its color" or "drag the crystal" are completely ambiguous when two players are staring at one screen. Every one of those strings now explicitly says `P1:` or `P2:` up front.

### "Hardcoding the easy note" made things harder
We thought forcing the tutorial to use the lowest frequency bucket (`config.SHIELD_COLORS[0]`) would be a nice gimmick so P1 wouldn't have to hunt for a high note. EXCEPT that lowest bucket is 500-1125Hz, which is actually kind of high for natural speaking voices. Forcing literally every single attempt to require exactly that one bucket meant if it was your worst range, you were stuck every single time.
**The Fix:** Reverted to `random.choice(config.SHIELD_COLORS)`. 

### The button/gate that never said what to sing
Players had to reverse-engineer the target purely from a live-updating swatch with no label and it would look "stuck" on a color instead of honestly saying "nothing detected right now" when P1 stopped singing. Added `config.SHIELD_COLOR_NAMES` so text hints can say "P1: sing GREEN", and resetting the color to a shared gray (`PITCH_SILENCE_COLOR`) when nothing is detected.

### The tornado that only span up because macOS wasn't looking closely enough
Found this one doing a full-repo audit. Code loaded frames from `"assets/tornado/"` (lowercase), but the folder on disk was `assets/Tornado` (capital T). APFS (macOS's default filesystem) is case-insensitive, so it worked fine for us. It would have hard-crashed the moment this ran on Linux.
**The Fix:** Pointed the calls to the real casing, `assets/Tornado`.

### The gate gets a sprite and preps for melody
The gate finally got a looping sprite instead of rendering off a base rectangle. Also left the color-matching logic behind a clean `_lock()` method so Marius can swap it for a short sung note sequence check later without breaking everything downstream.

### The entry gate that ate itself
**The bug:** Walking into the dungeon's entry crystal to start the fight threw an `AttributeError`. If P2 had already walked in, and then P1's entry completed the pair, `Gate.try_enter` fired `on_unlock` synchronously. `_start_combat` sets `self.gate = None` immediately, but the very next line then tried to call `self.gate.try_enter` on nothing.
**The Fix:** Read `self.gate` into a local variable once at the top and use that local for every call in the block instead of re-reading `self.gate` after each one.

### Walking into an unlocked gate did nothing
We required pixel-perfect overlap between the player's bottom-left corner and the gate's pixel box. Players only ever step in 64px jumps, so exactly *one* tile satisfied that point check. Missing it by even one step meant walking straight through the gate forever. Swapped the point check for an actual rect-vs-rect overlap.

### The crystal isn't a door
The dungeon's entry crystal quietly inherited the walk-in-together mechanic from doors. Gave `Gate` a `walk_in_required` flag. When `False`, coloring it triggers the unlock immediately.

### The gem stopped freezing mid-sing, and learned to be dragged
Gems froze on a single frame while listening to P1 sing. Rewrote it to swap looping color folders. Also bolted on `Chest`'s drag pattern, so coloring it unlocks dragging.

### Pinching could click a gem but couldn't drag it (Rounds 1 & 2)
Holding a pinch to drag did absolutely nothing. macOS treats a moved-while-button-down cursor as `kCGEventLeftMouseDragged` (type 6), but we were constantly posting plain `kCGEventMouseMoved`. `on_mouse_drag` literally never fired. 
**Fix 1:** Swapped to posting the proper event type.
**Fix 2:** The drag event fired, but always carried `delta=(0,0)`. Synthetic OS events don't carry native deltas, so we explicitly computed and injected `delta_x`/`delta_y` into the event fields.

### P1 and P2 stopped being plain colored squares
Real 16x20 pixel-art sprites landed! `GridActor` now loads idle and walk cycle frames based on the current movement direction. P2's pinch-highlight lost its old brightness trick and now drops the blue channel so it doesn't wash out the art.

### The overworld got walls
Added real per-tile collision via Tiled's `blocks` layer. Almost blocked the whole map initially because the `water` layer was a full-map base layer sitting underneath all the land. Had to search for new nearest-open-spots for all hardcoded spawns/gems because they landed inside solid walls.

### Tilemap animations
Animated tiles (fire, water) only showed their first static frame. Built a `pyglet.image.Animation` cached per-gid so they actually loop forever now. 

### Dungeon collision, capped enemies, right-sized players
Players looked oversized, so we shrank `PLAYER_RENDER_SCALE` down to 0.5. Gave the dungeon real wall collision too, which immediately ate our hardcoded bullet obstacles. Capped combat enemies at exactly 3 instead of randomly rolling up to 10.

### The enemy stopped being a colored square too
Enemies are now an animated 4-frame flying bat loop. Had to pass `anchor_center=False` to the animation loader because the physics hitboxes are bottom-left anchored, otherwise hits would visually miss.

### Bullets never actually knew the dungeon had walls
Bullets flew straight through actual stone walls that players couldn't cross. `_resolve_bullets` now checks `self.tilemap.is_walkable()` against a box centered on the bullet. 

### The collision box was the size of the tile
Players kept getting stuck even on walkable tiles because the 64px invisible box was huge compared to the tiny 16x20 sprite. Shrank the collision box down to match the real character's rendering dimensions.

### Shield loses its stopwatch, gun learns to sing
Cut the shield's duration timer entirely. Now it just tracks a `_size_peak` for 3 seconds. Also gave the gun the exact same hold-steady-for-2s color-locking treatment as the shield instead of its old manual toggle.

### One bullet speed wasn't enough
Split `config.BULLET_SPEED` into `PLAYER_BULLET_SPEED` and `ENEMY_BULLET_SPEED` so P2 shoots faster than what's coming back at them.

### The missing floor tiles were never a Tiled problem
Marius noticed `earth_floor` tiles missing. Not a Tiled bug, just Pyglet batching sprites from the same texture together with zero draw order, causing layers to interleave randomly. Created distinct ordered child groups for every layer.

### P2's gun was secretly a hitscan-on-enemy click
The gun wasn't free-aiming. It looped every enemy and only fired if the pinch landed *exactly* inside a hitbox rect. Dropped the loop and just let P2 shoot a projectile aimed straight at the clicked point.

### The gate needed multiple pinches
The gate visibly jumped 30px when clicked. The idle loop was center-anchored, but the listening image was bottom-left anchored. So the *rendered* gate drifted away from its invisible click target. Fixed anchors so `sprite.x/y` are identical across states.

### Bullets now actually point where they're going
Stole the `atan2` math from the Steering Law assignment to rotate sprites toward their travel direction. Just had to reverse it for Pyglet's y-up space (`-degrees(atan2(vy, vx))`).

### Unwinding Group 1 one layer at a time
Split the dungeon collision into 4 specific named layers (`walls_top`, `walls`, etc.), which forced us to move yet another hardcoded obstacle that got swallowed by `walls_back`.

### Gate walk-in box shrinkage
Used the new `collision_box()` for gate entries so players don't trigger the walk-in from 55px outside the sprite.

### The shield's pinch-to-listen step was missing entirely
You couldn't drag the shield after changing colors. The real bug was that the shield needed a `listening` flag so P1 screaming before P2 pinched it would do nothing. You now have to explicitly pinch to arm it before singing.

## Phase 3: Treasure Chamber + End-State Metrics

### Deciding what counts as a "pitch attempt"
Defined one "attempt" as one sample per frame where P1 is actively singing during a *real* color-match check (Gate/Chest locks). The Shield and Gun were left out since they just live-track with no fixed target.

### The chest slot markers are fully transparent
The chest markers were drawn with an `(0,0,0,0)` color fill. Just flagged it for review before assuming it looks right.

### The treasure chamber finally gets its own room
Swapped the flat rectangle background for an actual `treasure.tmx` tilemap. Moved the 3 target slots directly in front of the fenced dragon, left-to-right.

### The slot markers were the last spoiler
Slot markers were drawn in the chest's actual `target_color`. We swapped them to a flat black outline so they only say "a chest goes here", forcing you to actually sing to find the answer.

### Colors weren't actually random
We randomized chest colors, which meant two chests could easily share a color. That broke the puzzle logic because the solve order assumed the first chest physically lived on the left. Added an independent shuffle for the slots too. 

### Snapping into place was itself the tell
A chest only snapped when dropped near its *correct* slot. Drop it anywhere else and nothing happened. That basically told you the answer immediately without actually guessing.
**The Fix:** Chests now snap to *any* marked slot when dropped close enough, right or wrong. If it's the wrong slot, `_reset_wrong()` bounces the chest back to its spawn point, uncolored, and P1 has to sing it all over again like a peasant.

### Dragging after coloring didn't work if the pinch never let go
**The bug:** Pinch and drag didn't work right after a chest's color locked in. `on_mouse_press` only set `grabbed = True` if the chest was *already* colored when the press event fired. If you hold the pinch continuously while singing, there is no second press event, so `grabbed` never flips.
**The Fix:** Added `Chest.note_still_pressed(x, y)`. If the chest just locked its color, isn't grabbed, and the point is still inside it, it auto-grabs it right then instead of waiting for a press event that a continuous hold will never produce.

### The reveal waits for all 3
Instead of telling you immediately if a chest drop was correct, you have to place all 3 chests first. If any are wrong, it scatters the whole group to new random coordinates.

### The start/end screens Downloads landmine
**The bug:** `startscreen.tmx` and `endscreen.tmx` crashed on load with a `FileNotFoundError` pointing to `../../../../../Downloads/...`. Tiled saves image paths relative to where the `.tmx` lived at the time. These two were clearly built straight out of a Downloads folder and the PNGs never moved over. It would have broken instantly for anyone else. Dataset drama making a comeback!
**The Fix:** Copied the 20 distinct images into `assets/chamber/` and rewrote the paths down to plain filenames.

### One font, everywhere
Forced everything to use `Play-Regular.ttf`. Also shoved the Start/End screen buttons down to `y=100` so they aren't awkwardly sitting on top of everything else.

### Player collision shrunk again & Shield continuous grab
Shrunk the player collision box again to exactly 19.2x19.2 across all maps regardless of scale. Also applied the exact same continuous-hold `note_still_pressed` fix we built for `Chest` to the `Shield`. 

### Quick.py
Added a small `quick.py` script to directly load states (like `treasure`) so we can skip the start menu and dungeon walk cycles during testing. This script felt so liberating because we just wanted to see if e.g. the tilemap looks good and needed to do eeeeeverything again and again and again.... now we got PTSD

### dungeon.tmx's "3 blank spots"
Spent forever investigating 3 "blank spots". Turns out there were no missing tiles; it was just a deliberate stylistic choice to use clean `Floor` tiles in the boss room instead of the speckled `earth_floor`. There are still 3 spots that swapped the location after "ficing" it but I cant seem to find them maybe Monday is a better day :(

### Shield buttons renew, not retire
Buttons originally became permanently disabled one-shots after locking. Rewrote it so P2 can pinch the button again to redo the scream/sing window instead of being locked out forever.

### Treasure chest puzzle: right guesses stick now
Scattering *every* chest back to square one on a wrong guess made it impossible if chests had duplicate colors. Changed the logic to permanently lock-in any chest placed in its correct slot, only scattering the wrong ones (as it should be like some fixes ago but because of changing stuff it broke and needed to be fixed again).

### Dungeon combat cleanup & Gem deletion crash
Mid-flight enemy bullets would just freeze in the air when the phase flipped to cleared. We added cleanup to destroy them properly.
*However*, deleting the start-combat gem synchronously inside `on_update` caused an immediate `AttributeError` on the very next line because `self.gem` was suddenly `None`. We had to add fresh `is not None` guards to protect mid-frame self-deletions.
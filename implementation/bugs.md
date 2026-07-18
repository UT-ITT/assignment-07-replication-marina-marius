# bugs.md

a living diary of everything that made us swear at pyglet while building out the game (start menu -> overworld -> dungeon -> treasure chamber -> end screen, phases 1 through 3, plus whatever broke in between while actually playtesting it). in the same spirit as the README: braindump, not a bugtracker with tickets.

## phase 1: start menu + overworld

(filled in as we actually hit things, not written in advance like some kind of liar)

**the gesture cursor lies to you**
`gesture_tracking.py`'s `cursor_x`/`cursor_y` are camera-frame coordinates dressed up as screen coordinates, NOT pyglet-window coordinates. if you naively compare them against a button's pixel position you will hit things that aren't there and miss things that are. the actual fix: don't touch `cursor_x`/`cursor_y` at all for hit-testing. the pinch already drags a real OS mouse cursor and does a real OS click (see `Controller` in there), so pyglet's own `on_mouse_press`/`on_mouse_motion`/`on_mouse_drag` events already arrive in correctly-mapped window coordinates for free. moral of the story: let the OS do the coordinate math, its better at it than we are.

**"click and drag" is one word away from being free**
turns out pyglet's `on_mouse_drag` only fires while a button is physically held, which is exactly what a held pinch produces (see above). so `Pushable` didn't need any custom gesture-drag-detection logic, it just listens like its a bog standard mouse drag and gets pinch support as a side effect. found this out by accident while trying to figure out how to detect "is P2 currently dragging" and realizing pyglet already asks that question for us.

**everyone needs the same "sing until it matches" trick**
start button, overworld gate, (later) dungeon/treasure locks ,its the exact same "P1 sings, live color updates, hold it ~2s, lock" logic every single time. instead of writing it four times slightly differently and forgetting to fix a bug in three of the four copies later, it lives once in `entities/shield.py` (`frequency_to_color`) + `world/gate.py` (`Gate`), and the start button borrows the constants (`LOCK_HOLD_TIME`, `COLOR_TOLERANCE`) instead of inventing its own magic numbers.

## the great webcam refuses to start incident

**the bug**
"before phase 2 our webcam doesn't start at all" ,noticed right before we were about to move on. handed over two files (`pointing_input.py`, `recorder.py`) from the ITT assignment where the exact same webcam+mediapipe combo worked completely fine, so it wasn't opencv or mediapipe being cursed in general, it was something specifically ours.

diffing our `gesture_tracking.py` against those two working files, the difference jumped out immediately: the reference files call `cv2.VideoCapture(0)` exactly **once**. ours did not. tracing what actually happens before a single frame gets read in our version:
1. `select_camera()` scans camera indices 0, 1, 2, opening (`open_camera()`, which itself tries 2 backends per index) and releasing each one just to see if it exists
2. once you type an index, it opens that SAME camera *again* just to double-check it works, then releases it
3. `start_tracking()` spawns the tracking thread, which calls `hand_loop()`, which opens it a **third** time ,this is the one that actually gets used

so a single "select a webcam and start tracking" run was doing up to 5+ real `AVFoundation` capture-session open/release cycles back to back, each one measured at ~0.7-1.3s on its own. opencv has no cheap "does this index exist" query the way `sounddevice.query_devices()` does for audio (that one's just reading metadata, no hardware lock involved) ,so "scanning" a camera means actually grabbing and letting go of the hardware, repeatedly, fast. AVFoundation's session teardown isn't guaranteed to be instant, so slamming it with back-to-back open/release/open/release/open calls is exactly the kind of thing that leaves the camera in "nope, not now" state. classic case of "it works" ≠ "it works when you do it five times in a row real quick."

**the fix**
ripped out the scanning and the confirm-reopen entirely. `select_camera()` now just asks for an index (default 0) and returns it, no camera touched at all until `hand_loop()`'s single `open_camera()` call ,matching exactly what the two working reference files were already doing right along. verified with a counting wrapper around `open_camera()`: the full select->start flow now opens the camera exactly once, down from 5.

## the pinch that clicked absolutely nothing

**the bug**
camera works now, terminal happily prints `pinch=True` when you pinch, and... nothing happens in the game. no button reacts, no click registers anywhere. so tracking is fine, the "turn a pinch into a real OS click" part of `gesture_tracking.py` is presumably fine too (its the same trick `pointing_input.py` uses), which means the click is landing *somewhere* ,just not on our window.

turns out `hand_loop()` maps the hand landmark into screen coordinates using `screen_width`/`screen_height` params that default to a hardcoded 1920x1080, and `main.py` never overrode them, so every synthetic click was being aimed at a phantom 1920x1080 canvas glued to the top-left corner of the desktop (0, 0). checked this machine's actual displays and: two monitors, neither of which is helpfully positioned at the origin, and our own game window doesn't spawn at (0, 0) either (pyglet centers it by default, e.g. `(320, 180)` on this box). so the "click" was real, it just landed on whatever happened to be sitting at that made-up coordinate on the desktop ,almost never our game.

**the fix**
`hand_loop()`/`start_tracking()` now take `origin_x`/`origin_y` in addition to `screen_width`/`screen_height`, and `main.py` feeds them real values: `window.width`/`window.height` (not a guessed 1920x1080) plus `window.get_location()` (the window's actual top-left corner on the desktop, not an assumed (0, 0)). the landmark still maps into window-relative pixels first (that's still what `cursor_x`/`cursor_y` expose), the origin only gets folded in for the one line that actually moves the real OS cursor. known limitation: the origin is captured once at startup, so if you physically drag the game window around mid-session the clicks will quietly drift off ,fine for now, not what we were chasing here.

## phase 2: dungeon combat (bullets, enemies, hearts, gun hud)

**a shield glued to the dungeon's center tile**
`shield.py` originally just planted itself at a fixed `(WIN_WIDTH/2, WIN_HEIGHT/2)` and never moved again ,fine for testing color/size/tune in isolation, useless the moment bullets need to check "did the shield actually block this." P1 could be standing in a corner and the shield would still be chilling in the middle of the room doing nothing for them. added `Shield.follow(x, y)` and call it every frame with P1's position ,"spawns in front of P1" only means something if it actually stays in front of P1.

**"C is P2's key" needs to be true at the routing level, not just in a comment**
`state_dungeon.py`'s `on_key_press` funnels every key that isn't `ENTER`/`O` straight into `player1.handle_key_press(...)`. that was fine when the only other keys were P1's own `F`/`E` ,but `C` (P2's gun toggle) would've quietly gone into the same call, `Player1` wouldn't recognize it, and it'd vanish into a no-op with zero feedback. gave `Player2` its own `handle_key_press(symbol, gun)` and split the dispatch explicitly: `F`/`E` to P1, `C` to P2. an unrecognized-key bug that fails silently is the worst kind to chase later, so worth catching before it existed.

**testing "does the bullet reach the enemy" through two static obstacles is a coin flip**
first pass at the P2-shoots-an-enemy test kept failing ,bullet spawns fine, enemy survives. spent a bit convinced `hits_rect`/velocity math was wrong before actually printing the bullet's flight path: it died exactly on top of one of the dungeon's two obstacle blocks. not a bug, the obstacle-blocks-bullets mechanic doing exactly what its supposed to ,our test just happened to draw a straight line from P2 through a wall. moved the obstacles out of the way for that specific assertion and gave obstacle-blocking its own dedicated test instead of an accidental one.

**an already-dead bullet still tried to update its own (deleted) shape**
found while poking at the above: call `Projectile.destroy()` (which does `shape.delete()`), then call `.update(dt)` on that same bullet again before its been filtered out of whatever list its in, and pyglet throws `AttributeError: 'NoneType' object has no attribute 'translation'` ,the vertex list is gone but nothing told `update()` to stop touching it. `_update_combat`'s normal per-frame flow always filters dead bullets out at the end of the same frame, so this never actually bites during real gameplay, but its exactly the kind of ordering assumption that breaks the moment anything reorders around it. cheap fix: `update()` just returns immediately if `self.alive` is already `False`.

## p1 quietly redecorating itself + hint text that stopped being true

**the bug: P1's rectangle was still a mood ring**
`player_singer.py`'s `Player1.update()` had `if audio_input.current_frequency > 0.0: self.color = pitch_to_color(...)` sitting in it ,leftover from before `Gate`/`Shield` existed, back when the overworld's gate check literally read `player1.color` off the player rectangle itself to see what P1 was singing. once `Gate` and `Shield` got their own independent live-color tracking (`entities/shield.py`'s `frequency_to_color`, checked entirely on the object's own rect, not on P1), nothing ever looked at `player1.color` again ,it just kept flickering through the palette for show, with zero mechanical purpose, purely so anyone watching could go "wait why is P1 changing colors, nothing's even nearby." dead code that still visibly *does something* is the sneakiest kind, since nothing crashes and nothing looks broken enough to grep for.

**the fix**
deleted the audio-reactive line and the now-unused `audio_input` import from `player_singer.py` ,P1's rectangle is just `config.P1_COLOR`, full stop, exactly as static as P2's (minus P2's pinch-glow, which P2 actually still uses for something). `pitch_to_color()` itself stayed since `main.py`'s `--debug` window still calls it directly for the pitch/color debug overlay, that one's unrelated and legit.

**the text bug: hint labels that assumed you already knew who does what**
`state_overworld.py`'s hint line, `Gate`'s floating hint, `Pushable`'s floating hint, and the base `Interactable`'s default hint all described an action ("click/pinch to wake it up," "sing its color," "drag the crystal") without ever saying *which player* does it. fine if you already know P1 sings and P2 gestures, useless the moment you don't, and with two players staring at one screen "sing it open" is genuinely ambiguous about who's supposed to open their mouth. every one of those strings now explicitly says `P1:` or `P2:` up front ,same fix applied to the dungeon's three hint variants (`puzzle`/`combat`/`cleared` phases) for consistency, since they had the exact same problem and we'd only just now made a rule about it.

## "hardcoding the easy note" made things harder, not easier

pitch matching on the start button felt broken ,turns out it wasn't the matching logic, it was a design call we made a bit earlier and got wrong. `state_startmenu.py` used to pick a `random.choice(config.SHIELD_COLORS)` target; we "improved" it to always pick `config.SHIELD_COLORS[0]` (the lowest bucket) since "its the tutorial screen, don't make P1 hunt for a high note." except the lowest bucket is still 500-1125Hz (`audio_input.min_freq`/`high_freq` span divided into 4) ,for a lot of natural speaking/singing voices that's already on the higher side, not a gimme, and forcing literally every single attempt to require exactly that one bucket meant there was no lucky-easy-roll fallback like random selection used to occasionally give you. "always the same target" also means if that particular bucket is the least reliable one to hit for your specific voice/mic, you're stuck every single time instead of one out of four.

reverted to `random.choice(config.SHIELD_COLORS)`, restored the generic hint text. kept the `PitchLegend` though ,showing the low->high mapping is still useful regardless of which of the four gets picked, that part wasn't the problem.

## the button (and gate) that never said what to sing, and never let go of the wrong color

**the ask**
two related complaints about the same underlying thing: "at least write in text which color (pitch) the button wants," and "the default should be gray if nothing is being said." P1/P2 had to reverse-engineer the target purely from a live-updating swatch with no label, and the button/gate would happily freeze on whatever color was last sung even after P1 stopped singing entirely ,looked "stuck" on a color instead of honestly saying "nothing detected right now."

**the fix**
added `config.SHIELD_COLOR_NAMES` (parallel to `SHIELD_COLORS`) so a target can be *named*, not just shown as a swatch, and `config.PITCH_SILENCE_COLOR` (gray) as the one shared "nobody's singing right now" color. `state_startmenu.py`'s hint text now says e.g. "P1: sing GREEN to match the button!" the second a target is picked, and `Gate` does the same the second P2 wakes it up ("P1: sing BLUE to unlock it!"). both now also reset their rect to `PITCH_SILENCE_COLOR` every single frame `audio_input.current_frequency <= 0`, instead of leaving `rect.color` sitting on whatever the last real sample happened to be.

## phase 3: treasure chamber + end-state metrics + restart flow

**deciding what actually counts as a "pitch attempt"**
the spec wants a "pitch accuracy ratio," but P1's pitch is sampled continuously, not as discrete button presses ,so what even is one "attempt"? landed on: one sample per frame P1 is actively singing during a *real* color-match check (`Gate.update()`, the start button's own `on_update()`, `Chest.update()`), each frame a hit or a miss depending on `colors_match()`. deliberately left `Shield`'s color mode and `Gun` out of the count ,neither has one fixed target color to be right or wrong against (`Shield` just mirrors whatever's sung live, `Gun` just loads it), so there's no "attempt" happening there in any meaningful sense, only "current state, no verdict." once the boundary was decided, wiring it in was a one-liner per object (`Gate`/`Chest` take an optional `stats=` and call `stats.record_pitch_sample(matched)` right where they already compute `matched` for the lock check anyway) ,the actual work here was the decision, not the code.

**the chest slot markers are drawn with a fully transparent fill and we haven't actually looked at them yet**
`world/chest.py` marks each chest's target slot with `pyglet.shapes.BorderedRectangle(..., color=(0, 0, 0, 0), border_color=target_color)` ,a colored outline with nothing filled in. this compiles and constructs fine, and nothing in the headless tests would catch a rendering problem since none of them ever call `on_draw()`. flagging it here instead of quietly assuming it looks right: worth an actual look in `python main.py` before trusting that a zero-alpha fill renders as "see-through" and not as, say, an opaque black square.

## the tornado that only span up because macOS wasn't looking closely enough

**the bug**
found this one doing a full-repo audit for the todo file, not from a report - `entities/shield.py` loads every tornado shield frame from `"assets/tornado/<color>/..."` (lowercase), but the actual folder on disk is `assets/Tornado` (capital T). this ran completely fine every single time it was tested, because APFS (macOS's default filesystem) is case-insensitive by default - `assets/tornado` and `assets/Tornado` point at the exact same directory as far as macOS is concerned. would've been a hard crash the moment this ran on Linux, or any case-sensitive filesystem, or even macOS with a case-sensitive volume - `pyglet.image.load()` doesn't case-fold paths, it just fails to find the file.

**the fix**
pointed the two `f"assets/tornado/{folder}"` calls (and the comment above them) at the real casing, `assets/Tornado`. quick reminder to actually check folder casing against what the code assumes, especially since case-insensitive-by-default is a macOS-specific convenience, not something to rely on.

## the gate finally gets a sprite, and stops opening the second you finish singing

**the sprite half**
`world/gate.py` was still rendering off the base `Interactable` rectangle, the one thing left doing that after `Chest`/`Gem` both got sprite passes already. gave it the same treatment: `assets/gate/basic/tile000-005.png` loops while it's idle, freezes on `tile000.png` of whichever color folder the live pitch maps to while P1's singing (`basic/tile000.png` during silence, same "gray means nothing's happening" rule everywhere else), and once locked it loops `tile000-005.png` of the matched color as the "unlocked, glowing" animation.


one thing this exposed: `state_dungeon.py`'s entry gate and combat phase share the *same* `Player1`/`Player2` objects (unlike every state-to-state transition, which just builds fresh ones), so `_start_combat()` now explicitly flips both players back to `visible = True` - otherwise you'd walk both players invisibly into their own fight. the exit gate and the overworld gate don't need this, both lead into a full `manager.set_state(...)` that rebuilds fresh players anyway, so there's nothing stale left to fix there.

**prepped, not built: the melody mechanic**
`idea.md` wants the final gate to check a short sung note sequence instead of one held pitch, that's marius's piece to build, not something we needed to implement here. left the color-matching logic in `update()` behind a single clearly-marked entry point (`_lock()`) so swapping it for a sequence check later doesn't touch anything downstream (the walk-in requirement, `on_unlock`, stats wiring) - left a comment pointing at `Shield._update_tune` in `entities/shield.py` as the existing "buffer stable notes, compare against a target sequence" pattern to reuse instead of reinventing it.

## the entry gate that ate itself the moment both of us walked in

**the bug**
marius sent over a crash from actually playing: `AttributeError: 'NoneType' object has no attribute 'try_enter'` in `state_dungeon.py`'s `on_update`, right when walking into the dungeon's entry crystal to start the fight. `on_update` checks P1's entry first, then P2's, both against `self.gate`. the trap: if P2 had already walked in on an earlier frame and P1's entry is the one that completes the pair, `Gate.try_enter` fires `on_unlock` synchronously right there, mid-call, `on_unlock` is `_start_combat`, and `_start_combat` sets `self.gate = None` immediately. the very next line then tries `self.gate.try_enter(self.player2, ...)` , except `self.gate` isn't the gate anymore, its `None`, so it blows up reaching for `.try_enter` on nothing. reproduced it directly with a script (fake `on_unlock` that nulls the gate, same as `_start_combat` does) before trusting it was actually this.

**the fix**
`on_update` now reads `self.gate` into a local (`gate = self.gate`) once at the top and uses that local for every call in the block instead of re-reading `self.gate` after each one. the underlying `Gate` object itself never gets destroyed, only the `DungeonState.gate` attribute pointing at it does, so the local reference stays perfectly valid even after `on_unlock` reassigns `self.gate` out from under it - and calling `try_enter` again on an already-completed gate is harmless anyway (`player in self._entered` just returns `False`). checked the overworld gate for the same landmine, its `on_unlock` (`_enter_dungeon`) only ever calls `manager.set_state(...)` and never touches `self.gate` at all, so that one was never actually at risk, left it alone instead of adding a guard for a crash that can't happen there.

## walking into an unlocked gate did nothing, because you basically couldn't

**the bug**
crash fixed, gate unlocks fine, both players walk into it... and nothing happens, no state change, ever. `try_enter(player, x, y)` was gating on `self.contains(x, y)`, which only tests whether one exact point (the player's bottom-left corner) falls inside the gate's own pixel box. players are `TILE_SIZE` (64px) tiles that only ever step in 64px jumps, gates are 80px boxes sitting at positions that aren't multiples of 64 - do the actual math (wrote a script instead of eyeballing it) and out of every grid tile a player can reach from their dungeon spawn, exactly **one single tile** ever satisfied that point check for the entry gate. missing it by even one step (which is basically always, since nothing on screen tells you which of dozens of tiles is *the* one) meant walking straight through the gate's sprite and having it do nothing, forever.

**the fix**
swapped the point check for an actual rect-vs-rect overlap between the player's 64x64 tile and the gate's own box - "is any part of the player standing on any part of the gate," which is what "walk into it" actually means. re-ran the same reachable-tile script after the fix: the same entry gate now has 4 workable tiles instead of 1, and they line up with what `in_range(radius=64)` (the same "close enough" check every other player-proximity interaction in this game already uses) would call adjacent to the gate - so this isn't some generous new leniency, it's just no longer needing pixel-perfect luck to trigger something the sprite visually says you're already standing on.

## the crystal isn't a door, it shouldn't have needed one walked into it

**the ask**
the dungeon's entry crystal (color it -> enemies spawn) and its exit gate (color/melody it -> head to treasure) both go through the same `Gate` class, so both quietly inherited the walk-in-together mechanic the moment we added it for real doors. that's wrong for the crystal specifically - "colored to start the enemy" means coloring it should be the whole trigger, not colored-then-also-walk-into-it. also asked to confirm the exit gate can't be unlocked before the enemies are dead, which turned out to already be true structurally: `_spawn_exit_gate()` (the only place that ever constructs it) only runs once `self.enemies` is empty, so there's nothing to click on before that, the gate simply doesn't exist yet.

**the fix**
gave `Gate` a `walk_in_required` flag (defaults `True`, so the overworld gate and the dungeon's exit gate are unaffected). when it's `False`, `_lock()` calls `on_unlock()` immediately the instant the color (or melody) locks in, same as every gate behaved before the walk-in mechanic existed, and `try_enter()` becomes a permanent no-op so nobody's sprite ever gets hidden waiting for a walk-in that isn't required. `state_dungeon.py`'s entry crystal now spawns with `walk_in_required=False`; the exit gate keeps the default. also deleted the `_start_combat()` lines restoring `player.rect.visible = True` - those existed only to undo the walk-in hide, which can't happen to this gate anymore, dead code the moment the flag flipped.

## the gem stopped freezing mid-sing, and learned to be dragged

**the ask**
`world/gem.py`'s `Gem` (built for the treasure chamber's final prize) froze on a single static `tile005.png` the whole time it was listening to P1 sing - fine for one gem nobody's timing against anything, but the new ask was for gems that do actual work: 4 of them in the overworld that need coloring *and* dragging into a matching slot before the gate can even be woken, and one in the dungeon that just needs coloring to spawn the enemies. asked for the animation to keep playing the whole time, just swapping which color folder is looping - basic while idle or silent, the live-pitch color while singing, the locked target forever after.

**the fix**
rewrote `Gem` around a single `_gem_loop_animation(folder)` helper (`tile000-007.png`, always looping, only the folder changes) instead of the old split between a `FLOAT_FRAMES` loop and a frozen `_idle_image`. `_set_folder()` only reassigns `sprite.image` when the folder actually changes, same "don't restart a loop that's already playing" rule the shield/gate already follow. then bolted on `Chest`'s exact color-then-drag-then-check-slot pattern (`on_mouse_drag`/`on_mouse_release`/`_check_solved`, `SLOT_TOLERANCE`), gated behind an optional `target_slot`: given one, coloring it just unlocks dragging, same as a chest; given none (the dungeon's trigger, the treasure chamber's finale), coloring it *is* solving it, `on_solved` (renamed from `on_locked` - it's not always "locked and done" anymore) fires the instant the color locks in.

**wired in**
`state_overworld.py`: swapped the single draggable `Pushable` "crystal" for 4 `Gem`s (one per `SHIELD_COLORS` entry) with slots near the gate; the gate's `on_mouse_press` only gets forwarded a click once `all(gem.solved for gem in self.gems)` - block it at the call site rather than teaching `Gate` about gems it has no business knowing about. `state_dungeon.py`: the old "crystal" (a `walk_in_required=False` `Gate`) is now a slot-less `Gem` instead, `on_solved=self._start_combat`. `state_treasure.py`: only needed the `on_locked=` -> `on_solved=` kwarg rename, its gem never had a slot so nothing else about its behavior changed. gave `Gem` a proper `hint_label` too (it never had one before, `Interactable`'s `in_range`/`show_hint` come along for free), wired into all three states' `on_update` the same way `Chest`'s already is.

## pinching could click a gem but couldn't actually drag it

**the bug**
first real hands-on test of the 4 overworld gems: singing the right color and clicking worked fine, but holding the pinch and moving the hand to drag the gem onto its slot did nothing at all - the gem just sat there. this one was never going to show up in the headless tests from the gem rewrite above, those fire `on_mouse_drag` directly, they don't go through the actual pinch pipeline.

`input/gesture_tracking.py`'s `Controller` drives a *real* OS cursor via raw `CGEvent`s (see the comment at the top of `player_gesture.py` - clicks reach the game exactly like a normal mouse would, that's the whole design). `press()`/`release()` correctly post `kCGEventLeftMouseDown`/`Up`, but the `position` setter - called every tracked frame to move the cursor always posted `kCGEventMouseMoved` (event type 5), regardless of whether the pinch was currently held down. macOS treats a moved-while-button-down cursor as a *different* event type, `kCGEventLeftMouseDragged` (type 6), and AppKit only routes `mouseDragged:` (which is what pyglet turns into `on_mouse_drag`) from that type - plain "moved" events go to `on_mouse_motion` instead. so a held pinch produced a real `mouseDown`, then a stream of `mouseMoved`s, then a real `mouseUp` - `on_mouse_press` and `on_mouse_release` both fired right on cue, `on_mouse_drag` never fired once, for anything, ever. this bug has been sitting under `Chest`'s drag too, just never physically tested with real pinch input yet.

**the fix**
gave `Controller` a `_button_down` flag, flipped in `press()`/`release()`. the `position` setter now checks it and posts `kCGEventLeftMouseDragged` (6) while a pinch is held instead of `kCGEventMouseMoved` (5), matching what a real trackpad-drag actually looks like at the OS event level. everything downstream pyglet's `on_mouse_drag`, `Gem`/`Chest`'s `on_mouse_drag(dx, dy)` - needed zero changes, they were only ever missing the event that should've been triggering them.

**round two: the drag event fired, but always carried (0, 0)**
that fix alone wasn't the whole story added `[pinch]`/`[pyglet]`/`[gem]` print tracing (still in the code) to actually see the pipeline live instead of guessing again, and the log told a very specific story: `on_mouse_drag` *was* firing repeatedly during a held pinch (so the event-type fix above was correct and necessary), but every single call logged `delta=(0.0, -0.0)` even while the cursor's own x/y was visibly sliding across the window frame to frame. `CGEventCreateMouseEvent` only stamps the *absolute* position we hand it - the separate `deltaX`/`deltaY` fields a real mouse event carries are normally filled in by the hardware HID driver from actual relative motion, which doesn't exist for a synthetic event built from nothing but a target point. pyglet's cocoa backend reads that raw delta field for `on_mouse_drag`, not "current position minus last position," so `Gem.on_mouse_drag(dx, dy)` was computing `self.x + 0` every frame - the gem's own move code was never wrong, it just never received a real number.

**the fix**
`position`'s setter now computes `delta_x, delta_y` itself (new point minus the previously stored `self._position`) before posting, and explicitly writes them into the event via `CGEventSetIntegerValueField` on `kCGMouseEventDeltaX`/`DeltaY` (fields 4 and 5). same trick applies to `on_mouse_motion` for free since that reads the same delta fields on a plain "moved" event.

## P1 and P2 stopped being plain colored squares

**the ask**
both players had been flat-colored `pyglet.shapes.Rectangle`s since day one - fine for testing collision/interaction logic, never meant to stay. real 16x20 pixel-art sprites landed in `assets/player1`/`assets/player2`, 12 per player: one idle + a 2-frame walk cycle for each of the 4 cardinal directions.

**the build**
`GridActor` (the shared base both `Player1`/`Player2` already used for the grid-stepping movement math) now loads a folder of named frames (`{direction}_idle.png`, `{direction}_walk1/2.png`) instead of taking a flat `color`, and renders a `pyglet.sprite.Sprite` scaled up to fill the same tile-sized footprint the old rectangle had. `step_towards` already receives `dx, dy` every frame from both players' `update()`, so direction-facing and "is currently walking" fall out of that for free - no separate input-reading needed. `facing` moved up from `Player1` into the base class (it was purely a "remember whichever direction was last non-zero" already, `Player2` gets it too now, unused for now but there for free) and `_set_animation` only reassigns `sprite.image` when the (direction, walking) pair actually changes, same "don't restart a loop that's already playing" rule `Gem`/`Gate` already follow - otherwise the walk cycle would restart from frame 0 every single frame and never visibly animate.

P2's pinching-highlight lost its old trick (`color = P2_COLOR-but-brighter`) since that only worked because the rectangle's fill color *was* its entire appearance - a real sprite's `.color` is a multiply-tint, which can only ever get darker or recolored, never brighter than the source art. swapped it for dropping the tint's blue channel while pinching (`entities/player_gesture.py`'s `PINCH_GLOW_TINT`), which reads as a warm highlight without washing the character out to solid white.

kept the external `player.rect.visible = False` used by both `state_overworld.py` and `state_dungeon.py`'s gate walk-in hide - renamed to `player.sprite.visible` at both call sites, since calling a `Sprite` `.rect` from the outside would've been actively misleading now that it isn't one.

## the overworld got walls

**the ask**: `overworld.tmx` existed but wasn't wired into `state_overworld.py` at all (still a flat green rectangle), and nothing stopped either player from walking anywhere, water included. wanted real per-tile collision driven by the actual map.

**the plan**: tag collision per *layer* in Tiled (a custom `blocks` bool property), not per individual tile - `overworld.tmx`'s layers are already organized semantically (`water`/`building`/`tree`/`bush`/`pilars` vs `ground`/`grass*`), so flagging ~5 layers beats hand-tagging hundreds of individual tile graphics. `world/tilemap.py`'s `TileMap` now reads each layer's `blocks` property while it's already walking tiles to build sprites, collecting blocked `(tiled_x, tiled_y)` cells into a set, and exposes `is_walkable(x, y, size)` - checks every tile cell a box touches, not just one corner, same "a point check misses things a real overlap wouldn't" lesson as the gate walk-in bug from earlier. `GridActor.step_towards` takes an optional `is_walkable` callback and just skips a blocked step (without resetting the cooldown, so bumping a wall re-checks every frame instead of eating a wasted wait once the way clears) - `None` elsewhere keeps the dungeon/treasure chamber exactly as free-roaming as they've always been.

**two landmines on the way in**:
1. `overworld.tmx` referenced an external tileset (`firstgid="6542" source="character.tsx"`) that doesn't exist anywhere in the repo - pytmx refuses to load the map at all with a dangling tileset reference. checked whether any placed tile actually used gids in that range first (max gid used across every layer: 6501, tileset starts at 6542) - confirmed unused, so just deleted that one `<tileset>` line.
2. first pass at `blocks` flags marked the whole map unwalkable - `water` turned out to be a full-map ocean *base* layer (1400/1400 tiles, sitting under every other layer including all the actual land) rather than just visible water, so blocking it blocked everything, land included. flagged this back before touching anything else instead of guessing a heuristic to paper over it - marius trimmed the water layer down to just the tiles actually sitting under nothing, re-checked after: 70% blocked now, in a shape that actually looks like an island instead of a solid wall of "no."

**collateral damage**: every hardcoded position in `state_overworld.py` (both spawns, the gate, all 4 gems, all 4 slots) had been picked before any real map existed and landed on now-blocked tiles once the collision was real. wrote a small nearest-open-spot search (expand outward in a ring from the original guess until `is_walkable` says yes, skipping anything already claimed by an earlier placement) and re-snapped all of them onto confirmed walkable ground, keeping the same rough layout - P1/P2 spawn together bottom-left-ish, gate off to the right, gems spread out with their slots clustered near the gate.

## tilemap animations - the TODO finally got picked up

`world/tilemap.py` had been carrying a TODO since it was first written: animated tiles (water, fire, traps, doors) only ever showed their first static frame, `layer.tiles()` resolves each gid straight to one image and stops there. marius finished a new `dungeon.tmx` (in `assets/chamber`, animated fire/spike/trap tiles this time) and asked to actually see them move.

**the build**: switched from `layer.tiles()` (x, y, image) to `layer.iter_data()` (x, y, gid) so the raw gid is available per placed tile, not just its pre-resolved static image. `TileMap._image_for_gid(gid)` checks `self.data.get_tile_properties_by_gid(gid)` for a `frames` property - pytmx already parses Tiled's `<animation>` tag into a list of `(gid, duration_ms)` pairs, one per Tile Animation Editor frame, no different than tile properties like "blocks". no `frames` -> same static image as before, zero behavior change. real frames -> builds a `pyglet.image.Animation` (looping forever, same as the gate/gem/shield loops elsewhere) from those frame gids' actual images, cached per-gid since the same animated water/fire tile easily gets placed hundreds of times across a map and there's no reason to build a hundred identical `Animation` objects for it.

**hiccup along the way**: the edit tool matched against a slightly misremembered version of the file's comments (missing a couple of dashes that used to be there) and failed silently-ish the first try - re-pulled the file straight through `nl -ba` instead of trusting memory, and on the second attempt the tail end of `__init__` (the `self.scale`/`self._offset_x/y` defaults `is_walkable()` needs) ended up physically relocated below the new `_image_for_gid` method's `return`, i.e. inside it, after its own return statement - dead code, caught immediately by the editor's "structurally unreachable" hint before it ever got run. moved those three lines back to where `__init__` actually ends.

confirmed against 4 different tmx files (`dungeon.tmx`, `overworld.tmx`, the old `Dungeon1.tmx` still live in `state_dungeon.py`, the treasure chamber's exterior) - real multi-frame animations built correctly (checked actual frame counts/durations/images, not just object types) everywhere, tile counts unchanged from before (the gid-vs-image iteration swap doesn't change which cells get placed, only how their image is resolved), zero regressions.

## dungeon collision, capped enemies, right-sized players

three asks landed together: give the dungeon the same real wall collision the overworld already has, cap combat at 3 enemies instead of up to 10, and shrink the players - they looked oversized next to the tilemap's 16px art.

**dungeon collision**: same wiring as the overworld - `Player1`/`Player2` get `collision_scale=self.tilemap.scale` at construction, `on_update` passes `self.tilemap.is_walkable` into both players' `update()`. checked `dungeon.tmx`'s `blocks` layers first before trusting them blindly (the overworld's `water` layer taught that lesson): `Floor` (598 tiles) and `walls` (320 tiles) are both flagged, and unlike `water` neither one is a full-map base layer - rendered the blocked-tile ascii map and it's a real room shape (outer walls plus a blocked structure in the middle), not a wall-to-wall landmine.

**collateral damage, again**: same pattern as the overworld gate/gems - the lever and both bullet-obstacles were positioned before any real wall geometry existed and landed inside walls once collision was real (the two obstacles sat inside the room's central blocked structure, the lever inside the outer wall - unreachable by `Interactable`'s proximity check). re-ran the same nearest-open-spot search from the overworld work and nudged all three onto walkable ground, same rough spot as before. player spawns and the gem/exit-gate positions were already fine, left alone.

**3 enemies**: `config.ENEMY_COUNT_MIN`/`ENEMY_COUNT_MAX` were `3`/`10` - dropped `ENEMY_COUNT_MAX` to `3` so `_start_combat`'s `random.randint(MIN, MAX)` always lands on exactly 3, no range left to roll higher.

**half-size players**: `GridActor` used to stretch the sprite to fill the entire 64px movement tile (`PLAYER_RENDER_SCALE` didn't exist, it was just `size`). added `PLAYER_RENDER_SCALE = 0.5` and a `_render_offset` that centers the now-32x32 sprite within its 64px tile - computed once at construction, reused every step alongside the existing `self.x`/`self.y` write. deliberately touches nothing else: movement stepping, the `collision_width`/`collision_height` box, `in_range()`/interactable radius, all still work off the full 64px tile exactly as before, only what gets drawn shrank and re-centered.

## the collision box was the size of the tile, not the size of the character

**the bug**: even on tiles that were genuinely walkable, both players kept getting stuck. `is_walkable()` was being asked "does the player's whole 64x64 movement tile fit here" - but the actual sprite art is 16x20 native pixels, tiny compared to a 64px box. measured it directly: on the 64px step grid, only 36 cells passed a full 64px box check, but 65 passed once the test box shrank to something closer to the sprite's real size - most of this map's walkable paths are only 1-2 native tiles wide, and a full 64px character can never fit through those no matter how open they look in Tiled, since the box always laps onto the blocked tiles to either side.

**the fix**: `GridActor` now derives a `collision_width`/`collision_height` from its own loaded sprite's actual native pixel size (16x20, read straight off the idle image instead of hardcoded) times the tilemap's own scale factor (`TileMap.scale`, now public) - so a screen with a `TileMap` gets a collision box shaped and sized like the real character (25.6 x 32 screen px here), not the 64px movement/rendering tile. `TileMap.is_walkable(x, y, width, height)` was generalized to take a width/height instead of assuming a square `size`, since the real character box isn't square (16 wide, 20 tall - noticed by marius, good catch, the earlier square-ish guess would've been wrong on the width/height ratio even if the total area happened to be close). `step_towards` centers that smaller box inside the 64px tile it's actually stepping to before checking it, movement/animation/interactable-radius math is completely untouched - only what gets handed to `is_walkable` changed. states without a `TileMap` (dungeon, treasure chamber) never pass `collision_scale`, so `collision_width/height` there just falls back to the full `size` and is inert anyway since those screens don't call `is_walkable` at all.



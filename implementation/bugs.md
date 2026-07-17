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



# here comes all logic for the shield since it can do 2 things now: get
# bigger/smaller (P1 screams, 3s window) and change color (P1 holds a pitch
# steady, 2s) - duration/breaking got cut entirely, once it's up it just
# stays up until F closes it again. both flows are one-shot: P2 picks a mode
# (hud button) -> P2 pinches the shield to actually start listening -> P1
# screams/sings -> it locks -> that button goes inactive, its job is done.
# only once *both* size and color have locked at least once does pinching
# the shield start dragging it instead of doing nothing - no more
# dragging/redoing either one halfway through, and no more re-arming a mode
# that's already locked in
import pyglet

import config
from entities.sprite_anim import load_animation
from input import audio_input

# the two flavors P2 can pick for P1's shield via the hud buttons
MODE_COLOR = "color"
MODE_SIZE = "size"

# the tornado shield sprite and the projectile sprite fold their color down
# to one of these 4 folders
_COLOR_FOLDERS = ["red", "blue", "green", "yellow"]

# assets/Tornado/<color>/001-005.png: the looping idle animation. used to
# also have a 006-009 "shield just broke" one-shot, but that only ever
# played when duration ran out - gone along with duration itself
TORNADO_FRAME_DURATION = 0.06
TORNADO_IDLE_FRAMES = tuple(range(1, 6))
TORNADO_SPRITE_PIXELS = 64  # source frames are 64x64, self.size scales from that


def frequency_bucket(frequency):
    # squishes whatever pitch audio_input picked up into one of the SHIELD_COLORS
    # slots exported so anything that wants "which of the 4 color buckets is
    # this pitch in" (PitchColorLock below, the melody gate) doesn't
    # reinvent it
    span = audio_input.high_freq - audio_input.min_freq
    normalized = (frequency - audio_input.min_freq) / span
    normalized = max(0.0, min(1.0, normalized))
    bucket = int(normalized * len(config.SHIELD_COLORS))
    return min(bucket, len(config.SHIELD_COLORS) - 1)


def frequency_to_color(frequency):
    # same pitch->color mapping the shield uses, exported so gate.py (and
    # anything else that wants "sing a color") doesn't reinvent this
    return config.SHIELD_COLORS[frequency_bucket(frequency)]


def colors_match(color, target, tolerance=35):
    # same "close enough" check gate.py/state_startmenu.py were each keeping
    # their own copy of, now also needed for enemy hit detection and the
    # shield-vs-bullet check in the dungeon
    return all(abs(color[i] - target[i]) <= tolerance for i in range(3))


def color_folder(color):
    # which of the 4 sprite-folders (red/blue/green/yellow) a SHIELD_COLORS
    # entry maps to - shared by the tornado shield, the projectiles and the
    # enemies, all stuck picking one of 4 discrete sprite sets, not a live tint
    for index, target in enumerate(config.SHIELD_COLORS):
        if target[:3] == tuple(color[:3]):
            return _COLOR_FOLDERS[index]
    return _COLOR_FOLDERS[
        0
    ]  # shouldn't happen, every color here comes from SHIELD_COLORS


def _tornado_idle_animation(folder):
    return load_animation(
        f"assets/Tornado/{folder}",
        TORNADO_IDLE_FRAMES,
        TORNADO_FRAME_DURATION,
        loop=True,
    )


class PitchColorLock:
    # shared "sing a color and hold it steady to lock it in" tracker - not
    # matching a pre-chosen target like the gate/gem/chest do, just picking
    # whichever of the 4 colors you hold steadiest for PITCH_LOCK_HOLD_TIME.
    # both the shield's color mode and the gun's color picker work off this
    # exact same class now ("same logic as shield coloring")
    def __init__(self):
        self.color = config.SHIELD_COLORS[0]
        self.locked = False
        self._bucket = None
        self._timer = 0.0

    def reset(self):
        # hud.py calls this the moment P2 (re)pinches the color button -
        # starts a fresh listening window, whatever was locked before is gone
        self.locked = False
        self._bucket = None
        self._timer = 0.0

    def update(self, frequency, dt):
        # returns True while actively tracking a pitch this frame (the
        # caller can refresh whatever visual shows "the color you're
        # currently on"), False while silent or already locked
        if self.locked:
            return False
        if frequency <= 0:
            self._bucket = None
            self._timer = 0.0
            return False

        bucket = frequency_bucket(frequency)
        if bucket != self._bucket:
            self._bucket = bucket
            self._timer = 0.0
        else:
            self._timer += dt

        self.color = config.SHIELD_COLORS[bucket]
        if self._timer >= config.PITCH_LOCK_HOLD_TIME:
            self.locked = True
        return True


class Shield:
    # a little tornado sprite, nonexistent on screen until P1 actually
    # raises it (F), stays up until F closes it again - no more duration or
    # breaking. flow per mode, same shape for both: P2 picks a mode via the
    # hud button (set_mode) -> P2 pinches the shield itself to actually
    # start listening (on_mouse_press, same "pinch the object to start" idiom
    # gate/chest/gem already use) -> P1 screams/sings -> it locks -> once
    # *both* modes are locked, pinching the shield grabs it for a drag
    # instead. either button can be pinched again at any time (renews that
    # one mode's window, same as picking it fresh) - doing so un-grabs
    # dragging again until that mode re-locks, same as the very first time
    def __init__(self, batch, group):
        self.x = 0
        self.y = 0
        self.size = (config.SHIELD_MIN_SIZE + config.SHIELD_MAX_SIZE) / 2

        self.active = False
        self.mode = None
        self.color = config.SHIELD_COLORS[0]
        self._folder = color_folder(self.color)
        self.listening = False
        self._grabbed = False

        # True while that mode's current value is locked in - False again
        # the moment set_mode() re-arms it, back to True once it re-locks.
        # both together gate dragging, see _both_done
        self._size_done = False
        self._color_done = False

        self._color_pick = PitchColorLock()
        # size mode: how long P1's been screaming this window, and the
        # loudest moment reached so far - see _update_size
        self._size_timer = 0.0
        self._size_peak = config.SHIELD_MIN_SIZE
        self._size_locked = True  # nothing to grow until size mode is picked

        # sprite only gets built the first time the shield is actually
        # raised - nothing to see (or animate) before that
        self._batch = batch
        self._group = group
        self.sprite = None

    def set_mode(self, mode):
        # hud.py calls this every time P2 clicks/pinches a mode button,
        # including re-picking a mode that's already locked - that's the
        # "renew" path, P2 can come back and redo either one whenever they
        # want. un-does that mode's "done" flag (so dragging pauses again
        # until it re-locks) and resets listening - P2 has to pinch the
        # shield again to actually kick the new window off, picking a mode
        # alone doesn't start P1's scream/sing counting
        self.mode = mode
        self.listening = False
        if mode == MODE_COLOR:
            self._color_pick.reset()
            self._color_done = False
        elif mode == MODE_SIZE:
            self._size_timer = 0.0
            self._size_peak = config.SHIELD_MIN_SIZE
            self._size_locked = False
            self._size_done = False

    def mode_done(self, mode):
        # hud.py can use this to show which buttons currently hold a locked
        # value vs. one mid-redo
        if mode == MODE_COLOR:
            return self._color_done
        if mode == MODE_SIZE:
            return self._size_done
        return False

    def _both_done(self):
        # dragging is gated on *both* modes currently being locked, not just
        # whichever one is currently selected - see on_mouse_press. renewing
        # either one (set_mode) clears its own done flag until it re-locks,
        # so this naturally goes False the instant P2 starts a redo and
        # True again once it finishes
        return self._size_done and self._color_done

    def _mode_locked(self):
        if self.mode == MODE_COLOR:
            return self._color_pick.locked
        if self.mode == MODE_SIZE:
            return self._size_locked
        return False

    def contains(self, x, y):
        half = self.size / 2
        return (
            self.x - half <= x <= self.x + half and self.y - half <= y <= self.y + half
        )

    def on_mouse_press(self, x, y):
        if not self.active or not self.contains(x, y):
            return False
        if self._both_done():
            # both modes locked at least once - pinching it now always
            # means "grab it to move it", never "start listening again"
            self._grabbed = True
        elif not self._mode_locked() and self.mode is not None:
            self.listening = True
        # else: current mode's already locked but the other one isn't done
        # yet - nothing to do until it is, no premature dragging and no
        # re-arming a mode that's already had its shot
        return True

    def note_still_pressed(self, x, y):
        # a held pinch very naturally spans the whole "pinch the shield to
        # start listening -> P1 screams/sings -> locks" sequence without
        # ever letting go in between - there's no second on_mouse_press in
        # that case to flip _grabbed, so a still-held pointer sitting on
        # the shield the instant *both* modes have locked (whichever one
        # finishes second) needs to grab it right then instead of silently
        # requiring a release-and-repress. state_dungeon.py calls this every
        # frame the button/pinch is down - same fix as Chest.note_still_pressed
        if self._both_done() and not self._grabbed and self.contains(x, y):
            self._grabbed = True

    def on_mouse_drag(self, dx, dy):
        if not self._grabbed:
            return
        half = self.size / 2
        self.x = min(max(self.x + dx, half), config.WIN_WIDTH - half)
        self.y = min(max(self.y + dy, half), config.WIN_HEIGHT - half)
        self.sprite.x = self.x
        self.sprite.y = self.y

    def on_mouse_release(self):
        self._grabbed = False

    def blocks(self, color):
        # only a raised, matching-color tornado actually absorbs a bullet -
        # anything else is meant to fly straight through it untouched
        return self.active and colors_match(color, self.color)

    def activate(self, x, y):
        # (re)raising it always spawns fresh beside P1's current spot.
        # clamped in case that spot lands past the edge of the screen.
        # color/size/mode all carry over from before though (only position
        # resets) - same as before duration existed at all
        half = self.size / 2
        self.x = min(max(x, half), config.WIN_WIDTH - half)
        self.y = min(max(y, half), config.WIN_HEIGHT - half)
        self.active = True
        self._grabbed = False

        if self.sprite is None:
            self.sprite = pyglet.sprite.Sprite(
                _tornado_idle_animation(self._folder),
                x=self.x,
                y=self.y,
                batch=self._batch,
                group=self._group,
            )
        else:
            self.sprite.x = self.x
            self.sprite.y = self.y
            self.sprite.image = _tornado_idle_animation(self._folder)
        self.sprite.scale = self.size / TORNADO_SPRITE_PIXELS
        self.sprite.visible = True

    def deactivate(self):
        self.active = False
        self._grabbed = False
        if self.sprite is not None:
            self.sprite.visible = False

    def toggle(self, x, y):
        # hooked up to the F key, x/y is where P1 wants it to appear
        if self.active:
            self.deactivate()
        else:
            self.activate(x, y)

    def update(self, dt):
        if not self.active:
            return

        if self.mode == MODE_COLOR:
            self._update_color(dt)
        elif self.mode == MODE_SIZE:
            self._update_size(dt)

    def _update_color(self, dt):
        if not self.listening:
            return  # P2 hasn't pinched the shield to start this window yet
        if not self._color_pick.update(audio_input.current_frequency, dt):
            return
        self.color = self._color_pick.color
        folder = color_folder(self.color)
        if folder != self._folder:
            # only swap the sprite image when the folder actually changes,
            # re-assigning it every frame would restart the idle loop nonstop
            self._folder = folder
            self.sprite.image = _tornado_idle_animation(folder)
        if self._color_pick.locked:
            self._color_done = True

    def _update_size(self, dt):
        if not self.listening:
            return  # P2 hasn't pinched the shield to start this window yet
        if self._size_locked:
            return

        self._size_timer += dt
        normalized = max(
            0.0, min(1.0, audio_input.current_volume / config.SHIELD_MAX_VOLUME)
        )
        live_size = config.SHIELD_MIN_SIZE + normalized * (
            config.SHIELD_MAX_SIZE - config.SHIELD_MIN_SIZE
        )
        # peak, not just the live value - "reaches after 3 seconds the
        # highest scream size", so the loudest moment in the window wins
        # even if P1 quiets down again before the window closes
        self._size_peak = max(self._size_peak, live_size)

        if self._size_timer >= config.SHIELD_SIZE_GROW_TIME:
            self._size_locked = True
            self._size_done = True
            self.size = self._size_peak
        else:
            self.size = live_size
        self.sprite.scale = self.size / TORNADO_SPRITE_PIXELS

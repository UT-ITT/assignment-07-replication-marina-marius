# here comes all logic for the shield since it can do 3 things
# get bigger/smaller, can be moved, can change color, shield hp
# this needs own file since it has a lot of logic
import pyglet

import config
from entities.sprite_anim import load_animation
from input import audio_input

# the three flavors P2 can pick for P1 shield via the hud buttons
MODE_COLOR = "color"
MODE_SIZE = "size"
MODE_TUNE = "tune"

# the tornado shield sprite and the projectile sprite fold their color down
# to one of these 4 folders
_COLOR_FOLDERS = ["red", "blue", "green", "yellow"]

# assets/tornado/<color>/001-009.png: 001-005 is the looping "has durability"
# idle animation, 006-009 is the one-shot "shield just broke" animation
TORNADO_FRAME_DURATION = 0.06
TORNADO_IDLE_FRAMES = tuple(range(1, 6))
TORNADO_BREAK_FRAMES = tuple(range(6, 10))
TORNADO_SPRITE_PIXELS = 64  # source frames are 64x64, self.size scales from that


def _frequency_bucket(frequency):
    # squishes whatever pitch audio_input picked up into one of the SHIELD_COLORS slots
    span = audio_input.high_freq - audio_input.min_freq
    normalized = (frequency - audio_input.min_freq) / span
    normalized = max(0.0, min(1.0, normalized))
    bucket = int(normalized * len(config.SHIELD_COLORS))
    return min(bucket, len(config.SHIELD_COLORS) - 1)


def frequency_to_color(frequency):
    # same pitch->color mapping the shield uses, exported so gate.py (and
    # anything else that wants "sing a color") doesn't reinvent this
    return config.SHIELD_COLORS[_frequency_bucket(frequency)]


def colors_match(color, target, tolerance=35):
    # same "close enough" check gate.py/state_startmenu.py were each keeping
    # their own copy of, now also needed for enemy hit detection and the
    # shield-vs-bullet check in the dungeon
    return all(abs(color[i] - target[i]) <= tolerance for i in range(3))


def color_folder(color):
    # which of the 4 sprite-folders (red/blue/green/yellow) a SHIELD_COLORS
    # entry maps to shared between the tornado shield and the projectiles,
    # both are stuck picking one of 4 discrete sprite sets, not a live tint
    for index, target in enumerate(config.SHIELD_COLORS):
        if target[:3] == tuple(color[:3]):
            return _COLOR_FOLDERS[index]
    return _COLOR_FOLDERS[0]  # shouldn't happen, every color here comes from SHIELD_COLORS


def _tornado_idle_animation(folder):
    return load_animation(
        f"assets/tornado/{folder}", TORNADO_IDLE_FRAMES, TORNADO_FRAME_DURATION, loop=True
    )


def _tornado_break_animation(folder):
    return load_animation(
        f"assets/tornado/{folder}", TORNADO_BREAK_FRAMES, TORNADO_FRAME_DURATION, loop=False
    )


class Shield:
    # a little tornado sprite, nonexistent on screen until P1 actually
    # raises it (F): 001-005 loops while it still has durability, 006-009
    # plays once when duration_left hits zero (it breaks, doesn't just
    # vanish), then it hides again until raised fresh. once up, P2 can
    # pinch/click + drag it around like the overworld crystal it spawns
    # at P1s position but doesn't keep following P1 after that, P2 owns
    # its position from there
    def __init__(self, batch, group):
        self.x = 0
        self.y = 0
        self.size = (config.SHIELD_MIN_SIZE + config.SHIELD_MAX_SIZE) / 2

        self.active = False
        self.mode = None
        self.duration_left = 0.0
        self.color = config.SHIELD_COLORS[0]
        self._folder = color_folder(self.color)
        self._breaking = False
        self._grabbed = False

        # keeping score of the notes P1 sang for the pitch-ladder mechanic
        self._tune_notes = []
        self._tune_timer = 0.0
        self._last_bucket = None

        # sprite only gets built the first time the shield is actually
        # raised nothing to see (or animate) before that
        self._batch = batch
        self._group = group
        self.sprite = None

    def set_mode(self, mode):
        # hud.py calls this the second P2 clicks/pinches a mode button
        self.mode = mode
        self._tune_notes = []
        self._tune_timer = 0.0
        self._last_bucket = None

    def contains(self, x, y):
        half = self.size / 2
        return self.x - half <= x <= self.x + half and self.y - half <= y <= self.y + half

    def on_mouse_press(self, x, y):
        # P2 mechanic: click/pinch the raised shield to grab it, same deal
        # as Pushable only takes effect while it's actually up
        if not self.active:
            return False
        if self.contains(x, y):
            self._grabbed = True
        return self._grabbed

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
        # only a raised, matching-color tornado actually absorbs a bullet
        # anything else is meant to fly straight through it untouched
        return self.active and colors_match(color, self.color)

    def activate(self, x, y):
        # (re)raising it always spawns fresh beside P1 P2 has to grab it
        # again to move it off that spot, it doesn't remember where it was
        # dropped last time. clamped same as a drag, in case the "beside P1"
        # spot lands past the edge of the screen
        half = self.size / 2
        self.x = min(max(x, half), config.WIN_WIDTH - half)
        self.y = min(max(y, half), config.WIN_HEIGHT - half)
        self.active = True
        self.duration_left = config.SHIELD_DEFAULT_DURATION
        self._breaking = False
        self._grabbed = False

        if self.sprite is None:
            self.sprite = pyglet.sprite.Sprite(
                _tornado_idle_animation(self._folder),
                x=self.x, y=self.y, batch=self._batch, group=self._group,
            )
            self.sprite.push_handlers(on_animation_end=self._on_break_animation_end)
        else:
            self.sprite.x = self.x
            self.sprite.y = self.y
            self.sprite.image = _tornado_idle_animation(self._folder)
        self.sprite.scale = self.size / TORNADO_SPRITE_PIXELS
        self.sprite.visible = True

    def deactivate(self):
        self.active = False
        self._breaking = False
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

        self.duration_left -= dt
        if self.duration_left <= 0:
            self._break()
            return

        if self.mode == MODE_COLOR:
            self._update_color(audio_input.current_frequency)
        elif self.mode == MODE_SIZE:
            self._update_size(audio_input.current_volume)
        elif self.mode == MODE_TUNE:
            self._update_tune(audio_input.current_frequency, dt)

    def _break(self):
        # duration ran out mid-fight stops blocking and grabbing
        # immediately, the break animation is purely cosmetic from here on
        self.active = False
        self._breaking = True
        self._grabbed = False
        self.sprite.image = _tornado_break_animation(self._folder)

    def _on_break_animation_end(self):
        if not self._breaking:
            return  # a fresh activate()/deactivate() already swapped the image, not our event to handle
        self._breaking = False
        self.sprite.visible = False

    def _update_color(self, frequency):
        if frequency <= 0:
            return
        self.color = frequency_to_color(frequency)
        folder = color_folder(self.color)
        if folder != self._folder:
            # only swap the sprite image when the folder actually changes,
            # re-assigning it every frame would restart the idle loop nonstop
            self._folder = folder
            self.sprite.image = _tornado_idle_animation(folder)

    def _update_size(self, volume):
        normalized = max(0.0, min(1.0, volume / config.SHIELD_MAX_VOLUME))
        self.size = config.SHIELD_MIN_SIZE + normalized * (config.SHIELD_MAX_SIZE - config.SHIELD_MIN_SIZE)
        self.sprite.scale = self.size / TORNADO_SPRITE_PIXELS

    def _update_tune(self, frequency, dt):
        self._tune_timer += dt
        if self._tune_notes and self._tune_timer > config.SHIELD_TUNE_SEQUENCE_TIMEOUT:
            self._tune_notes = []
            self._last_bucket = None

        if frequency <= 0:
            self._last_bucket = None
            return

        bucket = _frequency_bucket(frequency)
        if bucket == self._last_bucket:
            return  # still holding the same note, don't count it twice

        self._last_bucket = bucket
        self._tune_timer = 0.0
        self._tune_notes.append(bucket)
        if len(self._tune_notes) < 3:
            return

        # did the last three notes climb up (boost) or fall down (penalty)?
        a, b, c = self._tune_notes[-3:]
        if a < b < c:
            self.duration_left += config.SHIELD_TUNE_BOOST
        elif a > b > c:
            self.duration_left = max(0.0, self.duration_left - config.SHIELD_TUNE_PENALTY)
        self._tune_notes = []

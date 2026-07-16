# here comes all logic for the shield since it can do 3 things
# get bigger/smaller, can be moved, can change color, shield hp
# this needs own file since it has a lot of logic
import pyglet

import config
from input import audio_input

# the three flavors P2 can pick for P1 shield via the hud buttons
MODE_COLOR = "color"
MODE_SIZE = "size"
MODE_TUNE = "tune"

DEFAULT_COLOR = (255, 255, 255)


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


class Shield:
    # still just a rectangle, a sprite shows up here once somebody draws one (not me)
    def __init__(self, x, y, batch, group):
        self.x = x
        self.y = y
        self.size = (config.SHIELD_MIN_SIZE + config.SHIELD_MAX_SIZE) / 2

        self.active = False
        self.mode = None
        self.duration_left = 0.0

        # keeping score of the notes P1 sang for the pitch-ladder mechanic
        self._tune_notes = []
        self._tune_timer = 0.0
        self._last_bucket = None

        self.rect = pyglet.shapes.Rectangle(
            x - self.size / 2, y - self.size / 2, self.size, self.size,
            color=DEFAULT_COLOR, batch=batch, group=group,
        )
        self.rect.opacity = config.SHIELD_INACTIVE_OPACITY

    def set_mode(self, mode):
        # hud.py calls this the second P2 clicks/pinches a mode button
        self.mode = mode
        self._tune_notes = []
        self._tune_timer = 0.0
        self._last_bucket = None

    def follow(self, x, y):
        # "spawns in front of P1" only means something if it actually stays
        # in front of P1 - without this it just sits wherever it was first
        # placed while P1 wanders off, which makes blocking bullets pointless
        self.x = x
        self.y = y
        self.rect.x = x - self.size / 2
        self.rect.y = y - self.size / 2

    def activate(self):
        self.active = True
        self.duration_left = config.SHIELD_DEFAULT_DURATION
        self.rect.opacity = 255

    def deactivate(self):
        self.active = False
        self.rect.opacity = config.SHIELD_INACTIVE_OPACITY

    def toggle(self):
        # hooked up to the F key
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def update(self, dt):
        if not self.active:
            return

        self.duration_left -= dt
        if self.duration_left <= 0:
            self.deactivate()
            return

        if self.mode == MODE_COLOR:
            self._update_color(audio_input.current_frequency)
        elif self.mode == MODE_SIZE:
            self._update_size(audio_input.current_volume)
        elif self.mode == MODE_TUNE:
            self._update_tune(audio_input.current_frequency, dt)

    def _update_color(self, frequency):
        if frequency <= 0:
            return
        bucket = _frequency_bucket(frequency)
        self.rect.color = config.SHIELD_COLORS[bucket][:3]

    def _update_size(self, volume):
        normalized = max(0.0, min(1.0, volume / config.SHIELD_MAX_VOLUME))
        new_size = config.SHIELD_MIN_SIZE + normalized * (config.SHIELD_MAX_SIZE - config.SHIELD_MIN_SIZE)
        self.size = new_size
        self.rect.width = new_size
        self.rect.height = new_size
        self.rect.x = self.x - new_size / 2
        self.rect.y = self.y - new_size / 2

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

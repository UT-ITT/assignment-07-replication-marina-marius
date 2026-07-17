# the treasure chamber's actual prize: floats in its neutral look until P2
# clicks it, then P1 sings it into the right color and holds it - same
# "sing to match, hold ~2s, lock" trick as gate.py/chest.py, just with a
# floating/idle/reveal animation instead of a flat color swap
#
# sprites: assets/gem/<basic|red|blue|green|yellow>/tile000-007.png.
# basic/tile000-007 is the ambient "floating on the map" loop before anyone
# touches it. tile005.png (any folder) is the single "holding still,
# listening" frame basic while silent, live color-folder while P1 sings.
# once locked, tile001-007 of the matched color loops as the reveal.
import random

import pyglet

import config
from entities.shield import color_folder, colors_match, frequency_to_color
from entities.sprite_anim import load_animation, load_image
from input import audio_input
from world.gate import LOCK_HOLD_TIME, COLOR_TOLERANCE

GEM_SPRITE_PIXELS = 32
FLOAT_FRAME_DURATION = 0.12
REVEAL_FRAME_DURATION = 0.12
FLOAT_FRAMES = tuple(range(0, 8))
REVEAL_FRAMES = tuple(range(1, 8))


def _float_animation():
    return load_animation(
        "assets/gem/basic", FLOAT_FRAMES, FLOAT_FRAME_DURATION, loop=True, name_prefix="tile"
    )


def _idle_image(folder):
    return load_image(f"assets/gem/{folder}/tile005.png")


def _reveal_animation(folder):
    return load_animation(
        f"assets/gem/{folder}", REVEAL_FRAMES, REVEAL_FRAME_DURATION, loop=True, name_prefix="tile"
    )


class Gem:
    # states: floating (ambient loop, not clicked yet) -> listening (P2
    # clicked, frozen on tile005 basic while silent, live color-folder
    # while P1 sings) -> locked (target color held long enough, loops the
    # reveal animation in that color forever after)
    def __init__(self, x, y, size, batch, group, on_locked=None, target_color=None, stats=None):
        self.x = x
        self.y = y
        self.size = size
        self.target_color = target_color or random.choice(config.SHIELD_COLORS)
        self.target_folder = color_folder(self.target_color)
        self.on_locked = on_locked
        self.stats = stats

        self.listening = False
        self.locked = False
        self._match_timer = 0.0

        self.sprite = pyglet.sprite.Sprite(
            _float_animation(), x=x, y=y, batch=batch, group=group,
        )
        self.sprite.scale = size / GEM_SPRITE_PIXELS

    def contains(self, x, y):
        half = self.size / 2
        return self.x - half <= x <= self.x + half and self.y - half <= y <= self.y + half

    def on_mouse_press(self, x, y):
        if self.locked or self.listening or not self.contains(x, y):
            return False
        self.listening = True
        self.sprite.image = _idle_image("basic")
        return True

    def update(self, dt):
        if not self.listening or self.locked:
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.sprite.image = _idle_image("basic")
            return

        color = frequency_to_color(frequency)
        self.sprite.image = _idle_image(color_folder(color))

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock()
        else:
            self._match_timer = 0.0

    def _lock(self):
        self.locked = True
        self.listening = False
        self.sprite.image = _reveal_animation(self.target_folder)
        if self.on_locked:
            self.on_locked()

    def delete(self):
        self.sprite.delete()

# the gem: sing it the right color, and (if it's given a target_slot) drag
# it into place same two tricks world/gate.py and Chest already know,
# just on an animated object instead of a flat color swap. used solo as a
# single "color it to trigger something"

import random

import pyglet

import config
from entities.shield import color_folder, colors_match, frequency_to_color
from entities.sprite_anim import load_animation
from input import audio_input
from world.gate import LOCK_HOLD_TIME, COLOR_TOLERANCE
from world.interactable import Interactable

GEM_SPRITE_PIXELS = 32
GEM_FRAME_DURATION = 0.12
GEM_LOOP_FRAMES = tuple(range(0, 8))
SLOT_TOLERANCE = 24


def _gem_loop_animation(folder):
    return load_animation(
        f"assets/gem/{folder}", GEM_LOOP_FRAMES, GEM_FRAME_DURATION, loop=True, name_prefix="tile"
    )


class Gem(Interactable):
    # states: floating (ambient basic loop, not clicked yet) -> listening
    # (P2 clicked, loop keeps playing but in whichever color folder P1's
    # live pitch maps to, basic while silent) -> colored (target color
    # held long enough, loops that color forever) -> [only if a
    # target_slot was given] draggable -> solved (dragged onto its slot).
    # no target_slot means colored already *is* solved - on_solved fires
    # the instant the color locks, nothing left to drag anywhere
    def __init__(self, x, y, size, batch, group, on_solved=None, target_color=None,
                 target_slot=None, stats=None,
                 hint="P2: click/pinch to wake it up, then P1: sing its color"):

        self.x = x
        self.y = y
        self.size = size
        self.target_color = target_color or random.choice(config.SHIELD_COLORS)
        self.target_folder = color_folder(self.target_color)
        self.color_name = config.SHIELD_COLOR_NAMES[config.SHIELD_COLORS.index(self.target_color)]
        self.target_slot = target_slot
        self.on_solved = on_solved
        self.stats = stats

        self.listening = False
        self.colored = False
        self.solved = False
        self.grabbed = False
        self._match_timer = 0.0
        self._folder = "basic"

        self.sprite = pyglet.sprite.Sprite(
            _gem_loop_animation("basic"), x=x, y=y, batch=batch, group=group,
        )
        self.sprite.scale = size / GEM_SPRITE_PIXELS

        self.hint_label = pyglet.text.Label(
            hint, x=x, y=y + size / 2 + 10,
            anchor_x="center", anchor_y="bottom",
            font_name=config.FONT_NAME, font_size=11, color=(255, 255, 255, 255),
            batch=batch, group=group,
        )
        self.hint_label.visible = False

        self.slot_marker = None
        if target_slot is not None:
            # a Box outline showing where this gem actually belongs
            self.slot_marker = pyglet.shapes.Box(
                target_slot[0] - size / 2, target_slot[1] - size / 2, size, size,
                thickness=3, color=self.target_color[:3], batch=batch, group=group,
            )

    def contains(self, x, y):
        half = self.size / 2
        return self.x - half <= x <= self.x + half and self.y - half <= y <= self.y + half

    def on_mouse_press(self, x, y):
        if self.solved or not self.contains(x, y):
            return False
        if not self.colored:
            self.listening = True
            self.hint_label.text = f"P1: sing {self.color_name.upper()} to color it!"
            print(f"[gem {self.color_name}] press -> now listening")
        elif self.target_slot is not None:
            self.grabbed = True
            print(f"[gem {self.color_name}] press -> GRABBED at ({self.x:.0f}, {self.y:.0f})")
        return True

    def on_mouse_drag(self, dx, dy):
        if not self.grabbed:
            return
        half = self.size / 2
        self.x = min(max(self.x + dx, half), config.WIN_WIDTH - half)
        self.y = min(max(self.y + dy, half), config.WIN_HEIGHT - half)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.hint_label.x = self.x
        self.hint_label.y = self.y + self.size / 2 + 10
        print(f"[gem {self.color_name}] dragged to ({self.x:.0f}, {self.y:.0f})")

    def on_mouse_release(self):
        if not self.grabbed:
            return
        print(f"[gem {self.color_name}] release at ({self.x:.0f}, {self.y:.0f}) -> checking slot")
        self.grabbed = False
        self._check_solved()

    def _check_solved(self):
        slot_x, slot_y = self.target_slot  # type: ignore
        off_x, off_y = abs(self.x - slot_x), abs(self.y - slot_y)
        if off_x > SLOT_TOLERANCE or off_y > SLOT_TOLERANCE:
            print(
                f"[gem {self.color_name}] not close enough to slot "
                f"(off by {off_x:.0f}, {off_y:.0f}, tolerance={SLOT_TOLERANCE})"
            )
            return
        self.x, self.y = slot_x, slot_y
        self.sprite.x, self.sprite.y = slot_x, slot_y
        self.solved = True
        self.hint_label.visible = False
        print(f"[gem {self.color_name}] SOLVED")
        if self.on_solved:
            self.on_solved()

    def update(self, dt):
        if not self.listening or self.colored:
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self._set_folder("basic")
            return

        color = frequency_to_color(frequency)
        self._set_folder(color_folder(color))

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock_color()
        else:
            self._match_timer = 0.0

    def _set_folder(self, folder):
        if folder == self._folder:
            return  # already playing this loop, reassigning would restart it
        self._folder = folder
        self.sprite.image = _gem_loop_animation(folder)

    def _lock_color(self):
        self.colored = True
        self.listening = False
        self._set_folder(self.target_folder)
        if self.target_slot is None:
            self.solved = True
            self.hint_label.visible = False
            if self.on_solved:
                self.on_solved()
        else:
            self.hint_label.text = "P2: click/pinch + drag it onto its marked spot"

    def delete(self):
        self.sprite.delete()
        self.hint_label.delete()
        if self.slot_marker is not None:
            self.slot_marker.delete()

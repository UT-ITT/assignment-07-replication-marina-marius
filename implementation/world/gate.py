# here comes all gate logic (dont know actually if we need it seperately but would be i think easier to debug and look for stuff)
# also normaly you would do everything seperately e.g. unity so why not here also hihi
import random

import pyglet

import config
from entities.shield import (
    color_folder,
    colors_match,
    frequency_bucket,
    frequency_to_color,
)
from entities.sprite_anim import load_animation, load_image
from input import audio_input
from world.interactable import Interactable

LOCK_HOLD_TIME = 0.5
COLOR_TOLERANCE = 35
GATE_SPRITE_PIXELS = 32
GATE_FRAME_DURATION = 0.12
GATE_LOOP_FRAMES = tuple(range(0, 6))


def _gate_loop_animation(folder):

    return load_animation(
        f"assets/gate/{folder}",
        GATE_LOOP_FRAMES,
        GATE_FRAME_DURATION,
        loop=True,
        name_prefix="tile",
        anchor_center=False,
    )


def _gate_listening_image(folder):
    return load_image(f"assets/gate/{folder}/tile000.png", anchor_center=False)


def random_melody(length=None):

    length = length or random.randint(
        config.MELODY_LENGTH_MIN, config.MELODY_LENGTH_MAX
    )
    note_count = len(config.SHIELD_COLORS)
    melody = []
    for _ in range(length):
        choices = [
            b for b in range(note_count) if b != (melody[-1] if melody else None)
        ]
        melody.append(random.choice(choices))
    return melody


class Gate(Interactable):

    def __init__(
        self,
        x,
        y,
        size,
        batch,
        group,
        on_unlock=None,
        target_color=None,
        melody=None,
        stats=None,
        walk_in_required=True,
        hint="P2: click/pinch to wake it up, then P1: sing its color",
    ):

        self.x = x
        self.y = y
        self.size = size
        self.walk_in_required = walk_in_required

        # ---- unlock target: single color, or a melody of them ---------
        self.melody = random_melody() if melody is True else melody
        if self.melody:
            self.target_color = None
            # unlocked glow just borrows the last note's color folder,
            # nothing about "unlocked" needs its own asset
            self.target_folder = color_folder(config.SHIELD_COLORS[self.melody[-1]])
            self.color_name = " - ".join(
                config.SHIELD_COLOR_NAMES[bucket] for bucket in self.melody
            )
            self._melody_progress = 0
            self._last_bucket = None
            self._note_timer = 0.0
        else:
            self.target_color = target_color or random.choice(config.SHIELD_COLORS)
            self.target_folder = color_folder(self.target_color)
            self.color_name = config.SHIELD_COLOR_NAMES[
                config.SHIELD_COLORS.index(self.target_color)
            ]

        self.on_unlock = on_unlock
        # optional GameStats if given, every sung frame while listening
        # counts toward the end screen's pitch accuracy ratio
        self.stats = stats

        self.listening = False
        self.locked = False
        self._match_timer = 0.0

        # ---- walk-in requirement ---------------------------------------
        self._entered = set()  # holds whichever player object(s) have walked in

        self.sprite = pyglet.sprite.Sprite(
            _gate_loop_animation("basic"),
            x=x,
            y=y,
            batch=batch,
            group=group,
        )
        self.sprite.scale = size / GATE_SPRITE_PIXELS

        self.hint_label = pyglet.text.Label(
            hint,
            x=x + size / 2,
            y=y + size + 10,
            anchor_x="center",
            anchor_y="bottom",
            font_name=config.FONT_NAME,
            font_size=11,
            color=(255, 255, 255, 255),
            batch=batch,
            group=group,
        )
        self.hint_label.visible = False

    def on_mouse_press(self, x, y):
        if self.locked or not self.contains(x, y):
            return False
        self.listening = True
        if self.melody:
            self.hint_label.text = (
                f"P1: sing {self.color_name.upper()} in order to unlock it!"
            )
        else:
            self.hint_label.text = f"P1: sing {self.color_name.upper()} to unlock it!"
        self.sprite.image = _gate_listening_image("basic")
        return True

    def update(self, dt):
        if not self.listening or self.locked:
            return

        if self.melody:
            self._update_melody(dt)
        else:
            self._update_single_pitch(dt)

    def _update_single_pitch(self, dt):
        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.sprite.image = _gate_listening_image("basic")
            return

        color = frequency_to_color(frequency)
        self.sprite.image = _gate_listening_image(color_folder(color))

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock()
        else:
            self._match_timer = 0.0

    def _update_melody(self, dt):
        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._last_bucket = None
            self.sprite.image = _gate_listening_image("basic")
        else:
            self.sprite.image = _gate_listening_image(
                color_folder(frequency_to_color(frequency))
            )

        self._note_timer += dt
        if self._melody_progress and self._note_timer > config.MELODY_NOTE_TIMEOUT:
            self._melody_progress = 0
            self._last_bucket = None
            self._note_timer = 0.0
            self.hint_label.text = (
                f"P1: sing {self.color_name.upper()} in order to unlock it!"
            )

        if frequency <= 0:
            return

        bucket = frequency_bucket(frequency)
        if bucket == self._last_bucket:
            return  # still holding the same note, don't count it twice

        self._last_bucket = bucket
        self._note_timer = 0.0

        expected = self.melody[self._melody_progress]  # type: ignore
        matched = bucket == expected
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._melody_progress += 1
            if self._melody_progress >= len(self.melody):  # type: ignore
                self._lock()
            else:
                self.hint_label.text = (
                    f"{self._melody_progress}/{len(self.melody)} - keep going: "  # type: ignore
                    f"{self.color_name.upper()}"
                )
        else:
            # wrong note, start the sequence over from scratch
            self._melody_progress = 0
            self.hint_label.text = (
                f"P1: sing {self.color_name.upper()} in order to unlock it!"
            )

    def _lock(self):
        self.locked = True
        self.listening = False
        self.sprite.image = _gate_loop_animation(self.target_folder)
        if self.walk_in_required:
            self.hint_label.text = "P1 & P2: both walk into the gate to go through!"
        elif self.on_unlock:
            self.on_unlock()

    def try_enter(self, player, x, y, width=config.TILE_SIZE, height=config.TILE_SIZE):

        if not self.walk_in_required or not self.locked or player in self._entered:
            return False

        overlaps = (
            x < self.x + self.size
            and x + width > self.x
            and y < self.y + self.size
            and y + height > self.y
        )
        if not overlaps:
            return False

        self._entered.add(player)
        if len(self._entered) < 2:
            self.hint_label.text = "one of you is through - the other: walk in too!"
        elif self.on_unlock:
            self.on_unlock()
        return True

    def delete(self):
        self.sprite.delete()
        self.hint_label.delete()

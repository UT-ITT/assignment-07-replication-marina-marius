# here comes the treasure chamber's chest logic: sing it the right color,
# then drag it onto its marked spot - do both and it's solved. combines the
# same two tricks world/gate.py and Pushable already know, just on one object
import pyglet

import config
from entities.shield import colors_match, frequency_to_color
from input import audio_input
from world.gate import LOCK_HOLD_TIME, COLOR_TOLERANCE
from world.interactable import Interactable

SLOT_TOLERANCE = 24
LOCKED_COLOR = (60, 60, 60)


class Chest(Interactable):
    # states: locked (not its turn) -> idle (its turn, is_active) ->
    # listening (P1 singing) -> colored (locked in, draggable) -> solved
    def __init__(self, x, y, size, target_color, target_slot, batch, group,
                 on_solved=None, stats=None, **kwargs):
        kwargs.setdefault("idle_color", LOCKED_COLOR)
        kwargs.setdefault("hint", "P2: click/pinch to wake it up, then P1: sing its color")
        super().__init__(x, y, size, batch, group, **kwargs)
        self.target_color = target_color
        self.color_name = config.SHIELD_COLOR_NAMES[config.SHIELD_COLORS.index(target_color)]
        self.target_slot = target_slot
        self.on_solved = on_solved
        self.stats = stats

        self.is_active = False
        self.listening = False
        self.colored = False
        self.solved = False
        self.grabbed = False
        self._match_timer = 0.0

        # outline showing where this chest actually belongs, visible from the start
        self.slot_marker = pyglet.shapes.BorderedRectangle(
            target_slot[0], target_slot[1], size, size, border=3,
            color=(0, 0, 0, 0), border_color=target_color[:3],
            batch=batch, group=group,
        )

    def activate(self):
        # TreasureState calls this once it's this chest turn in the sequence
        self.is_active = True
        self.rect.color = config.PITCH_SILENCE_COLOR

    def on_mouse_press(self, x, y):
        if not self.is_active or self.solved or not self.contains(x, y):
            return False
        if not self.colored:
            self.listening = True
            self.hint_label.text = f"P1: sing {self.color_name.upper()} to color it!"
        else:
            self.grabbed = True
        return True

    def on_mouse_drag(self, dx, dy):
        if not self.grabbed:
            return
        self.x = min(max(self.x + dx, 0), config.WIN_WIDTH - self.size)
        self.y = min(max(self.y + dy, 0), config.WIN_HEIGHT - self.size)
        self.rect.x = self.x
        self.rect.y = self.y
        self.hint_label.x = self.x + self.size / 2
        self.hint_label.y = self.y + self.size + 10

    def on_mouse_release(self):
        if not self.grabbed:
            return
        self.grabbed = False
        self._check_solved()

    def _check_solved(self):
        slot_x, slot_y = self.target_slot
        if abs(self.x - slot_x) > SLOT_TOLERANCE or abs(self.y - slot_y) > SLOT_TOLERANCE:
            return
        self.x, self.y = slot_x, slot_y
        self.rect.x, self.rect.y = slot_x, slot_y
        self.solved = True
        self.hint_label.visible = False
        if self.on_solved:
            self.on_solved()

    def update(self, dt):
        if not self.is_active or self.solved or not self.listening:
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.rect.color = config.PITCH_SILENCE_COLOR
            return

        color = frequency_to_color(frequency)
        self.rect.color = color

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock_color()
        else:
            self._match_timer = 0.0

    def _lock_color(self):
        self.colored = True
        self.listening = False
        self.rect.color = self.target_color[:3]
        self.hint_label.text = "P2: click/pinch + drag it onto its marked spot"

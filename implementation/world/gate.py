# here comes all gate logic (dont know actually if we need it seperately but would be i think easier to debug and look for stuff)
# also normaly you would do everything seperately e.g. unity so why not here also hihi
import random

import config
from entities.shield import colors_match, frequency_to_color
from input import audio_input
from world.interactable import Interactable

LOCK_HOLD_TIME = 2.0
COLOR_TOLERANCE = 35


class Gate(Interactable):
    # P2 clicks/pinches to wake it up, then P1 sings its target color until
    # it locks shared by the overworld gate now, and the dungeon/treasure
    # color-locks later, so this mechanic only gets built once
    def __init__(self, x, y, size, batch, group, on_unlock=None,
                 target_color=None, stats=None, **kwargs):
        kwargs.setdefault("idle_color", config.PITCH_SILENCE_COLOR)
        kwargs.setdefault("hint", "P2: click/pinch to wake it up, then P1: sing its color")
        super().__init__(x, y, size, batch, group, **kwargs)
        self.target_color = target_color or random.choice(config.SHIELD_COLORS)
        self.color_name = config.SHIELD_COLOR_NAMES[config.SHIELD_COLORS.index(self.target_color)]
        self.on_unlock = on_unlock
        # optional GameStats if given, every sung frame while listening
        # counts toward the end screen's pitch accuracy ratio
        self.stats = stats

        self.listening = False
        self.locked = False
        self._match_timer = 0.0

    def on_mouse_press(self, x, y):
        if self.locked or not self.contains(x, y):
            return False
        self.listening = True
        self.hint_label.text = f"P1: sing {self.color_name.upper()} to unlock it!"
        return True

    def update(self, dt):
        if not self.listening or self.locked:
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
                self._lock()
        else:
            self._match_timer = 0.0

    def _lock(self):
        self.locked = True
        self.listening = False
        self.rect.color = self.target_color[:3]
        if self.on_unlock:
            self.on_unlock()

# P2's gun: L toggles whether it's drawn (mirrors shield.py's F toggle).
# coloring it works exactly like the shield's color mode now - P2 pinches
# the gun hud button, P1 holds a pitch steady for PITCH_LOCK_HOLD_TIME and
# whatever color that is locks in, loaded into every bullet fired from then
# on until P2 pinches the button again to pick a new one
from entities.shield import PitchColorLock
from input import audio_input


class Gun:
    def __init__(self):
        self.active = False
        self._color_pick = PitchColorLock()

    @property
    def color(self):
        return self._color_pick.color

    @property
    def locked(self):
        return self._color_pick.locked

    def toggle(self):
        # hooked up to the L key, via Player2.handle_key_press
        self.active = not self.active

    def start_color_pick(self):
        # hooked up to the gun hud button -> P2 (re)pinching it starts a fresh "sing a color 
        # and hold it" window, same as the shields
        self._color_pick.reset()

    def update(self, dt):
        if not self.active:
            return
        self._color_pick.update(audio_input.current_frequency, dt)

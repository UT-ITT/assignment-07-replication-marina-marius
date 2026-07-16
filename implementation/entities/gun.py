# P2's gun: C toggles whether it's drawn (mirrors shield.py's F toggle), and
# while unlocked its color live-tracks whatever pitch P1 is singing - same
# "sing a color" trick as everywhere else, just loaded into bullets this time
from entities.shield import frequency_to_color
from input import audio_input


class Gun:
    def __init__(self):
        self.active = False
        self.locked = False
        self.color = frequency_to_color(0)

    def toggle(self):
        # hooked up to the C key, via Player2.handle_key_press
        self.active = not self.active

    def toggle_lock(self):
        # hooked up to the gun hud button
        self.locked = not self.locked

    def update(self, dt):
        if self.locked:
            return
        frequency = audio_input.current_frequency
        if frequency > 0:
            self.color = frequency_to_color(frequency)

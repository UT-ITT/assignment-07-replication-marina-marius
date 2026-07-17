# here comes the logic for P1: WASD to walk, E to poke stuff, F for shield
from pyglet.window import key

import config
from entities.grid_actor import GridActor


def pitch_to_color(pitch):
    min_pitch = 100
    max_pitch = 1000
    steps = 8

    normalized_pitch = (pitch - min_pitch) / (max_pitch - min_pitch)
    normalized_pitch = max(0.0, min(1.0, normalized_pitch))

    # snap to one of a fixed number of steps instead of a smooth gradient,
    # so small pitch jitter while singing doesn't constantly shift the color
    bucket = min(int(normalized_pitch * steps), steps - 1)
    stepped_pitch = bucket / (steps - 1)

    r = int(stepped_pitch * 255)
    g = 0
    b = int((1 - stepped_pitch) * 255)

    return (r, g, b)


class Player1(GridActor):

    def __init__(self, x, y, batch, group, shield=None):
        super().__init__(x, y, config.P1_COLOR[:3], batch, group)
        # not every screen has a shield (looking at you, overworld), so this can stay None
        self.shield = shield

    def update(self, dt, keys):
        dy = self.axis_from_keys(keys, key.S, key.W)
        dx = 0 if dy != 0 else self.axis_from_keys(keys, key.A, key.D)
        self.step_towards(dt, dx, dy)

    def handle_key_press(self, symbol, interactables=()):
        if symbol == key.F and self.shield is not None:
            self.shield.toggle()
        elif symbol == key.E:
            self.try_interact(interactables)

    def try_interact(self, interactables, radius=64):
        for interactable in interactables:
            if abs(self.x - interactable.x) <= radius and abs(self.y - interactable.y) <= radius:
                interactable.interact()
                return interactable
        return None

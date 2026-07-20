# here comes the logic for P1: WASD to walk, E to poke stuff, F for shield
from pyglet.window import key

import config
from entities.grid_actor import GridActor


class Player1(GridActor):

    def __init__(self, x, y, batch, group, shield=None, collision_scale=None):
        super().__init__(
            x, y, "assets/player1", batch, group, collision_scale=collision_scale
        )
        # not every screen has a shield (looking at you, overworld), so this can stay None
        self.shield = shield

    def update(self, dt, keys, is_walkable=None):
        dy = self.axis_from_keys(keys, key.S, key.W)
        dx = 0 if dy != 0 else self.axis_from_keys(keys, key.A, key.D)
        self.step_towards(dt, dx, dy, is_walkable)

    def handle_key_press(self, symbol, interactables=()):
        if symbol == key.F and self.shield is not None:
            # raising it always spawns fresh beside P1, one tile out in
            # whichever direction P1 is currently facing see Shield.activate
            center_x, center_y = self.x + self.size / 2, self.y + self.size / 2
            face_x, face_y = self.facing
            self.shield.toggle(
                center_x + face_x * config.TILE_SIZE,
                center_y + face_y * config.TILE_SIZE,
            )
        elif symbol == key.E:
            self.try_interact(interactables)

    def try_interact(self, interactables, radius=64):
        for interactable in interactables:
            if (
                abs(self.x - interactable.x) <= radius
                and abs(self.y - interactable.y) <= radius
            ):
                interactable.interact()
                return interactable
        return None

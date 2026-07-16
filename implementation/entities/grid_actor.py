# P1 and P2 both need the same "walk exactly one tile, then wait" movement
# instead of sliding around (pokemon vibes), so instead of
# copy-pasting the stepping math into both player files it lives here once
import pyglet

import config


class GridActor:

    # reuse PLAYER_SPEED so "tiles per second" from config.py still means
    # something even though nobody is sliding continuously anymore
    STEP_INTERVAL = config.TILE_SIZE / config.PLAYER_SPEED

    def __init__(self, x, y, color, batch, group, size=config.TILE_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self._step_timer = 0.0

        self.rect = pyglet.shapes.Rectangle(
            x, y, size, size, color=color, batch=batch, group=group,
        )

    @property
    def color(self):
        return self.rect.color

    @color.setter
    def color(self, value):
        self.rect.color = value

    @staticmethod
    def axis_from_keys(keys, negative_key, positive_key):
        # turns a key pair into -1/0/1 - mash both at once and they just cancel out
        if keys[positive_key] and not keys[negative_key]:
            return 1
        if keys[negative_key] and not keys[positive_key]:
            return -1
        return 0

    def step_towards(self, dt, dx, dy):
        # dx/dy should be -1, 0 or 1, one axis at a time please (Player1/Player2.update
        # already sort that out with vertical priority so nobody sneaks in diagonally)
        if dx == 0 and dy == 0:
            self._step_timer = 0.0
            return

        self._step_timer -= dt
        if self._step_timer > 0:
            return

        self.x = min(max(self.x + dx * self.size, 0), config.WIN_WIDTH - self.size)
        self.y = min(max(self.y + dy * self.size, 0), config.WIN_HEIGHT - self.size)
        self.rect.x = self.x
        self.rect.y = self.y
        self._step_timer = self.STEP_INTERVAL

# here comes the logic for P2: arrow keys to walk, hand tracking does the rest

from pyglet.window import key

import config
from entities.grid_actor import GridActor
from entities.projectile import Projectile
from input import gesture_tracking

PINCH_GLOW_TINT = (255, 255, 140)
NORMAL_TINT = (255, 255, 255)


class Player2(GridActor):

    def __init__(self, x, y, batch, group, collision_scale=None):
        super().__init__(x, y, "assets/player2", batch, group, collision_scale=collision_scale)

    def update(self, dt, keys, is_walkable=None):
        dy = self.axis_from_keys(keys, key.DOWN, key.UP)
        dx = 0 if dy != 0 else self.axis_from_keys(keys, key.LEFT, key.RIGHT)
        self.step_towards(dt, dx, dy, is_walkable)

        # no camera preview window open? no problem, sprite just glows while pinching
        self.color = PINCH_GLOW_TINT if gesture_tracking.is_pinching else NORMAL_TINT

    def try_interact_at(self, x, y, interactables, radius=64):
        # comes from the state's on_mouse_press with the real click/pinch spot,
        # hud gets first dibs on the click before we bother checking the world
        for interactable in interactables:
            if abs(x - interactable.x) <= radius and abs(y - interactable.y) <= radius:
                interactable.interact()
                return interactable
        return None

    def handle_key_press(self, symbol, gun):
        # P1 gets F/E via Player1.handle_key_press, P2 gets L here, two
        # separate dispatch points so the two players keys can never get
        # mixed up at the routing level
        if symbol == key.L:
            gun.toggle()

    def try_shoot(self, x, y, gun, batch, group):
        # free-aim: fires straight at wherever P2 clicked/pinched
        if not gun.active:
            return None

        return Projectile(
            self.x + self.size / 2,
            self.y + self.size / 2,
            x,
            y,
            gun.color,
            batch,
            group,
            owner="player2",
            speed=config.PLAYER_BULLET_SPEED,
        )

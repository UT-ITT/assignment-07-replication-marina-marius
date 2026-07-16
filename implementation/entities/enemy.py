# here comes all the enemy(enemies) logic and game mechanics
import random

import pyglet

import config
from entities.projectile import Projectile
from entities.shield import colors_match


class Enemy:
    # dummy rectangle that wanders around its spawn point and takes potshots
    # at whichever player is closer dies in one hit from a matching-color
    # bullet, otherwise just shrugs it off
    def __init__(self, x, y, batch, group):
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        self.size = config.ENEMY_HITBOX_SIZE[0]
        self.color = random.choice(config.SHIELD_COLORS)
        self.alive = True

        self._fire_timer = random.uniform(0, config.ENEMY_FIRE_INTERVAL)
        self._wander_target = self._pick_wander_target()

        self.rect = pyglet.shapes.Rectangle(
            x, y, self.size, self.size, color=self.color[:3], batch=batch, group=group,
        )

    def _pick_wander_target(self):
        radius = config.ENEMY_WANDER_RADIUS
        tx = self.spawn_x + random.uniform(-radius, radius)
        ty = self.spawn_y + random.uniform(-radius, radius)
        tx = min(max(tx, 0), config.WIN_WIDTH - self.size)
        ty = min(max(ty, 0), config.WIN_HEIGHT - self.size)
        return tx, ty

    def _wander(self, dt):
        tx, ty = self._wander_target
        dx, dy = tx - self.x, ty - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < 4:
            self._wander_target = self._pick_wander_target()
            return

        step = min(config.ENEMY_SPEED * dt, distance)
        self.x += dx / distance * step
        self.y += dy / distance * step
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, dt, targets, batch, group):
        # targets: list of (x, y) player positions to aim at. returns a
        # freshly fired Projectile when the cooldown lands, None otherwise
        if not self.alive:
            return None

        self._wander(dt)

        self._fire_timer -= dt
        if self._fire_timer > 0 or not targets:
            return None

        self._fire_timer = config.ENEMY_FIRE_INTERVAL
        target_x, target_y = min(
            targets, key=lambda t: (t[0] - self.x) ** 2 + (t[1] - self.y) ** 2
        )
        return Projectile(
            self.x + self.size / 2, self.y + self.size / 2,
            target_x, target_y, self.color, batch, group, owner="enemy",
        )

    def take_hit(self, color):
        if not self.alive or not colors_match(color, self.color):
            return False
        self.alive = False
        self.rect.delete()
        return True

# bullets: enemy ones and P2 ones, both fly in a straight line and
# completely ignore grid movement -> a bullet doesn't care whose turn it is
#
# sprites: assets/projectile/<color>/001-010.png. 001-005 is the looping
# in-flight animation, 006-010 is a one-shot explosion played on impact
# folder picked via shield.py color_folder(), same bucket index the
# shield/gate/gun already use for "which color is this"
import math

import pyglet

import config
from entities.shield import color_folder
from entities.sprite_anim import load_animation

FRAME_DURATION = 0.05
FLIGHT_FRAMES = tuple(range(1, 6))
EXPLOSION_FRAMES = tuple(range(6, 11))


def _flight_animation(folder):
    return load_animation(
        f"assets/projectile/{folder}", FLIGHT_FRAMES, FRAME_DURATION, loop=True
    )


def _explosion_animation(folder):
    return load_animation(
        f"assets/projectile/{folder}", EXPLOSION_FRAMES, FRAME_DURATION, loop=False
    )


def circle_rect_overlap(cx, cy, radius, rx, ry, size):
    # closest point on the (axis-aligned) rect to the circle center
    nearest_x = max(rx, min(cx, rx + size))
    nearest_y = max(ry, min(cy, ry + size))
    return (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2 <= radius**2


class Projectile:
    def __init__(
        self,
        x,
        y,
        target_x,
        target_y,
        color,
        batch,
        group,
        owner,
        speed,
        radius=config.BULLET_RADIUS,
    ):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.owner = owner  # "enemy" or "player2", decides what its allowed to hit
        self.alive = True  # still flying, still able to hit / be hit
        self.finished = (
            False  # explosion animation (if any) has played out, safe to drop
        )
        # pyglet fires on_animation_end every time a *looping* animation
        # wraps around too, not just once for a one-shot one (see
        # pyglet/sprite.py's _animate) - the in-flight animation loops the
        # whole time this bullet is alive, so without this flag
        # _on_explosion_end would fire (and delete the sprite) every lap of
        # the flight loop, not just when destroy() actually starts the
        # one-shot explosion animation
        self._exploding = False

        dx, dy = target_x - x, target_y - y
        distance = max(1.0, (dx**2 + dy**2) ** 0.5)
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed

        self._folder = color_folder(color)
        self.sprite = pyglet.sprite.Sprite(
            _flight_animation(self._folder),
            x=x,
            y=y,
            batch=batch,
            group=group,
        )
        self.sprite.scale = config.PROJECTILE_DISPLAY_SIZE / self.sprite.width
        self.sprite.push_handlers(on_animation_end=self._on_explosion_end)

        # art faces along +x (right) by default. pyglet's sprite.rotation is
        # clockwise degrees in this same y-up world space, so to make the
        # sprite's default-right tip point at (vx, vy) instead, negate the
        # standard (counter-clockwise) math angle atan2(vy, vx) - a bullet
        # never turns mid-flight, so this is set once and left alone
        self.sprite.rotation = -math.degrees(math.atan2(self.vy, self.vx))

    def update(self, dt):
        if not self.alive:
            return  # exploding or already gone, the animation drives itself now

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.sprite.x = self.x
        self.sprite.y = self.y

        if not (0 <= self.x <= config.WIN_WIDTH and 0 <= self.y <= config.WIN_HEIGHT):
            self.destroy(explode=False)  # off-screen, nobody's around to see it pop

    def hits_rect(self, x, y, size):
        return circle_rect_overlap(self.x, self.y, self.radius, x, y, size)

    def destroy(self, explode=True):
        if not self.alive:
            return
        self.alive = False
        if explode:
            self._exploding = True
            self.sprite.image = _explosion_animation(self._folder)
        else:
            self.finished = True
            self.sprite.delete()

    def _on_explosion_end(self):
        if not self._exploding:
            return  # the looping flight animation just lapped, not a real explosion
        self.finished = True
        self.sprite.delete()

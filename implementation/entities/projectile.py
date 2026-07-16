# bullets: enemy ones and P2 ones, both fly in a straight line and
# completely ignore grid movement -> a bullet doesn't care whose turn it is
import pyglet

import config


def circle_rect_overlap(cx, cy, radius, rx, ry, size):
    # closest point on the (axis-aligned) rect to the circle center
    nearest_x = max(rx, min(cx, rx + size))
    nearest_y = max(ry, min(cy, ry + size))
    return (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2 <= radius ** 2


class Projectile:
    def __init__(self, x, y, target_x, target_y, color, batch, group, owner,
                 speed=config.BULLET_SPEED, radius=config.BULLET_RADIUS):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.owner = owner  # "enemy" or "player2", decides what it's allowed to hit
        self.alive = True

        dx, dy = target_x - x, target_y - y
        distance = max(1.0, (dx ** 2 + dy ** 2) ** 0.5)
        self.vx = dx / distance * speed
        self.vy = dy / distance * speed

        self.shape = pyglet.shapes.Circle(
            x, y, radius, color=color[:3], batch=batch, group=group,
        )

    def update(self, dt):
        if not self.alive:
            return  # already destroyed this frame, don't touch a deleted shape

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.shape.x = self.x
        self.shape.y = self.y

        if not (0 <= self.x <= config.WIN_WIDTH and 0 <= self.y <= config.WIN_HEIGHT):
            self.alive = False

    def hits_rect(self, x, y, size):
        return circle_rect_overlap(self.x, self.y, self.radius, x, y, size)

    def destroy(self):
        self.alive = False
        self.shape.delete()

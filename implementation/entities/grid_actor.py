# P1 and P2 both need the same "walk exactly one tile, then wait" movement
# instead of sliding around (pokemon vibes), so instead of
# copy-pasting the stepping math into both player files it lives here once
#
# sprites: assets/<player1|player2>/<direction>_idle.png plus
# <direction>_walk1/2.png for direction in (down, up, left, right) idle is
# one still frame, walk is a 2-frame loop, "facing" is whichever direction
# was last actually pressed (held over after stopping, same as most top-down
# games you don't snap back to facing down the instant you let go of the key)
import pyglet

import config
from entities.sprite_anim import load_image

WALK_FRAME_DURATION = 0.15

# dx, dy (as step_towards already receives them) -> sprite folder direction name
DIRECTION_NAMES = {
    (0, -1): "down",
    (0, 1): "up",
    (-1, 0): "left",
    (1, 0): "right",
}

# folder -> {direction: {"idle": image, "walk": Animation}}, loaded once per
# folder and shared by every GridActor built from it (both players never
# need their own copy of the same four images)
_sprite_sets = {}


def _load_sprite_set(folder):
    if folder not in _sprite_sets:
        directions = {}
        for direction in ("down", "up", "left", "right"):
            idle = load_image(f"{folder}/{direction}_idle.png", anchor_center=False)
            walk1 = load_image(f"{folder}/{direction}_walk1.png", anchor_center=False)
            walk2 = load_image(f"{folder}/{direction}_walk2.png", anchor_center=False)
            directions[direction] = {
                "idle": idle,
                "walk": pyglet.image.Animation.from_image_sequence(
                    [walk1, walk2], WALK_FRAME_DURATION, loop=True
                ),
            }
        _sprite_sets[folder] = directions
    return _sprite_sets[folder]


class GridActor:

    # reuse PLAYER_SPEED so "tiles per second" from config.py still means
    # something even though nobody is sliding continuously anymore
    STEP_INTERVAL = config.TILE_SIZE / config.PLAYER_SPEED

    def __init__(self, x, y, sprite_folder, batch, group, size=config.TILE_SIZE, collision_scale=None):
        self.x = x
        self.y = y
        self.size = size
        self._step_timer = 0.0
        self.facing = (0, -1)  # facing down until the player first moves

        self._sprites = _load_sprite_set(sprite_folder)
        self._sprite_key = ("down", False)  # (direction, is_walking) currently showing

        idle_image = self._sprites["down"]["idle"]
        self.native_width = idle_image.width
        self.native_height = idle_image.height

        # tilemap collision (is_walkable) should test a box shaped like the
        # actual character, not the much bigger 64px movement tile a
        # GridActor built on a screen with a TileMap passes that map's own
        # scale here so "native sprite pixels" turns into "screen pixels" the
        # same way the map's own tiles were scaled, instead of guessing a
        # round number. no tilemap (dungeon/treasure chamber) -> no
        # collision_scale -> falls back to the full size x size box, which
        # is simply never used since those screens never pass is_walkable
        if collision_scale is None:
            self.collision_width = size
            self.collision_height = size
        else:
            self.collision_width = self.native_width * collision_scale
            self.collision_height = self.native_height * collision_scale

        self.sprite = pyglet.sprite.Sprite(
            idle_image, x=x, y=y, batch=batch, group=group,
        )
        # native art is small pixel-art (16x20) - stretch to fill the tile's
        # visual footprint exactly, same as the old plain-color rectangle had
        # (collision uses collision_width/height above instead, not this)
        self.sprite.width = size
        self.sprite.height = size

    @property
    def color(self):
        return self.sprite.color

    @color.setter
    def color(self, value):
        self.sprite.color = value

    @staticmethod
    def axis_from_keys(keys, negative_key, positive_key):
        # turns a key pair into -1/0/1 - mash both at once and they just cancel out
        if keys[positive_key] and not keys[negative_key]:
            return 1
        if keys[negative_key] and not keys[positive_key]:
            return -1
        return 0

    def step_towards(self, dt, dx, dy, is_walkable=None):
        # dx/dy should be -1, 0 or 1, one axis at a time please (Player1/Player2.update
        # already sort that out with vertical priority so nobody sneaks in diagonally)
        moving = dx != 0 or dy != 0
        if moving:
            self.facing = (dx, dy)
        self._set_animation(moving)

        if not moving:
            self._step_timer = 0.0
            return

        self._step_timer -= dt
        if self._step_timer > 0:
            return

        new_x = min(max(self.x + dx * self.size, 0), config.WIN_WIDTH - self.size)
        new_y = min(max(self.y + dy * self.size, 0), config.WIN_HEIGHT - self.size)
        # only screens with a walkable tilemap (currently just the overworld)
        # pass is_walkable - leaving it None elsewhere keeps the dungeon/
        # treasure chamber exactly as free-roaming as they've always been.
        # deliberately not resetting _step_timer on a blocked attempt: it's
        # already <=0 here, so bumping a wall re-checks every frame instead
        # of eating a wasted cooldown once the way actually clears
        if is_walkable is not None:

            check_x = new_x + (self.size - self.collision_width) / 2
            check_y = new_y + (self.size - self.collision_height) / 2
            if not is_walkable(check_x, check_y, self.collision_width, self.collision_height):
                return

        self.x, self.y = new_x, new_y
        self.sprite.x = self.x
        self.sprite.y = self.y
        self._step_timer = self.STEP_INTERVAL

    def _set_animation(self, moving):
        # walking plays the whole time a direction key is held (not just
        # during the grid-step cooldown) so the legs keep moving smoothly
        # between steps instead of freezing between each 64px hop
        key = (DIRECTION_NAMES[self.facing], moving)
        if key == self._sprite_key:
            return  # already showing this - reassigning would restart the walk loop
        self._sprite_key = key
        direction, is_walking = key
        frames = self._sprites[direction]
        self.sprite.image = frames["walk"] if is_walking else frames["idle"]

# here comes the tilemap/sprite logic
# why an own file? since we have 3 different maps
# overworld, dungeon, treasure chamber
# so here everything is set and the corresponding state screen file can get the tilemap batch they need
# keyowrds will be: overworld, dungeon and treasure

import pyglet
# loads a .tmx file painted in tiled and turns it into pyglet sprites in the given batch
from pytmx.util_pyglet import load_pyglet


class TileMap:

    def __init__(self, tmx_path, batch, group):
        self.data = load_pyglet(tmx_path)
        self.tile_width = self.data.tilewidth
        self.tile_height = self.data.tileheight
        self.width_tiles = self.data.width
        self.height_tiles = self.data.height

        # keep references around, otherwise pyglet garbage-collects the sprites
        self.sprites = []
        # each tile is unscaled (x, y) in pixels, so fit_to() can rescale later
        # without having to reload/rebuild anything
        self._native_positions = []

        # (tiled_x, tiled_y) Tiled's own row-from-top tile coords, same ones
        # layer.iter_data() already hands us - for every tile sitting on a
        # layer whose custom "blocks" property (set per-layer in Tiled, not
        # per tile way less tedious to tag by hand than every individual
        # tile graphic) is checked true
        self._blocked_tiles = set()

        # gid -> pyglet.image.Animation, built the first time that gid is
        # seen and shared by every other placed tile using it - a map can
        # easily place the same animated water/fire/trap tile hundreds of
        # times, one Animation object per gid beats one per placement
        self._animation_cache = {}

        for layer in self.data.visible_layers:
            if not hasattr(layer, "tiles"):
                continue  # skip object groups / image layers, only draw tile layers

            blocks = bool(getattr(layer, "properties", {}).get("blocks"))

            for x, y, gid in layer.iter_data():
                if not gid:
                    continue  # empty cell, nothing placed here on this layer

                if blocks:
                    self._blocked_tiles.add((x, y))

                # Tiled counts y from the top row down, pyglet counts y from
                # the bottom row up -> flip it here so the map isn't upside down
                px = x * self.tile_width
                py = (self.height_tiles - 1 - y) * self.tile_height
                sprite = pyglet.sprite.Sprite(
                    self._image_for_gid(gid), x=px, y=py, batch=batch, group=group
                )
                self.sprites.append(sprite)
                self._native_positions.append((px, py))

        # fit_to() fills these in is_walkable() needs them to translate an
        # on-screen position back into native tile space, they default to
        # "unscaled, no offset" so is_walkable() still works even if fit_to()
        # never gets called (e.g. a headless test building a TileMap directly).
        # scale is public, it's how a GridActor turns its own native sprite
        # size into a screen-space collision box that's actually sized like
        # the character instead of the (much bigger) movement-grid tile
        self.scale = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def _image_for_gid(self, gid):
        # most gids are a plain static tile - pytmx already resolved and
        # cached those images itself (self.data.images), nothing to build.
        # a gid with a Tiled "Tile Animation Editor" sequence attached
        # instead carries a "frames" property: a list of (gid, duration_ms)
        # pointing at other tiles in the same tileset to cycle through -
        # turn that into a real looping pyglet.image.Animation, once per gid
        if gid in self._animation_cache:
            return self._animation_cache[gid]

        properties = self.data.get_tile_properties_by_gid(gid)
        frames = properties.get("frames") if properties else None
        if not frames:
            return self.data.images[gid]

        # Tiled stores frame duration in milliseconds, pyglet wants seconds.
        # leaving every frame's duration a real number (never None) is what
        # makes a pyglet Animation loop forever instead of stopping on the
        # last frame - exactly what a background water/fire/trap tile wants
        animation = pyglet.image.Animation([
            pyglet.image.AnimationFrame(self.data.images[frame.gid], frame.duration / 1000)
            for frame in frames
        ])
        self._animation_cache[gid] = animation
        return animation

    def fit_to(self, target_width, target_height, center=True):

        native_width = self.width_tiles * self.tile_width
        native_height = self.height_tiles * self.tile_height
        scale = min(target_width / native_width, target_height / native_height)

        offset_x = (target_width - native_width * scale) / 2 if center else 0
        offset_y = (target_height - native_height * scale) / 2 if center else 0

        self.scale = scale
        self._offset_x = offset_x
        self._offset_y = offset_y

        for sprite, (native_x, native_y) in zip(self.sprites, self._native_positions):
            sprite.scale = scale
            sprite.x = offset_x + native_x * scale
            sprite.y = offset_y + native_y * scale

    def is_walkable(self, x, y, width, height):
        # x, y: bottom-left of the box being tested, width/height its size
        # all in the same on-screen pixel space fit_to() placed the map
        # sprites in. not required to be square: a GridActor checks a box
        # sized to its actual sprite (native pixels * this map's own scale),
        # not its much bigger 64px movement tile. players step in 64px jumps
        # but native tiles are 16px (times whatever fit_to() scaled them by)
        # a player box almost never lines up with a single tile, so this
        # checks every tile cell the whole box touches, not just one corner
        # (same "point checks miss things a real overlap wouldn't" lesson as
        # the gate walk-in bug)
        left = (x - self._offset_x) / self.scale
        bottom = (y - self._offset_y) / self.scale
        right = (x + width - self._offset_x) / self.scale
        top = (y + height - self._offset_y) / self.scale

        col_min = int(left // self.tile_width)
        col_max = int((right - 1) // self.tile_width)
        row_from_bottom_min = int(bottom // self.tile_height)
        row_from_bottom_max = int((top - 1) // self.tile_height)

        for col in range(col_min, col_max + 1):
            for row_from_bottom in range(row_from_bottom_min, row_from_bottom_max + 1):
                row = self.height_tiles - 1 - row_from_bottom
                if (col, row) in self._blocked_tiles:
                    return False
        return True
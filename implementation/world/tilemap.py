# here comes the tilemap/sprite logic
# why an own file? since we have 3 different maps
# overworld, dungeon, treasure chamber
# so here everything is set and the corresponding state screen file can get the tilemap batch they need
# keyowrds will be: overworld, dungeon and treasure

import pyglet
# loads a .tmx file painted in tiled and turns it into pyglet sprites in the given batch
from pytmx.util_pyglet import load_pyglet


class TileMap:

    def __init__(self, tmx_path, batch, group, wall_collision_shrink=1.0):
        # a blocked tile used to count as solid across its *entire* 16x16
        # cell fine for a tileset where the wall art actually fills the
        # tile, way too generous for one where the drawn wall is a much
        # thinner line/border within it (dungeon.tmx's walls_top/walls/
        # walls_back/walls_outside), which read as "the hallway is way
        # narrower than it looks". 1.0 keeps the old full-cell behavior
        # (overworld/treasure never asked for anything smaller), anything
        # below that insets the blocking rect within each tile, centered -
        # see is_walkable
        self.wall_collision_shrink = wall_collision_shrink
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

        self._blocked_tiles = set()

        # gid -> pyglet.image.Animation, built the first time that gis is seen
        self._animation_cache = {}

        layer_index = 0
        for layer in self.data.visible_layers:
            if not hasattr(layer, "tiles"):
                continue  # skip object groups / image layers, only draw tile layers

            blocks = bool(getattr(layer, "properties", {}).get("blocks"))
            layer_group = pyglet.graphics.Group(order=layer_index, parent=group)
            layer_index += 1

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
                    self._image_for_gid(gid), x=px, y=py, batch=batch, group=layer_group
                )
                self.sprites.append(sprite)
                self._native_positions.append((px, py))

        self.scale = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def _image_for_gid(self, gid):

        if gid in self._animation_cache:
            return self._animation_cache[gid]

        properties = self.data.get_tile_properties_by_gid(gid)
        frames = properties.get("frames") if properties else None
        if not frames:
            return self.data.images[gid]

        animation = pyglet.image.Animation(  # type: ignore
            [  
                pyglet.image.AnimationFrame(  # type: ignore
                    self.data.images[frame.gid], frame.duration / 1000
                )
                for frame in frames
            ]
        )
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

        left = (x - self._offset_x) / self.scale
        bottom = (y - self._offset_y) / self.scale
        right = (x + width - self._offset_x) / self.scale
        top = (y + height - self._offset_y) / self.scale

        col_min = int(left // self.tile_width)
        col_max = int((right - 1) // self.tile_width)
        row_from_bottom_min = int(bottom // self.tile_height)
        row_from_bottom_max = int((top - 1) // self.tile_height)

        margin_x = self.tile_width * (1 - self.wall_collision_shrink) / 2
        margin_y = self.tile_height * (1 - self.wall_collision_shrink) / 2
        shrunk_width = self.tile_width * self.wall_collision_shrink
        shrunk_height = self.tile_height * self.wall_collision_shrink

        for col in range(col_min, col_max + 1):
            for row_from_bottom in range(row_from_bottom_min, row_from_bottom_max + 1):
                row = self.height_tiles - 1 - row_from_bottom
                if (col, row) not in self._blocked_tiles:
                    continue
                tile_left = col * self.tile_width + margin_x
                tile_bottom = row_from_bottom * self.tile_height + margin_y
                tile_right = tile_left + shrunk_width
                tile_top = tile_bottom + shrunk_height
                if left < tile_right and right > tile_left and bottom < tile_top and top > tile_bottom:
                    return False
        return True

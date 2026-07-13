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

        for layer in self.data.visible_layers:
            if not hasattr(layer, "tiles"):
                continue  # skip object groups / image layers, only draw tile layers

            for x, y, image in layer.tiles():
                # TODO: animated tiles (water/fire/traps/doors etc.) aren't
                # handled yet! this only grabs each gid static first frame
                # Dungeon1.tmx alone has 425 <animation> tile defs, so this
                # will need reading the frame list per gid and driving it
                # with pyglet.clock instead of a single static Sprite image
                # unity could do that better *sigh*

                # Tiled counts y from the top row down, pyglet counts y from
                # the bottom row up -> flip it here so the map isn't upside down
                px = x * self.tile_width
                py = (self.height_tiles - 1 - y) * self.tile_height
                sprite = pyglet.sprite.Sprite(
                    image, x=px, y=py, batch=batch, group=group
                )
                self.sprites.append(sprite)

        # TODO: walkability/collision isn't handled yet
        # tag tiles missing with a custom property in Tiled (like "walkable") 
        # and read it via self.data.get_tile_properties_by_gid(gid) once movement needs it
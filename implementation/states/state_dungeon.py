import pyglet
from pyglet.window import key
import config

# Screen 2: Dungeon
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class DungeonState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.entity_group = pyglet.graphics.Group(order=1)
        self.ui_group = pyglet.graphics.Group(order=2)

        # TODO: replace with tilemap.py rendering of the dungeon layout
        self.background = pyglet.shapes.Rectangle(
            0, 0, config.WIN_WIDTH, config.WIN_HEIGHT,
            color=(30, 30, 40), batch=self.batch, group=self.bg_group,
        )

        # TODO: replace with shield.py (color/size/charge state)
        self.shield = pyglet.shapes.Circle(
            config.WIN_WIDTH // 2, config.WIN_HEIGHT // 2, 30,
            color=(200, 200, 200), batch=self.batch, group=self.entity_group,
        )

        # TODO: replace with enemy.py (projectile spawning + movement)
        self.enemy = pyglet.shapes.Rectangle(
            config.WIN_WIDTH - 150, config.WIN_HEIGHT // 2 - 25,
            50, 50, color=(160, 40, 40), batch=self.batch, group=self.entity_group,
        )

        self.hint_label = pyglet.text.Label(
            "placeholder dungeon - ENTER: clear it, O: die",
            x=20, y=config.WIN_HEIGHT - 30,
            anchor_x="left", anchor_y="center",
            font_size=14, color=config.TEXT_COLOR,
            batch=self.batch, group=self.ui_group,
        )

    def on_enter(self, **kwargs):
        pass

    def on_update(self, dt):
        # TODO: enemy projectile spawn/movement + shield collision checks
        pass

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        # TODO: replace with real "dungeon cleared" condition
        if symbol == key.ENTER:
            self.manager.set_state("treasure")
        # TODO: replace with real "player died" condition
        elif symbol == key.O:
            self.manager.set_state("end", won=False)

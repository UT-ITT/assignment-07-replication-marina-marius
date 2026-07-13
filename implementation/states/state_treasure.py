import pyglet
from pyglet.window import key
import config

# Screen 3: Treasure Chamber
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class TreasureState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.entity_group = pyglet.graphics.Group(order=1)
        self.ui_group = pyglet.graphics.Group(order=2)

        # TODO: replace with tilemap.py rendering of the treasure room layout
        self.background = pyglet.shapes.Rectangle(
            0, 0, config.WIN_WIDTH, config.WIN_HEIGHT,
            color=(50, 40, 20), batch=self.batch, group=self.bg_group,
        )

        # TODO: replace with interactable.py (blocks/levers puzzle objects)
        self.puzzle_object = pyglet.shapes.Rectangle(
            config.WIN_WIDTH // 2 - 25, config.WIN_HEIGHT // 2 - 25,
            50, 50, color=(180, 160, 60), batch=self.batch, group=self.entity_group,
        )

        self.hint_label = pyglet.text.Label(
            "placeholder puzzle: ENTER to simulate solving it since the developers were to lazy doing it directly",
            x=20, y=config.WIN_HEIGHT - 30,
            anchor_x="left", anchor_y="center",
            font_size=14, color=config.TEXT_COLOR,
            batch=self.batch, group=self.ui_group,
        )

    def on_enter(self, **kwargs):
        pass

    def on_update(self, dt):
        # TODO: puzzle-solved condition driven by P2 interactable logic
        pass

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.manager.set_state("end", won=True)

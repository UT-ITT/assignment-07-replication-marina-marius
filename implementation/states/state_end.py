import pyglet
from pyglet.window import key
import config

# Screen 4: Game Over/Game Won
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class EndState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.ui_group = pyglet.graphics.Group(order=1)

        self.title_label = pyglet.text.Label(
            "",
            x=config.WIN_WIDTH // 2, y=config.WIN_HEIGHT // 2 + 40,
            anchor_x="center", anchor_y="center",
            font_size=32, batch=self.batch, group=self.ui_group,
        )
        self.hint_label = pyglet.text.Label(
            "press ENTER to return to the start menu (actually we need here also an interaction technique so TODO)",
            x=config.WIN_WIDTH // 2, y=config.WIN_HEIGHT // 2 - 30,
            anchor_x="center", anchor_y="center",
            font_size=16, color=config.TEXT_COLOR,
            batch=self.batch, group=self.ui_group,
        )

    def on_enter(self, won=False, **kwargs):
        if won:
            self.title_label.text = "Such a great work wizardinos!"
            self.title_label.color = (80, 200, 100, 255)
        else:
            self.title_label.text = "Damn, didnt know we had losers as tutores *side eye*"
            self.title_label.color = (200, 60, 60, 255)

    def on_update(self, dt):
        pass

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.manager.set_state("start_menu")

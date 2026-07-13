import pyglet
from buttons import Button
import config

# Screen 0: Startmenu
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class StartMenuState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.ui_group = pyglet.graphics.Group(order=1)

        # TODO: swap for a real title image/logo
        self.title_label = pyglet.text.Label(
            "GAME TITLE",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT - 120,
            anchor_x="center",
            anchor_y="center",
            font_size=36,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.hint_label = pyglet.text.Label(
            # TODO: swap for a better catch phrase
            "P2: click/pinch the button below to continue",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT // 2 + 80,
            anchor_x="center",
            anchor_y="center",
            font_size=16,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.continue_button = Button(
            x=config.WIN_WIDTH // 2 - 100,
            y=config.WIN_HEIGHT // 2 - 40,
            width=200,
            height=60,
            text="Continue",
            batch=self.batch,
            group=self.ui_group,
        )

    def on_enter(self, **kwargs):
        self.continue_button.set_active(False)

    def on_update(self, dt):
        pass

    def on_draw(self):
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        # TODO: replace with P2 gesture cursor + pinch check once
        # gesture tracking is wired in and mouse click stands in for now
        if self.continue_button.hit_test(x, y):
            self.continue_button.set_active(True)
            self.manager.set_state("overworld")

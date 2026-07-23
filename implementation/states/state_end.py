import pyglet
from pyglet.window import key
from world import music
from world.buttons import Button
from world.tilemap import TileMap
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

        self.tilemap = TileMap(
            "assets/chamber/endscreen.tmx", self.batch, self.bg_group
        )
        self.tilemap.fit_to(config.WIN_WIDTH, config.WIN_HEIGHT)

        self.title_label = pyglet.text.Label(
            "",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT - 100,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=32,
            batch=self.batch,
            group=self.ui_group,
        )

        # TODO: swap for real end-game metrics UI once we have one
        self.stats_label = pyglet.text.Label(
            "",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT - 160,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=16,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.restart_button = Button(
            x=config.WIN_WIDTH // 2 - 100,
            y=120,
            width=200,
            height=60,
            text="Restart",
            batch=self.batch,
            group=self.ui_group,
        )

        self.hint_label = pyglet.text.Label(
            "P2: click/pinch Restart (or press ENTER) to head back to the start menu",
            x=config.WIN_WIDTH // 2,
            y=60,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=14,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self._duration = 0.0

    def on_enter(self, won=False, **kwargs):
        music.stop()

        # freeze the clock the moment we land here, don't keep ticking while
        # you're standing around reading your own score
        self._duration = self.manager.stats.elapsed()

        if won:
            self.title_label.text = "Such a great work wizardinos!"
            self.title_label.color = (80, 200, 100, 255)
            bullets = self.manager.stats.bullets_fired
            accuracy = self.manager.stats.accuracy() * 100
            self.stats_label.text = (
                f"time: {self._duration:.1f}s | bullets fired: {bullets} | "
                f"pitch accuracy: {accuracy:.0f}%"
            )
        else:
            self.title_label.text = (
                "Damn, didnt know we had losers as tutores *side eye*"
            )
            self.title_label.color = (200, 60, 60, 255)
            self.stats_label.text = f"time: {self._duration:.1f}s"

    def on_update(self, dt):
        pass

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            self.manager.set_state("start_menu")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.restart_button.hit_test(x, y):
            self.manager.set_state("start_menu")

import random

import pyglet
from world.buttons import Button
from world.hud import PitchLegend
from world.tilemap import TileMap
import config
from entities.shield import colors_match, frequency_to_color
from input import audio_input
from world.gate import LOCK_HOLD_TIME, COLOR_TOLERANCE

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
        
        self.tilemap = TileMap(
            "assets/chamber/startscreen.tmx", self.batch, self.bg_group
        )
        self.tilemap.fit_to(config.WIN_WIDTH, config.WIN_HEIGHT)

        # TODO: swap for a real title image/logo
        self.title_label = pyglet.text.Label(
            "WHOAMONIZE",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT - 120,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=36,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        # TODO: swap this for final rules once we agree what they are
        self.rules_label = pyglet.text.Label(
            "P1 sings to match colors, P2 points and "
            "clicks/pinches things, and together you'll talk your way through gates, "
            "block some bullets, and hopefully not embarrass yourselves too badly.",
            x=config.WIN_WIDTH // 2,
            y=config.WIN_HEIGHT - 200,
            width=700,
            multiline=True,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=14,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.hint_label = pyglet.text.Label(
            "P2: click/pinch the button below to wake it up",
            x=config.WIN_WIDTH // 2,
            y=200,
            anchor_x="center",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=16,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.continue_button = Button(
            x=config.WIN_WIDTH // 2 - 100,
            y=100,
            width=200,
            height=60,
            text="Start",
            batch=self.batch,
            group=self.ui_group,
        )

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH // 2 - 61, 40,
            self.batch, self.ui_group,
        )

        self.phase = "idle"  # idle -> listening -> locked
        self.target_color = None
        self._match_timer = 0.0

    def on_enter(self, **kwargs):
        self.phase = "idle"
        self.target_color = None
        self._match_timer = 0.0
        self.continue_button.set_active(False)
        self.continue_button.label.text = "Start"
        self.hint_label.text = "P2: click/pinch the button below to wake it up"

    def on_update(self, dt):
        if self.phase != "listening":
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.continue_button.rect.color = config.PITCH_SILENCE_COLOR
            return

        color = frequency_to_color(frequency)
        self.continue_button.rect.color = color[:3]

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        self.manager.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock()
        else:
            self._match_timer = 0.0

    def _lock(self):
        self.phase = "locked"
        self.continue_button.rect.color = self.target_color[:3] # type: ignore
        self.continue_button.label.text = "Continue"
        self.hint_label.text = "P2: click/pinch it again to head into the world"

    def on_draw(self):
        self.batch.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.continue_button.hit_test(x, y):
            return

        if self.phase == "idle":
            self.phase = "listening"
            self.target_color = random.choice(config.SHIELD_COLORS)
            self._match_timer = 0.0
            color_name = config.SHIELD_COLOR_NAMES[config.SHIELD_COLORS.index(self.target_color)]
            self.hint_label.text = f"P1: sing {color_name.upper()} to match the button! (see the legend below)"
        elif self.phase == "locked":
            self.manager.stats.start_run()
            self.manager.set_state("overworld")

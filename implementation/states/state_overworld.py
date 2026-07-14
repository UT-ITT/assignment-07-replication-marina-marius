import pyglet
from pyglet.window import key
import config
from input import audio_input
from entities import player_singer

# Screen 1: World
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class OverworldState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.entity_group = pyglet.graphics.Group(order=1)
        self.ui_group = pyglet.graphics.Group(order=2)

        # TODO: replace with tilemap.py rendering of the overworld layout
        self.background = pyglet.shapes.Rectangle(
            0, 0, config.WIN_WIDTH, config.WIN_HEIGHT,
            color=(40, 60, 40), batch=self.batch, group=self.bg_group,
        )

        # TODO: replace with player_singer.py / player_gesture.py sprites
        self.player1 = pyglet.shapes.Rectangle(
            200, 200, config.TILE_SIZE, config.TILE_SIZE,
            color=config.P1_COLOR[:3], batch=self.batch, group=self.entity_group,
        )
        self.player2 = pyglet.shapes.Rectangle(
            260, 200, config.TILE_SIZE, config.TILE_SIZE,
            color=config.P2_COLOR[:3], batch=self.batch, group=self.entity_group,
        )

        # TODO: replace with gate.py (color-match gate) logic
        self.gate = pyglet.shapes.Rectangle(
            config.WIN_WIDTH - 150, config.WIN_HEIGHT // 2 - 50,
            80, 100, color=player_singer.pitch_to_color(500), batch=self.batch, group=self.entity_group,
        )
        self.gate_target_color = tuple(self.gate.color)
        self.gate_open = False
        self.gate_match_start = None
        self.current_sung_color = self.player1.color

        self.hint_label = pyglet.text.Label(
            # TODO: dummy logic for nwo
            "WASD: P1 | Arrow keys: P2 | Sing the gate color near the gate, ENTER to enter",
            x=20,
            y=config.WIN_HEIGHT - 30,
            anchor_x="left",
            anchor_y="center",
            font_size=14,
            color=config.TEXT_COLOR,
            batch=self.batch,
            group=self.ui_group,
        )

        self.keys = key.KeyStateHandler()

    def on_enter(self, **kwargs):
        self.gate_open = False
        self.gate_match_start = None
        self.gate.color = self.gate_target_color
        self.manager.window.push_handlers(self.keys)

    def on_exit(self):
        self.manager.window.remove_handlers(self.keys)

    def on_update(self, dt):
        speed = 150 * dt
        if self.keys[key.W]:
            self.player1.y += speed
        if self.keys[key.S]:
            self.player1.y -= speed
        if self.keys[key.A]:
            self.player1.x -= speed
        if self.keys[key.D]:
            self.player1.x += speed

        if self.keys[key.UP]:
            self.player2.y += speed
        if self.keys[key.DOWN]:
            self.player2.y -= speed
        if self.keys[key.LEFT]:
            self.player2.x -= speed
        if self.keys[key.RIGHT]:
            self.player2.x += speed

        if audio_input.current_frequency > 0.0:
            self.current_sung_color = player_singer.pitch_to_color(audio_input.current_frequency)

        self.player1.color = self.current_sung_color

        if self._near_gate(self.player1) and self._colors_match(self.player1.color, self.gate_target_color):
            if self.gate_match_start is None:
                self.gate_match_start = 0.0
            self.gate_match_start += dt
            if self.gate_match_start >= 2.0:
                self.gate_open = True
                self.gate.color = (60, 180, 90)
        else:
            self.gate_match_start = None

    def _near_gate(self, player):
        return abs(player.x - self.gate.x) < 80 and abs(player.y - self.gate.y) < 80

    def _colors_match(self, player_color, gate_color, tolerance=35):
        return all(abs(player_color[index] - gate_color[index]) <= tolerance for index in range(3))

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER and self.gate_open:
            self.manager.set_state("dungeon")

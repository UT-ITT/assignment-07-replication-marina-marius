import pyglet
from pyglet.window import key
import config
from entities.player_singer import Player1
from entities.player_gesture import Player2
from world.gate import Gate
from world.hud import PitchLegend
from world.interactable import Pushable

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

        # overworld has no shield (that's a dungeon thing), so F is just a shrug here
        self.player1 = Player1(200, 200, self.batch, self.entity_group)
        self.player2 = Player2(260, 200, self.batch, self.entity_group)

        # mechanic B: P2 grabs it and drags it around, no strings attached
        self.crystal = Pushable(
            200, config.WIN_HEIGHT - 200, 40, self.batch, self.entity_group,
        )

        # mechanic A: P2 wakes it up, P1 sings its color to unlock it and
        # unlocking it *is* opening it, straight into the dungeon
        self.gate = Gate(
            config.WIN_WIDTH - 150, config.WIN_HEIGHT // 2 - 50, 80,
            self.batch, self.entity_group, on_unlock=self._enter_dungeon,
            stats=self.manager.stats,
        )

        self.interactables = (self.crystal, self.gate)

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH - 160, config.WIN_HEIGHT - 70,
            self.batch, self.ui_group,
        )

        self.hint_label = pyglet.text.Label(
            "P1 (WASD): sings to unlock the gate | "
            "P2 (Arrows + click/pinch): drags the crystal, wakes the gate up",
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
        self.manager.window.push_handlers(self.keys)

    def on_exit(self):
        self.manager.window.remove_handlers(self.keys)

    def _enter_dungeon(self):
        self.manager.set_state("dungeon")

    def on_update(self, dt):
        self.player1.update(dt, self.keys)
        self.player2.update(dt, self.keys)
        self.gate.update(dt)

        for interactable in self.interactables:
            near = (
                interactable.in_range(self.player1.x, self.player1.y)
                or interactable.in_range(self.player2.x, self.player2.y)
            )
            interactable.show_hint(near)

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        self.player1.handle_key_press(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.gate.on_mouse_press(x, y):
            return
        self.crystal.on_mouse_press(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.crystal.on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        self.crystal.on_mouse_release()

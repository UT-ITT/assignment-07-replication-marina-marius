import pyglet
from pyglet.window import key
import config
from entities.player_singer import Player1
from entities.player_gesture import Player2
from world.chest import Chest
from world.hud import PitchLegend

# Screen 3: Treasure Chamber
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

DIAMOND_DISPLAY_TIME = 10.0


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

        self.player1 = Player1(200, 120, self.batch, self.entity_group)
        self.player2 = Player2(260, 120, self.batch, self.entity_group)

        # 3 chests, solved strictly in order, each needs P1 color and then
        # a P2 drag onto its marked slot, chest N+1 only wakes up once N is solved
        slot_positions = [
            (config.WIN_WIDTH // 2 - 220, 200),
            (config.WIN_WIDTH // 2 - 20, 200),
            (config.WIN_WIDTH // 2 + 180, 200),
        ]
        spawn_positions = [
            (config.WIN_WIDTH // 2 - 220, 420),
            (config.WIN_WIDTH // 2 - 20, 420),
            (config.WIN_WIDTH // 2 + 180, 420),
        ]
        colors = config.SHIELD_COLORS[:3]

        self.chests = [
            Chest(
                spawn_positions[i][0], spawn_positions[i][1], 50,
                colors[i], slot_positions[i], self.batch, self.entity_group,
                on_solved=self._advance, stats=self.manager.stats,
            )
            for i in range(3)
        ]
        self.progress = 0
        self.chests[0].activate()

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH - 160, config.WIN_HEIGHT - 70,
            self.batch, self.ui_group,
        )

        self.diamond = None
        self.diamond_timer = 0.0
        self.solved_all = False

        self.hint_label = pyglet.text.Label(
            "P2: click/pinch the glowing chest to wake it | P1: sing it its color, "
            "then P2: drag it onto its marked spot - solve chests in order",
            x=20, y=config.WIN_HEIGHT - 30,
            anchor_x="left", anchor_y="center",
            font_size=14, color=config.TEXT_COLOR,
            batch=self.batch, group=self.ui_group,
        )

        self.keys = key.KeyStateHandler()

    def on_enter(self, **kwargs):
        self.manager.window.push_handlers(self.keys)

    def on_exit(self):
        self.manager.window.remove_handlers(self.keys)

    def _advance(self):
        self.progress += 1
        if self.progress < len(self.chests):
            self.chests[self.progress].activate()
        else:
            self._all_solved()

    def _all_solved(self):
        self.solved_all = True
        for chest in self.chests:
            chest.rect.visible = False
            chest.slot_marker.visible = False
            chest.hint_label.visible = False

        # TODO: replace with an actual diamond sprite once art exists
        self.diamond = pyglet.shapes.Circle(
            config.WIN_WIDTH // 2, config.WIN_HEIGHT // 2, 100,
            color=(230, 200, 60), batch=self.batch, group=self.entity_group,
        )
        self.diamond_timer = DIAMOND_DISPLAY_TIME
        self.hint_label.text = "you found it! heading back to celebrate soon..."

    def on_update(self, dt):
        self.player1.update(dt, self.keys)
        self.player2.update(dt, self.keys)

        if self.solved_all:
            self.diamond_timer -= dt
            if self.diamond_timer <= 0:
                self.manager.set_state("end", won=True)
            return

        active_chest = self.chests[self.progress]
        active_chest.update(dt)
        near = (
            active_chest.in_range(self.player1.x, self.player1.y)
            or active_chest.in_range(self.player2.x, self.player2.y)
        )
        active_chest.show_hint(near)

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        # TODO: replace with real "puzzle failed" condition if we ever add one
        if symbol == key.ENTER:
            self.manager.set_state("end", won=True)
        else:
            self.player1.handle_key_press(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.solved_all:
            return
        self.chests[self.progress].on_mouse_press(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.solved_all:
            return
        self.chests[self.progress].on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.solved_all:
            return
        self.chests[self.progress].on_mouse_release()

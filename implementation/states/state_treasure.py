import pyglet
from pyglet.window import key
import config
from entities.player_singer import Player1
from entities.player_gesture import Player2
from world.chest import Chest, SkullChest
from world.gem import Gem
from world.hud import PitchLegend

# Screen 3: Treasure Chamber
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

SOLVED_WAIT_TIME = 3.0  # pause on the 3 solved chests before they give way to the skull chest
REVEAL_DISPLAY_TIME = 10.0  # how long the locked, revealed gem sits there before heading to the end screen


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

        self.phase = "chests"  # chests -> waiting -> skull -> gem -> reveal
        self._wait_timer = 0.0
        self.skull_chest = None
        self.gem = None
        self.reveal_timer = 0.0

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
            # all 3 solved - sit on that for a beat before the room reacts
            self.phase = "waiting"
            self._wait_timer = SOLVED_WAIT_TIME
            self.hint_label.text = "all three chests are glowing... something's happening"

    def _spawn_skull(self):
        self.phase = "skull"
        for chest in self.chests:
            chest.delete()

        # dead center of the row the 3 chest slots sat on
        first_slot, last_slot = self.chests[0].target_slot, self.chests[-1].target_slot
        skull_x = (first_slot[0] + last_slot[0]) / 2 + 25
        skull_y = first_slot[1] + 25
        self.skull_chest = SkullChest(
            skull_x, skull_y, 50, self.batch, self.entity_group, on_open=self._spawn_gem,
        )
        self.hint_label.text = "the chest is opening..."

    def _spawn_gem(self):
        self.phase = "gem"
        self.gem = Gem(
            self.skull_chest.sprite.x, self.skull_chest.sprite.y, 50,
            self.batch, self.entity_group,
            on_locked=self._gem_locked, stats=self.manager.stats,
        )
        self.hint_label.text = "P2: click the gem to wake it | P1: sing its color and hold it"

    def _gem_locked(self):
        self.phase = "reveal"
        self.reveal_timer = REVEAL_DISPLAY_TIME
        self.hint_label.text = "you found it! heading back to celebrate soon..."

    def on_update(self, dt):
        self.player1.update(dt, self.keys)
        self.player2.update(dt, self.keys)

        if self.phase == "chests":
            active_chest = self.chests[self.progress]
            active_chest.update(dt)
            near = (
                active_chest.in_range(self.player1.x, self.player1.y)
                or active_chest.in_range(self.player2.x, self.player2.y)
            )
            active_chest.show_hint(near)
        elif self.phase == "waiting":
            self._wait_timer -= dt
            if self._wait_timer <= 0:
                self._spawn_skull()
        elif self.phase == "gem":
            self.gem.update(dt)
        elif self.phase == "reveal":
            self.reveal_timer -= dt
            if self.reveal_timer <= 0:
                self.manager.set_state("end", won=True)
        # phase == "skull": nothing to tick here, the sprite's own animation
        # clock drives it and _spawn_gem fires via the on_open callback

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        # TODO: replace with real "puzzle failed" condition if we ever add one
        if symbol == key.ENTER:
            self.manager.set_state("end", won=True)
        else:
            self.player1.handle_key_press(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.phase == "chests":
            self.chests[self.progress].on_mouse_press(x, y)
        elif self.phase == "gem":
            self.gem.on_mouse_press(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.phase != "chests":
            return
        self.chests[self.progress].on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.phase != "chests":
            return
        self.chests[self.progress].on_mouse_release()

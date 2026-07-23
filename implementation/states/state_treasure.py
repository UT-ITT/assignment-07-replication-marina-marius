import random

import pyglet
from pyglet.window import key
import config
from entities.player_singer import Player1
from entities.player_gesture import Player2
from world.chest import Chest, SkullChest
from world.gem import Gem
from world.hud import PitchLegend
from world.tilemap import TileMap

# Screen 3: Treasure Chamber
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

SOLVED_WAIT_TIME = (
    3.0  # pause on the 3 solved chests before they give way to the skull chest
)
REVEAL_DISPLAY_TIME = (
    7.0  # how long the locked, revealed gem sits there before heading to the end screen
)


class TreasureState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.entity_group = pyglet.graphics.Group(order=1)
        self.ui_group = pyglet.graphics.Group(order=2)

        self.tilemap = TileMap("assets/chamber/treasure.tmx", self.batch, self.bg_group)
        self.tilemap.fit_to(config.WIN_WIDTH, config.WIN_HEIGHT)

        self.player1 = Player1(
            595,
            59,
            self.batch,
            self.entity_group,
            collision_scale=self.tilemap.scale,
        )
        self.player2 = Player2(
            646,
            59,
            self.batch,
            self.entity_group,
            collision_scale=self.tilemap.scale,
        )

        self._slot_positions = [
            (449, 92),
            (628, 92),
            (807, 92),
        ]
        spawn_positions = [
            (65, 425),
            (193, 245),
            (1140, 348),
        ]

        self._scatter_positions = [
            (39, 450),
            (116, 322),
            (218, 194),
            (1063, 425),
            (1165, 297),
            (1217, 169),
        ]

        colors = [random.choice(config.SHIELD_COLORS) for _ in range(3)]
        shuffled_slots = random.sample(self._slot_positions, len(self._slot_positions))

        self.chests = [
            Chest(
                spawn_positions[i][0],
                spawn_positions[i][1],
                50,
                colors[i],
                shuffled_slots[i],
                self.batch,
                self.entity_group,
                on_placed=self._on_chest_placed,
                stats=self.manager.stats,
                slots_provider=self._free_slots,
            )
            for i in range(3)
        ]

        self.pending = list(range(len(self.chests)))
        self.progress = 0
        self.chests[self.pending[0]].activate()

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH - 160,
            config.WIN_HEIGHT - 70,
            self.batch,
            self.ui_group,
        )

        self.phase = "chests"  # chests -> waiting -> skull -> gem -> reveal
        self._wait_timer = 0.0
        self.skull_chest = None
        self.gem = None
        self.reveal_timer = 0.0

        # tracks where a held pinch/mouse button currently is
        # a chest canlock its color while that same press is still down
        self._pointer_down_at = None

        self.hint_label = pyglet.text.Label(
            "P2: click/pinch the glowing chest to wake it | P1: sing it its color, "
            "then P2: drag it onto its marked spot - solve chests in order",
            x=20,
            y=config.WIN_HEIGHT - 30,
            anchor_x="left",
            anchor_y="center",
            font_name=config.FONT_NAME,
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

    def _free_slots(self):
        taken = {
            chest.current_slot
            for chest in self.chests
            if chest.current_slot is not None
        }
        return [slot for slot in self._slot_positions if slot not in taken]

    def _on_chest_placed(self, chest):
        # fires the instant any chest snaps into a slot, right or wrong
        # this chest doesn't get its own verdict, only the round does, once
        # every chest still pending this round has been placed *somewhere*
        self.progress += 1
        if self.progress < len(self.pending):
            self.chests[self.pending[self.progress]].activate()
            return
        self._check_round()

    def _check_round(self):
        # every chest that placed correctly this round locks in for good
        # and drops out of rotation, only the ones still wrong come back
        # around for another attempt
        still_wrong = []
        for index in self.pending:
            chest = self.chests[index]
            if chest.current_slot == chest.target_slot:
                chest.lock_in()
            else:
                still_wrong.append(index)

        if not still_wrong:
            self._all_correct()
            return

        self.hint_label.text = (
            "close, but not quite - the wrong ones scatter, try again!"
        )
        new_spots = random.sample(self._scatter_positions, len(still_wrong))
        for index, spot in zip(still_wrong, new_spots):
            self.chests[index].scatter(*spot)

        self.pending = still_wrong
        self.progress = 0
        self.chests[self.pending[0]].activate()

    def _all_correct(self):
        # sit on that for a beat before the room reacts
        self.phase = "waiting"
        self._wait_timer = SOLVED_WAIT_TIME
        self.hint_label.text = "all three chests are glowing... something's happening"

    def _spawn_skull(self):
        self.phase = "skull"
        for chest in self.chests:
            chest.delete()

        slot_xs = [chest.target_slot[0] for chest in self.chests]
        skull_x = (min(slot_xs) + max(slot_xs)) / 2 + 25
        skull_y = self.chests[0].target_slot[1] + 25
        self.skull_chest = SkullChest(
            skull_x,
            skull_y,
            50,
            self.batch,
            self.entity_group,
            on_open=self._spawn_gem,
        )
        self.hint_label.text = "the chest is opening..."

    def _spawn_gem(self):
        self.phase = "gem"
        self.gem = Gem(
            self.skull_chest.sprite.x,  # type: ignore
            self.skull_chest.sprite.y,  # type: ignore
            50,  # type: ignore
            self.batch,
            self.entity_group,
            on_solved=self._gem_locked,
            stats=self.manager.stats,
        )
        self.hint_label.text = (
            "P2: click the gem to wake it | P1: sing its color and hold it"
        )

    def _gem_locked(self):
        self.phase = "reveal"
        self.reveal_timer = REVEAL_DISPLAY_TIME
        self.hint_label.text = "you found it! heading back to celebrate soon..."

    def on_update(self, dt):
        self.player1.update(dt, self.keys, self.tilemap.is_walkable)
        self.player2.update(dt, self.keys, self.tilemap.is_walkable)

        if self.phase == "chests":
            active_chest = self.chests[self.pending[self.progress]]
            active_chest.update(dt)
            if self._pointer_down_at is not None:
                active_chest.note_still_pressed(*self._pointer_down_at)
            near = active_chest.in_range(
                self.player1.x, self.player1.y
            ) or active_chest.in_range(self.player2.x, self.player2.y)
            active_chest.show_hint(near)
        elif self.phase == "waiting":
            self._wait_timer -= dt
            if self._wait_timer <= 0:
                self._spawn_skull()
        elif self.phase == "gem":
            self.gem.update(dt)  # type: ignore
            near = self.gem.in_range(  # type: ignore
                self.player1.x, self.player1.y
            ) or self.gem.in_range(  # type: ignore
                self.player2.x, self.player2.y
            )  # type: ignore
            self.gem.show_hint(near)  # type: ignore
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
        self._pointer_down_at = (x, y)
        if self.phase == "chests":
            self.chests[self.pending[self.progress]].on_mouse_press(x, y)
        elif self.phase == "gem":
            self.gem.on_mouse_press(x, y)  # type: ignore

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self._pointer_down_at = (x, y)
        if self.phase != "chests":
            return
        self.chests[self.pending[self.progress]].on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        self._pointer_down_at = None
        if self.phase != "chests":
            return
        self.chests[self.pending[self.progress]].on_mouse_release()

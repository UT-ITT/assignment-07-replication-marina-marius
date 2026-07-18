import pyglet
from pyglet.window import key
import config
from entities.player_singer import Player1
from entities.player_gesture import Player2
from world.gate import Gate
from world.gem import Gem
from world.hud import PitchLegend

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

        # mechanic B: 4 gems, one per color P1 sings each one its color,
        # P2 drags it onto its matching marked slot near the gate. all 4
        # solved before the gate can even be clicked, see on_mouse_press
        gem_colors = config.SHIELD_COLORS
        gem_slot_positions = [
            (config.WIN_WIDTH - 280, 180),
            (config.WIN_WIDTH - 280, 320),
            (config.WIN_WIDTH - 280, 460),
            (config.WIN_WIDTH - 280, 600),
        ]
        gem_spawn_positions = [
            (200, 500), (400, 500), (600, 500), (800, 500),
        ]
        self.gems = [
            Gem(
                gem_spawn_positions[i][0], gem_spawn_positions[i][1], 50,
                self.batch, self.entity_group,
                target_color=gem_colors[i], target_slot=gem_slot_positions[i],
                stats=self.manager.stats,
            )
            for i in range(4)
        ]
        self._gems_done_notified = False

        # mechanic A: P1 sings its color to unlock it, then both walk in
        # but it can't even be woken up until all 4 gems are in place
        self.gate = Gate(
            config.WIN_WIDTH - 150, config.WIN_HEIGHT // 2 - 50, 80,
            self.batch, self.entity_group, on_unlock=self._enter_dungeon,
            stats=self.manager.stats,
        )

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH - 160, config.WIN_HEIGHT - 70,
            self.batch, self.ui_group,
        )

        self.hint_label = pyglet.text.Label(
            "P1: sing each gem its color | P2: drag it onto its matching slot - "
            "solve all 4 to wake the gate",
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

        for gem in self.gems:
            gem.update(dt)
            near = (
                gem.in_range(self.player1.x, self.player1.y)
                or gem.in_range(self.player2.x, self.player2.y)
            )
            gem.show_hint(near)

        gems_done = all(gem.solved for gem in self.gems)
        if gems_done and not self._gems_done_notified:
            self._gems_done_notified = True
            self.hint_label.text = "P2: click/pinch the gate to wake it | P1: sing its color to unlock it"

        gate_near = (
            self.gate.in_range(self.player1.x, self.player1.y)
            or self.gate.in_range(self.player2.x, self.player2.y)
        )
        self.gate.show_hint(gems_done and gate_near)

        # gate unlocked color alone doesn't open it anymore, both P1 and
        # P2 have to physically walk in, whoevers first just disappears
        # until the other catches up (see Gate.try_enter)
        if self.gate.try_enter(self.player1, self.player1.x, self.player1.y):
            self.player1.sprite.visible = False
        if self.gate.try_enter(self.player2, self.player2.x, self.player2.y):
            self.player2.sprite.visible = False

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        self.player1.handle_key_press(symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        print(f"[pyglet] on_mouse_press at ({x}, {y})")
        for gem in self.gems:
            if gem.on_mouse_press(x, y):
                return
        if all(gem.solved for gem in self.gems) and self.gate.on_mouse_press(x, y):
            return

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        print(f"[pyglet] on_mouse_drag at ({x}, {y}) delta=({dx}, {dy})")
        for gem in self.gems:
            gem.on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        print(f"[pyglet] on_mouse_release at ({x}, {y})")
        for gem in self.gems:
            gem.on_mouse_release()

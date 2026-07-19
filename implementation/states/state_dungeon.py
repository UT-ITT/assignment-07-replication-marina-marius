import random

import pyglet
from pyglet.window import key
import config
from world import music
from world.tilemap import TileMap
from world.hud import ShieldHud, GunHud, HeartsDisplay, PitchLegend
from world.interactable import Interactable
from world.gate import Gate
from world.gem import Gem
from entities.shield import Shield
from entities.gun import Gun
from entities.player_singer import Player1
from entities.player_gesture import Player2
from entities.enemy import Enemy

# Screen 2: Dungeon
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class DungeonState:

    def __init__(self, manager):
        self.manager = manager
        self.batch = pyglet.graphics.Batch()
        self.bg_group = pyglet.graphics.Group(order=0)
        self.entity_group = pyglet.graphics.Group(order=1)
        self.ui_group = pyglet.graphics.Group(order=2)

        self.tilemap = TileMap(
            "assets/chamber/dungeon.tmx", self.batch, self.bg_group
        )
        self.tilemap.fit_to(config.WIN_WIDTH, config.WIN_HEIGHT)

        # invisible until P1 actually raises it with F - see Shield.activate
        self.shield = Shield(self.batch, self.entity_group)
        self.shield_hud = ShieldHud(self.shield, self.batch, self.ui_group)

        self.gun = Gun()
        self.gun_hud = GunHud(self.gun, self.batch, self.ui_group, x=20, y=30)

        # far-left edge of the map, on its vertical midline - the
        # gem/exit-gate/eventual diamond all sit on the opposite (right)
        # side, so this is the natural "start" end of the room. (40, 360)/
        # (104, 360) confirmed walkable against the real "blocks" tiles,
        # not guessed - the old (200, 120)/(260, 120) spawn had player1
        # sitting directly on a walls tile
        self.player1 = Player1(
            40, 360, self.batch, self.entity_group, shield=self.shield,
            collision_scale=self.tilemap.scale,
        )
        self.player2 = Player2(
            104, 360, self.batch, self.entity_group, collision_scale=self.tilemap.scale
        )

        self.hearts1 = HeartsDisplay(20, config.WIN_HEIGHT - 60, self.batch, self.ui_group)
        self.hearts2 = HeartsDisplay(20, config.WIN_HEIGHT - 90, self.batch, self.ui_group)

        # a lever that does nothing except prove E and pinch-click both work.
        # nudged onto walkable ground once dungeon.tmx's "blocks" layers
        # landed - the round-number placeholder used to sit inside a wall
        self.lever = Interactable(
            212, 448, 40, self.batch, self.entity_group,
        )

        # a couple of static blocks bullets can crash into instead of
        # reaching their target - also nudged off the walls onto the open
        # floor, same reason as the lever above
        obstacle_positions = [(620, 136), (596, 392)]
        self.obstacles = [
            pyglet.shapes.Rectangle(
                x, y, config.OBSTACLE_SIZE, config.OBSTACLE_SIZE,
                color=(90, 80, 70), batch=self.batch, group=self.entity_group,
            )
            for x, y in obstacle_positions
        ]

        # cheat sheet so P1 knows roughly what to sing instead of guessing
        self.pitch_legend = PitchLegend(
            config.WIN_WIDTH - 160, config.WIN_HEIGHT - 70,
            self.batch, self.ui_group,
        )

        self.enemies = []
        self.bullets = []
        self.gate = None
        self.phase = "puzzle"  # puzzle -> combat -> cleared

        self.hint_label = pyglet.text.Label(
            "P2: click/pinch the gem to wake it | P1: sing it its color to start the fight",
            x=20, y=config.WIN_HEIGHT - 30,
            anchor_x="left", anchor_y="center",
            font_name=config.FONT_NAME, font_size=14, color=config.TEXT_COLOR,
            batch=self.batch, group=self.ui_group,
        )

        self.keys = key.KeyStateHandler()

        # the fight starter isn't a door - no target_slot means coloring it
        # alone is the whole trigger, on_solved fires the instant it locks
        self.gem = Gem(
            config.WIN_WIDTH - 110, config.WIN_HEIGHT // 2, 64,
            self.batch, self.entity_group, on_solved=self._start_combat,
            stats=self.manager.stats,
        )

    def _spawn_gate(self, on_unlock, melody=False):
        # the exit gate only - idea.md's "final gate", so it gets a sung
        # melody (see world/gate.py) instead of one held pitch, and (the
        # default) walk_in_required=True since it's an actual door out
        self.gate = Gate(
            config.WIN_WIDTH - 150, config.WIN_HEIGHT // 2 - 40, 80,
            self.batch, self.entity_group, on_unlock=on_unlock,
            melody=melody, stats=self.manager.stats,
        )

    def _start_combat(self):
        self.phase = "combat"
        self.gate = None
        # one enemy per color now, not a random headcount - each bat only
        # ever fires bullets in its own color (Enemy.update), so 4 colors
        # spawned means all 4 gun/shield colors are actually needed to clear
        for color in config.SHIELD_COLORS:
            x = random.uniform(100, config.WIN_WIDTH - 150)
            y = random.uniform(150, config.WIN_HEIGHT - 150)
            self.enemies.append(Enemy(x, y, color, self.batch, self.entity_group))
        self.hint_label.text = (
            "P1: F for shield, pinch hud buttons then sing to color/size it | "
            "P2: L for gun, pinch hud button then P1 sings its color, click enemies to shoot"
        )

    def _spawn_exit_gate(self):
        self.phase = "cleared"
        self._spawn_gate(self._enter_treasure, melody=True)
        self.hint_label.text = "room clear - P2: wake the exit crystal | P1: sing its melody to open it"

    def _enter_treasure(self):
        self.manager.set_state("treasure")

    def on_enter(self, **kwargs):
        self.manager.window.push_handlers(self.keys)
        music.play("assets/sound/Dungeon.mp3")

    def on_exit(self):
        self.manager.window.remove_handlers(self.keys)

    def on_update(self, dt):
        self.shield.update(dt)
        self.shield_hud.sync_with_shield()
        self.gun.update(dt)
        self.gun_hud.sync_with_gun()
        self.player1.update(dt, self.keys, self.tilemap.is_walkable)
        self.player2.update(dt, self.keys, self.tilemap.is_walkable)

        self.gem.update(dt)
        near = (
            self.gem.in_range(self.player1.x, self.player1.y)
            or self.gem.in_range(self.player2.x, self.player2.y)
        )
        self.gem.show_hint(near)

        gate = self.gate
        if gate is not None:
            gate.update(dt)
            # gate unlocked color alone doesnt open it anymore, both P1
            # and P2 have to physically walk in, whoever first just
            # disappears until the other catches up (see Gate.try_enter).
            # cache the gate in a local first - try_enter can fire
            # on_unlock the instant the second player registers, and that
            # callback (_start_combat) sets self.gate = None, so re-reading
            # self.gate for the second call would crash once a pair
            # completes on the same frame
            if gate.try_enter(self.player1, *self.player1.collision_box()):
                self.player1.sprite.visible = False
            if gate.try_enter(self.player2, *self.player2.collision_box()):
                self.player2.sprite.visible = False

        if self.phase == "combat":
            self._update_combat(dt)

    def _update_combat(self, dt):
        targets = [(self.player1.x, self.player1.y), (self.player2.x, self.player2.y)]
        for enemy in self.enemies:
            bullet = enemy.update(dt, targets, self.batch, self.entity_group)
            if bullet is not None:
                self.bullets.append(bullet)

        for bullet in self.bullets:
            bullet.update(dt)

        self._resolve_bullets()

        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
        # keep exploding bullets around until their pop animation finishes,
        # only "alive" (still flying) ones stop moving/colliding this frame
        self.bullets = [bullet for bullet in self.bullets if not bullet.finished]

        if not self.enemies:
            self._spawn_exit_gate()

    def _resolve_bullets(self):
        for bullet in self.bullets:
            if not bullet.alive:
                continue

            # the tilemap's real walls (dungeon.tmx's "blocks" layers, same
            # ones player movement already respects) - bullets used to only
            # know about the two hardcoded obstacle rects below and flew
            # straight through actual stone walls
            box_size = bullet.radius * 2
            if not self.tilemap.is_walkable(
                bullet.x - bullet.radius, bullet.y - bullet.radius, box_size, box_size
            ):
                bullet.destroy()
                continue

            for obstacle in self.obstacles:
                if bullet.hits_rect(obstacle.x, obstacle.y, obstacle.width):
                    bullet.destroy()
                    break
            if not bullet.alive:
                continue

            if bullet.owner == "enemy":
                self._resolve_enemy_bullet(bullet)
            else:
                self._resolve_player_bullet(bullet)

    def _resolve_enemy_bullet(self, bullet):
        # only a same-color bullet gets absorbed anything else flies
        # straight through the tornado like it isn't even there
        if self.shield.blocks(bullet.color) and bullet.hits_rect(
            self.shield.x - self.shield.size / 2, self.shield.y - self.shield.size / 2, self.shield.size
        ):
            bullet.destroy()
            return

        if bullet.hits_rect(self.player1.x, self.player1.y, self.player1.size):
            bullet.destroy()
            self._lose_heart(self.hearts1)
        elif bullet.hits_rect(self.player2.x, self.player2.y, self.player2.size):
            bullet.destroy()
            self._lose_heart(self.hearts2)

    def _resolve_player_bullet(self, bullet):
        for enemy in self.enemies:
            if enemy.alive and bullet.hits_rect(enemy.x, enemy.y, enemy.size):
                enemy.take_hit(bullet.color)
                bullet.destroy()
                break

    def _lose_heart(self, hearts):
        if hearts.lose() <= 0:
            self.manager.set_state("end", won=False)

    def on_draw(self):
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        # TODO: replace with real "dungeon cleared" condition
        if symbol == key.ENTER:
            self.manager.set_state("treasure")
        # TODO: replace with real "player died" condition
        elif symbol == key.O:
            self.manager.set_state("end", won=False)
        elif symbol == key.L:
            self.player2.handle_key_press(symbol, self.gun)
        else:
            self.player1.handle_key_press(symbol, interactables=(self.lever,))

    def on_mouse_motion(self, x, y, dx, dy):
        self.shield_hud.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.shield_hud.on_mouse_press(x, y, button, modifiers):
            return
        if self.gun_hud.on_mouse_press(x, y, button, modifiers):
            return
        if self.gem.on_mouse_press(x, y):
            return
        if self.gate is not None and self.gate.on_mouse_press(x, y):
            return
        if self.shield.on_mouse_press(x, y):
            return

        if self.phase == "combat":
            bullet = self.player2.try_shoot(
                x, y, self.gun, self.batch, self.entity_group,
            )
            if bullet is not None:
                self.bullets.append(bullet)
                self.manager.stats.record_bullet_fired()
                return

        self.player2.try_interact_at(x, y, (self.lever,))

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.shield.on_mouse_drag(dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        self.shield.on_mouse_release()

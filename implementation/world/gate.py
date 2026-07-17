# here comes all gate logic (dont know actually if we need it seperately but would be i think easier to debug and look for stuff)
# also normaly you would do everything seperately e.g. unity so why not here also hihi
#
# sprites: assets/gate/basic/tile000-005.png loops while idle (nobody's
# woken it up yet). while P1 is singing at it, it freezes on tile000.png of
# whichever color folder (red/green/blue/yellow) the live pitch currently
# maps to color_folder() from entities/shield.py, same bucket everything
# else (shield/chest/gem) uses basic/tile000.png while silent. once the
# target color is held long enough to lock, it switches to looping
# tile000-005 of that color folder as the "unlocked, glowing" animation.
#
# locking the color no longer opens the gate by itself, P1 and P2 both
# have to physically walk into it afterwards (see try_enter()). whichever
# one gets there first "disappears" (their sprite hides, callers job) while
# waiting for the other, on_unlock only fires once both have walked in.
import random

import pyglet

import config
from entities.shield import color_folder, colors_match, frequency_to_color
from entities.sprite_anim import load_animation, load_image
from input import audio_input
from world.interactable import Interactable

LOCK_HOLD_TIME = 2.0
COLOR_TOLERANCE = 35
GATE_SPRITE_PIXELS = 32
GATE_FRAME_DURATION = 0.12
GATE_LOOP_FRAMES = tuple(range(0, 6))


def _gate_loop_animation(folder):
    return load_animation(
        f"assets/gate/{folder}", GATE_LOOP_FRAMES, GATE_FRAME_DURATION, loop=True, name_prefix="tile"
    )


def _gate_listening_image(folder):
    return load_image(f"assets/gate/{folder}/tile000.png", anchor_center=False)


class Gate(Interactable):
    # P2 clicks/pinches to wake it up, then P1 sings its target color until
    # it locks, then both P1 and P2 have to walk into it - shared by the
    # overworld gate and the dungeon's entry/exit gates, so this mechanic
    # only gets built once
    def __init__(self, x, y, size, batch, group, on_unlock=None,
                 target_color=None, stats=None,
                 hint="P2: click/pinch to wake it up, then P1: sing its color"):
        # not calling Interactable.__init__ - gates render via a sprite,
        # not the base rectangle, same deal as Chest/Gem. contains()/
        # in_range()/show_hint() still come for free from Interactable,
        # they only touch x/y/size/hint_label, all set right here
        self.x = x
        self.y = y
        self.size = size

        # ---- color-matching target -----------------------------------
        # NOTE for whoever builds the melody mechanic (idea.md wants the
        # gate to eventually check a short SUNG SEQUENCE instead of one
        # held pitch): target_color/color_name/COLOR_TOLERANCE below are
        # only used by the single-sustained-pitch check in update(). swap
        # that out for a sequence buffer (Shield._update_tune in
        # entities/shield.py already buffers stable notes the same way a
        # melody check would need to) and call self._lock() once the
        # sequence matches - _lock() is the single entry point everything
        # downstream (the walk-in requirement, on_unlock) depends on, and
        # it doesn't care *how* the gate decided it's unlocked.
        self.target_color = target_color or random.choice(config.SHIELD_COLORS)
        self.target_folder = color_folder(self.target_color)
        self.color_name = config.SHIELD_COLOR_NAMES[config.SHIELD_COLORS.index(self.target_color)]
        self.on_unlock = on_unlock
        # optional GameStats if given, every sung frame while listening
        # counts toward the end screen's pitch accuracy ratio
        self.stats = stats

        self.listening = False
        self.locked = False
        self._match_timer = 0.0

        # ---- walk-in requirement ---------------------------------------
        self._entered = set()  # holds whichever player object(s) have walked in

        self.sprite = pyglet.sprite.Sprite(
            _gate_loop_animation("basic"), x=x, y=y, batch=batch, group=group,
        )
        self.sprite.scale = size / GATE_SPRITE_PIXELS

        self.hint_label = pyglet.text.Label(
            hint, x=x + size / 2, y=y + size + 10,
            anchor_x="center", anchor_y="bottom",
            font_size=11, color=(255, 255, 255, 255),
            batch=batch, group=group,
        )
        self.hint_label.visible = False

    def on_mouse_press(self, x, y):
        if self.locked or not self.contains(x, y):
            return False
        self.listening = True
        self.hint_label.text = f"P1: sing {self.color_name.upper()} to unlock it!"
        self.sprite.image = _gate_listening_image("basic")
        return True

    def update(self, dt):
        if not self.listening or self.locked:
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.sprite.image = _gate_listening_image("basic")
            return

        color = frequency_to_color(frequency)
        self.sprite.image = _gate_listening_image(color_folder(color))

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock()
        else:
            self._match_timer = 0.0

    def _lock(self):
        self.locked = True
        self.listening = False
        self.sprite.image = _gate_loop_animation(self.target_folder)
        self.hint_label.text = "P1 & P2: both walk into the gate to go through!"

    def try_enter(self, player, x, y):
        # called every frame per player by the owning state. only matters
        # once the gate's actually unlocked - walking through a dark gate
        # does nothing. returns True the instant this particular player's
        # entry registers, so the caller knows to hide that player's sprite
        if not self.locked or player in self._entered or not self.contains(x, y):
            return False

        self._entered.add(player)
        if len(self._entered) < 2:
            self.hint_label.text = "one of you is through - the other: walk in too!"
        elif self.on_unlock:
            self.on_unlock()
        return True

    def delete(self):
        self.sprite.delete()
        self.hint_label.delete()

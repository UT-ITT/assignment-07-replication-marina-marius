# here comes the treasure chamber's chest logic: sing it the right color,
# then drag it onto its marked spot - do both and its solved. combines the
# same two tricks world/gate.py and Pushable already know, just on one object
#
# sprites: assets/chest/basic001.png is the neutral "no color yet" look,
# assets/chest/<color>001.png is what it swaps to while P1's live pitch (or
# the locked-in target) lands on that color same color_folder() bucket
# gate.py/shield.py already use. assets/chest/skull/skull001-004.png is the
# one-shot "final chest opening" animation once all 3 are solved.
import pyglet

import config
from entities.shield import color_folder, colors_match, frequency_to_color
from entities.sprite_anim import load_animation, load_image
from input import audio_input
from world.gate import LOCK_HOLD_TIME, COLOR_TOLERANCE
from world.interactable import Interactable

SLOT_TOLERANCE = 24
CHEST_SPRITE_PIXELS = 32
CHEST_BASIC_IMAGE = "assets/chest/basic001.png"

SKULL_FRAME_DURATION = (
    0.35  # slow and deliberate, not a snappy pop like the projectiles/shield
)
SKULL_OPEN_FRAMES = tuple(range(1, 5))


def _chest_color_image(folder):
    return load_image(f"assets/chest/{folder}001.png", anchor_center=False)


def _skull_open_animation():
    return load_animation(
        "assets/chest/skull",
        SKULL_OPEN_FRAMES,
        SKULL_FRAME_DURATION,
        loop=False,
        name_prefix="skull",
    )


class Chest(Interactable):
    # states: locked (not its turn) -> idle (its turn, is_active) ->
    # listening (P1 singing) -> colored (locked in, draggable) -> solved
    def __init__(
        self,
        x,
        y,
        size,
        target_color,
        target_slot,
        batch,
        group,
        on_solved=None,
        stats=None,
        hint="P2: click/pinch to wake it up, then P1: sing its color",
    ):
        # not calling Interactable.__init__ chests render via a color-
        # swapping sprite, not the base rectangle, so theres nothing to
        # reuse there besides x/y/size and the hint label, built directly below
        self.x = x
        self.y = y
        self.size = size
        self.target_color = target_color
        self.target_folder = color_folder(target_color)
        self.color_name = config.SHIELD_COLOR_NAMES[
            config.SHIELD_COLORS.index(target_color)
        ]
        self.target_slot = target_slot
        self.on_solved = on_solved
        self.stats = stats

        self.is_active = False
        self.listening = False
        self.colored = False
        self.solved = False
        self.grabbed = False
        self._match_timer = 0.0

        self.sprite = pyglet.sprite.Sprite(
            load_image(CHEST_BASIC_IMAGE, anchor_center=False),
            x=x,
            y=y,
            batch=batch,
            group=group,
        )
        self.sprite.scale = size / CHEST_SPRITE_PIXELS

        self.hint_label = pyglet.text.Label(
            hint,
            x=x + size / 2,
            y=y + size + 10,
            anchor_x="center",
            anchor_y="bottom",
            font_size=11,
            color=(255, 255, 255, 255),
            batch=batch,
            group=group,
        )
        self.hint_label.visible = False

        # outline showing where this chest actually belongs, visible from the
        # start - a plain Box, not BorderedRectangle: that one only supports
        # a single alpha shared between fill and border, so a transparent
        # fill (alpha 0) was silently zeroing the border out too, making the
        # whole marker invisible
        self.slot_marker = pyglet.shapes.Box(
            target_slot[0],
            target_slot[1],
            size,
            size,
            thickness=3,
            color=target_color[:3],
            batch=batch,
            group=group,
        )

    def activate(self):
        # TreasureState calls this once its this chest turn in the sequence
        self.is_active = True
        self.sprite.image = load_image(CHEST_BASIC_IMAGE, anchor_center=False)

    def on_mouse_press(self, x, y):
        if not self.is_active or self.solved or not self.contains(x, y):
            return False
        if not self.colored:
            self.listening = True
            self.hint_label.text = f"P1: sing {self.color_name.upper()} to color it!"
        else:
            self.grabbed = True
        return True

    def on_mouse_drag(self, dx, dy):
        if not self.grabbed:
            return
        self.x = min(max(self.x + dx, 0), config.WIN_WIDTH - self.size)
        self.y = min(max(self.y + dy, 0), config.WIN_HEIGHT - self.size)
        self.sprite.x = self.x
        self.sprite.y = self.y
        self.hint_label.x = self.x + self.size / 2
        self.hint_label.y = self.y + self.size + 10

    def on_mouse_release(self):
        if not self.grabbed:
            return
        self.grabbed = False
        self._check_solved()

    def _check_solved(self):
        slot_x, slot_y = self.target_slot
        if (
            abs(self.x - slot_x) > SLOT_TOLERANCE
            or abs(self.y - slot_y) > SLOT_TOLERANCE
        ):
            return
        self.x, self.y = slot_x, slot_y
        self.sprite.x, self.sprite.y = slot_x, slot_y
        self.solved = True
        self.hint_label.visible = False
        if self.on_solved:
            self.on_solved()

    def update(self, dt):
        if not self.is_active or self.solved or not self.listening:
            return

        frequency = audio_input.current_frequency
        if frequency <= 0:
            self._match_timer = 0.0
            self.sprite.image = load_image(CHEST_BASIC_IMAGE, anchor_center=False)
            return

        color = frequency_to_color(frequency)
        self.sprite.image = _chest_color_image(color_folder(color))

        matched = colors_match(color, self.target_color, COLOR_TOLERANCE)
        if self.stats:
            self.stats.record_pitch_sample(matched)

        if matched:
            self._match_timer += dt
            if self._match_timer >= LOCK_HOLD_TIME:
                self._lock_color()
        else:
            self._match_timer = 0.0

    def _lock_color(self):
        self.colored = True
        self.listening = False
        self.sprite.image = _chest_color_image(self.target_folder)
        self.hint_label.text = "P2: click/pinch + drag it onto its marked spot"

    def delete(self):
        self.sprite.delete()
        self.slot_marker.delete()
        self.hint_label.delete()


class SkullChest:
    # spawns once all 3 color chests are solved: plays the opening animation
    # once (slowly this is the payoff, not a quick pop), then just sits on
    # the last frame. on_open fires the instant that animation finishes, so
    # whoever owns this can spawn the diamond right on cue
    def __init__(self, x, y, size, batch, group, on_open=None):
        self.on_open = on_open
        self.opened = False
        self.sprite = pyglet.sprite.Sprite(
            _skull_open_animation(),
            x=x,
            y=y,
            batch=batch,
            group=group,
        )
        self.sprite.scale = size / CHEST_SPRITE_PIXELS
        self.sprite.push_handlers(on_animation_end=self._on_open_end)

    def _on_open_end(self):
        self.opened = True
        if self.on_open:
            self.on_open()

    def delete(self):
        self.sprite.delete()

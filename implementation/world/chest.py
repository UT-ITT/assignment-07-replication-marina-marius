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
    # same corner-anchor convention as _chest_color_image/CHEST_BASIC_IMAGE -
    # SkullChest only ever plays this one animation on its sprite (never
    # swaps to a differently-anchored image later, unlike Gate/Chest), so
    # this couldn't cause a mid-play jump, but a center anchor would still
    # have quietly placed it off from the (x, y) its caller actually asked for
    return load_animation(
        "assets/chest/skull",
        SKULL_OPEN_FRAMES,
        SKULL_FRAME_DURATION,
        loop=False,
        name_prefix="skull",
        anchor_center=False,
    )


class Chest(Interactable):
    # states: locked (not its turn) -> idle (its turn, is_active) ->
    # listening (P1 singing) -> colored (locked in, draggable) -> placed
    # (snapped into *some* slot, right or wrong - not revealed yet) ->
    # once all 3 chests are placed, TreasureState checks the whole group at
    # once: every chest in its own real target_slot -> solved for good,
    # otherwise every chest scatters back to square one. a single chest
    # never finds out right/wrong on its own - only the full group does
    def __init__(
        self,
        x,
        y,
        size,
        target_color,
        target_slot,
        batch,
        group,
        on_placed=None,
        stats=None,
        slots_provider=None,
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
        self.target_slot = target_slot
        self.current_slot = None
        # which slots are still up for grabs right now - a callable, not a
        # plain list, since occupancy changes as sibling chests get placed
        # one after another (a slot another chest already snapped into
        # can't be dropped into again). defaults to "just my own slot" for
        # any caller with no siblings to coordinate with at all
        self.slots_provider = slots_provider or (lambda: [target_slot])
        self.on_placed = on_placed
        self.stats = stats

        self.is_active = False
        self.listening = False
        self.colored = False
        self.placed = False  # sitting in a slot, awaiting the group verdict
        self.solved = False  # permanently done - only ever set from outside,
        # once the *whole* group of 3 has been confirmed correct
        self.grabbed = False
        self._match_timer = 0.0
        self._default_hint = hint  # scatter() resets the hint text back to this

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

        # outline showing where this chest belongs - deliberately plain
        # black, not target_color, so the slot itself gives no hint at all
        # about which color goes where. that's the actual riddle: singing
        # is the only way to find a chest's real color, position is a
        # completely separate thing to work out. a plain Box, not
        # BorderedRectangle: that one only supports a single alpha shared
        # between fill and border, so a transparent fill (alpha 0) was
        # silently zeroing the border out too, making the whole marker invisible
        self.slot_marker = pyglet.shapes.Box(
            target_slot[0],
            target_slot[1],
            size,
            size,
            thickness=3,
            color=(0, 0, 0),
            batch=batch,
            group=group,
        )

    def activate(self):
        # TreasureState calls this once its this chest turn in the sequence
        self.is_active = True
        self.sprite.image = load_image(CHEST_BASIC_IMAGE, anchor_center=False)

    def on_mouse_press(self, x, y):
        if not self.is_active or self.solved or self.placed or not self.contains(x, y):
            return False
        if not self.colored:
            self.listening = True
            # deliberately doesn't name the color - the puzzle is figuring
            # it out from the target slot's own colored outline, not being
            # told outright
            self.hint_label.text = "P1: sing to match its color!"
        else:
            self.grabbed = True
        return True

    def note_still_pressed(self, x, y):
        # a held pinch very naturally spans the whole "click to start
        # listening -> P1 sings -> locks" sequence without ever letting go
        # in between - there's no second on_mouse_press in that case to
        # flip grabbed, so a still-held pointer sitting over the chest the
        # instant it locks needs to grab it right then instead of silently
        # requiring a release-and-repress the player has no reason to expect.
        # TreasureState calls this every frame the button/pinch is down
        if self.colored and not self.grabbed and not self.placed and self.contains(x, y):
            self.grabbed = True

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
        self._check_placed()

    def _check_placed(self):
        # snaps into whichever *still-open* marked slot it was actually
        # dropped near - right or wrong, doesn't matter, so the snap itself
        # never tells you anything. a slot a sibling chest already grabbed
        # is off the table (slots_provider only ever returns open ones).
        # right/wrong isn't decided here at all anymore - TreasureState
        # checks the whole group only once every chest has been placed
        # somewhere, via on_placed
        available = self.slots_provider()
        if not available:
            return  # every slot's already taken, nothing to snap into

        nearest = min(
            available,
            key=lambda slot: abs(self.x - slot[0]) + abs(self.y - slot[1]),
        )
        if (
            abs(self.x - nearest[0]) > SLOT_TOLERANCE
            or abs(self.y - nearest[1]) > SLOT_TOLERANCE
        ):
            return  # not close to any open slot, just leave it where it landed

        self.x, self.y = nearest
        self.sprite.x, self.sprite.y = nearest
        self.current_slot = nearest
        self.placed = True
        self.hint_label.visible = False
        if self.on_placed:
            self.on_placed(self)

    def scatter(self, x, y):
        # TreasureState calls this on every chest at once when the group
        # of 3 turns out wrong - back to a fresh (usually different) spot,
        # uncolored, unplaced, has to be sung and placed all over again.
        # is_active resets too - the solve order starts over from chest 0,
        # so chest 1/2 shouldn't stay clickable just because they already
        # had their turn earlier this round
        self.is_active = False
        self.x = x
        self.y = y
        self.sprite.x = x
        self.sprite.y = y
        self.current_slot = None
        self.placed = False
        self.colored = False
        self.listening = False
        self._match_timer = 0.0
        self.sprite.image = load_image(CHEST_BASIC_IMAGE, anchor_center=False)
        self.hint_label.x = x + self.size / 2
        self.hint_label.y = y + self.size + 10
        self.hint_label.text = self._default_hint

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

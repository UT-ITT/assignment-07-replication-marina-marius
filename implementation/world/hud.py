# this file is the for the dungeon overlay
# so the idea is following:
# P1 can do the following with theri voice
# 1. change color of shield (hold a pitch steady for 2s)
# 2. change size of shield (scream for a 3s window, loudest moment wins)
# to set those P2 need to pinch the right overlay so P1 can start using all the vocal chords they have
# why? because its easier handling for us (in my opinion)
import pyglet

import audio_settings
import config
from world.buttons import Button

# (mode we hand to shield.set_mode, label the button actually shows)
MODE_BUTTONS = [
    ("color", "Pitch -> Color"),
    ("size", "Scream -> Size (3s)"),
]


class ShieldHud:
    # pops up whenever the shield is out (F key), P2 pinches/clicks a button
    # here to decide which of the two mechanics P1 voice controls right now.
    # either button can be pinched again any time, even after its mode's
    # already locked once, that's how P2 renews it (Shield.set_mode resets
    # just that mode's done flag, dragging pauses again until it re-locks)
    def __init__(self, shield, batch, group):
        self.shield = shield
        self.buttons = {}
        self._hover_pos = None

        button_width, button_height, gap = 180, 50, 20
        total_width = len(MODE_BUTTONS) * button_width + (len(MODE_BUTTONS) - 1) * gap
        start_x = config.WIN_WIDTH // 2 - total_width // 2
        y = 30

        for i, (mode, label) in enumerate(MODE_BUTTONS):
            x = start_x + i * (button_width + gap)
            self.buttons[mode] = Button(
                x, y, button_width, button_height, label, batch, group
            )

        self.set_visible(False)

    def set_visible(self, visible):
        for button in self.buttons.values():
            button.rect.visible = visible
            button.label.visible = visible

    def sync_with_shield(self):
        # shows/hides with the shield
        self.set_visible(self.shield.active)
        hovered_mode = (
            self._hit_mode(*self._hover_pos)
            if (self.shield.active and self._hover_pos)
            else None
        )

        for mode, button in self.buttons.items():
            button.set_active(mode == self.shield.mode)
            if mode == hovered_mode and mode != self.shield.mode:
                r, g, b = button.idle_color
                button.rect.color = (
                    min(255, r + 40),
                    min(255, g + 40),
                    min(255, b + 40),
                )

    def on_mouse_motion(self, x, y, dx, dy):
        # P2 pinch literally drags the real mouse around (see Controller
        # in gesture_tracking.py), so this fires for a hand just as happily as for an actual mouse
        self._hover_pos = (x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.shield.active:
            return False
        mode = self._hit_mode(x, y)
        if mode is None:
            return False
        self.shield.set_mode(mode)
        return True

    def _hit_mode(self, x, y):
        for mode, button in self.buttons.items():
            if button.hit_test(x, y):
                return mode
        return None


class GunHud:
    # P2's other hud button: same "sing a color and hold it for 2s" trick as
    # the shield's color mode now, just for whatever color gets loaded into
    # P2's next bullets instead of the shield. only shown while the gun is
    # drawn (L)
    def __init__(self, gun, batch, group, x, y):
        self.gun = gun
        self.button = Button(x, y, 160, 50, "Gun: sing a color!", batch, group)
        self.set_visible(False)

    def set_visible(self, visible):
        self.button.rect.visible = visible
        self.button.label.visible = visible

    def sync_with_gun(self):
        self.set_visible(self.gun.active)
        self.button.rect.color = self.gun.color[:3]
        self.button.label.text = (
            "Gun: LOCKED" if self.gun.locked else "Gun: sing a color!"
        )

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.gun.active or not self.button.hit_test(x, y):
            return False
        self.gun.start_color_pick()
        return True


class HeartsDisplay:
    # three little pips per player, dimmed one at a time as hits land
    # stand-ins until actual heart sprites exist
    def __init__(self, x, y, batch, group, count=config.PLAYER_HEART_COUNT):
        self.count = count
        self.pips = [
            pyglet.shapes.Circle(
                x + i * 26, y, 10, color=(220, 60, 60), batch=batch, group=group
            )
            for i in range(count)
        ]

    def lose(self):
        if self.count <= 0:
            return 0
        self.count -= 1
        self.pips[self.count].color = (60, 60, 60)
        return self.count


class PitchLegend:
    # note-to-color legend
    def __init__(self, x, y, batch, group, swatch_size=26, gap=6):
        self.note_labels = [
            pyglet.text.Label(
                note,
                x=x + i * (swatch_size + gap) + swatch_size / 2,
                y=y + swatch_size + 4,
                anchor_x="center",
                anchor_y="bottom",
                font_name=config.FONT_NAME,
                font_size=10,
                color=config.TEXT_COLOR,
                batch=batch,
                group=group,
            )
            for i, note in enumerate(config.SHIELD_COLOR_NOTES)
        ]
        self.swatches = [
            pyglet.shapes.Rectangle(
                x + i * (swatch_size + gap),
                y,
                swatch_size,
                swatch_size,
                color=color[:3],
                batch=batch,
                group=group,
            )
            for i, color in enumerate(config.SHIELD_COLORS)
        ]


class Slider:
    # draggable slider control
    def __init__(
        self,
        x,
        y,
        width,
        label,
        get_value,
        set_value,
        batch,
        group,
        height=10,
        fill_color=(90, 200, 140),
    ):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.set_value = set_value

        self.label = pyglet.text.Label(
            label,
            x=x,
            y=y + height + 4,
            anchor_x="left",
            anchor_y="bottom",
            font_name=config.FONT_NAME,
            font_size=10,
            color=config.TEXT_COLOR,
            batch=batch,
            group=group,
        )
        self.track = pyglet.shapes.Rectangle(
            x, y, width, height, color=(50, 50, 50), batch=batch, group=group
        )
        self.fill = pyglet.shapes.Rectangle(
            x, y, width * get_value(), height, color=fill_color, batch=batch, group=group
        )
        self.value_label = pyglet.text.Label(
            f"{round(get_value() * 100)}%",
            x=x + width + 8,
            y=y + height / 2,
            anchor_x="left",
            anchor_y="center",
            font_name=config.FONT_NAME,
            font_size=10,
            color=config.TEXT_COLOR,
            batch=batch,
            group=group,
        )

    def hit_test(self, x, y):
        pad = 6  # a little slack above/below the thin track, easier to hit
        return self.x <= x <= self.x + self.width and self.y - pad <= y <= self.y + self.height + pad

    def apply_at(self, x):
        # ignore y during drag
        fraction = (x - self.x) / self.width
        fraction = max(0.0, min(1.0, fraction))
        self.set_value(fraction)
        self.fill.width = self.width * fraction
        self.value_label.text = f"{round(fraction * 100)}%"

    def on_mouse_press(self, x, y):
        if not self.hit_test(x, y):
            return False
        self.apply_at(x)
        return True


class VolumeControls:
    # global volume slider controls
    def __init__(self, x, y, batch, group, width=120, gap=36):
        self.music_slider = Slider(
            x,
            y,
            width,
            "Music",
            audio_settings.get_music_volume,
            audio_settings.set_music_volume,
            batch,
            group,
        )
        self.sfx_slider = Slider(
            x,
            y - gap,
            width,
            "SFX",
            audio_settings.get_sfx_volume,
            audio_settings.set_sfx_volume,
            batch,
            group,
        )
        self._sliders = [self.music_slider, self.sfx_slider]
        self._active = None  # whichever slider is currently being dragged, if any

    def on_mouse_press(self, x, y):
        for slider in self._sliders:
            if slider.on_mouse_press(x, y):
                self._active = slider
                return True
        return False

    def on_mouse_drag(self, x, y):
        if self._active is None:
            return False
        self._active.apply_at(x)
        return True

    def on_mouse_release(self):
        was_active = self._active is not None
        self._active = None
        return was_active

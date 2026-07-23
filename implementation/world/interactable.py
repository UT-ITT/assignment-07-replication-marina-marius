# here comes all logic for various interactible objects (dont know actually if we need it seperately but would be i think easier to debug and look for stuff)
# also normaly you would do everything seperately e.g. unity so why not here also hihi
# actually you would do cool objects :( with own scripts that can inherent from a mother class)
import pyglet

import config


class Interactable:
    # just a rectangle that flips color when poked, so we can test P1 E key
    # and P2s pinch/click against the exact same dummy object instead of two
    def __init__(
        self,
        x,
        y,
        size,
        batch,
        group,
        label_group=None,
        idle_color=(150, 150, 150),
        active_color=(240, 220, 80),
        hint="P1: E, or P2: click/pinch, to interact",
    ):
        self.x = x
        self.y = y
        self.size = size
        self.idle_color = idle_color
        self.active_color = active_color
        self.triggered = False

        self.rect = pyglet.shapes.Rectangle(
            x,
            y,
            size,
            size,
            color=idle_color,
            batch=batch,
            group=group,
        )

        # floating "psst, something happens here" label, only shown up close
        self.hint_label = pyglet.text.Label(
            hint,
            x=x + size / 2,
            y=y + size + 10,
            anchor_x="center",
            anchor_y="bottom",
            font_name=config.FONT_NAME,
            font_size=11,
            color=(255, 255, 255, 255),
            batch=batch,
            group=label_group or group,
        )
        self.hint_label.visible = False

    def contains(self, x, y):
        return self.x <= x <= self.x + self.size and self.y <= y <= self.y + self.size

    def in_range(self, px, py, radius=64):
        return abs(px - self.x) <= radius and abs(py - self.y) <= radius

    def show_hint(self, near):
        self.hint_label.visible = near

    def interact(self):
        self.triggered = not self.triggered
        self.rect.color = self.active_color if self.triggered else self.idle_color


class Pushable(Interactable):
    # P2 mechanic B: click/pinch it to grab, then drag to push or pull it
    # around freely. pinch-holding already drags a real mouse button (see
    # gesture_tracking.Controller), so a held pinch fires on_mouse_drag just
    # like a held physical mouse would, no gesture-specific code needed here
    def __init__(self, x, y, size, batch, group, **kwargs):
        kwargs.setdefault("hint", "P2: click/pinch + drag to push or pull")
        kwargs.setdefault("idle_color", (150, 110, 200))
        super().__init__(x, y, size, batch, group, **kwargs)
        self.grabbed = False

    def on_mouse_press(self, x, y):
        if self.contains(x, y):
            self.grabbed = True
        return self.grabbed

    def on_mouse_drag(self, dx, dy):
        if not self.grabbed:
            return
        self.x = min(max(self.x + dx, 0), config.WIN_WIDTH - self.size)
        self.y = min(max(self.y + dy, 0), config.WIN_HEIGHT - self.size)
        self.rect.x = self.x
        self.rect.y = self.y
        self.hint_label.x = self.x + self.size / 2
        self.hint_label.y = self.y + self.size + 10

    def on_mouse_release(self):
        self.grabbed = False

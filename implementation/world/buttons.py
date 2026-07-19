import pyglet

import config

# Buttons: currently just a rectangle with a label that changes color when activated
# for P2 clicking/pinching it during the start menu
# Created a skeleton since we can test the logic and later on prettifyyyy it with good looking sprites
# Will add code comments in the end since this will be getting updated and I dont want to waste precise time
# rewriting my funny comments over and over again :3

class Button:

    def __init__(self, x, y, width, height, text, batch, group,
                 idle_color=(80, 80, 80), active_color=(60, 180, 90)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.idle_color = idle_color
        self.active_color = active_color
        self.active = False

        self.rect = pyglet.shapes.Rectangle(
            x, y, width, height, color=idle_color, batch=batch, group=group
        )
        self.label = pyglet.text.Label(
            text, x=x + width / 2, y=y + height / 2,
            anchor_x="center", anchor_y="center",
            font_name=config.FONT_NAME, font_size=16, batch=batch, group=group,
        )

    def hit_test(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def set_active(self, active):
        self.active = active
        self.rect.color = self.active_color if active else self.idle_color

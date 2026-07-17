# shared "load N numbered PNG frames into a pyglet Animation, anchored
# center, cached so repeat calls don't re-decode the same images off disk"
# used by anything that plays a folder-of-frames sprite animation
# (projectiles, shield tornado, ...)
import pyglet

_cache = {}


def load_animation(path_prefix, frame_numbers, duration, loop):
    key = (path_prefix, frame_numbers, duration, loop)
    if key not in _cache:
        images = []
        for number in frame_numbers:
            image = pyglet.image.load(f"{path_prefix}/{number:03d}.png")
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
            images.append(image)
        _cache[key] = pyglet.image.Animation.from_image_sequence(images, duration, loop=loop)
    return _cache[key]

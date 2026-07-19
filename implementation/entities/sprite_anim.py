# shared "load N numbered PNG frames into a pyglet Animation, anchored
# center, cached so repeat calls don't re-decode the same images off disk"
import pyglet

_animation_cache = {}
_image_cache = {}


def load_animation(path_prefix, frame_numbers, duration, loop, name_prefix="", anchor_center=True):
    # filenames are f"{path_prefix}/{name_prefix}{n:03d}.png"
    # name_prefix is only needed when the number isn't the whole filename (skull001.png
    # vs projectile's plain 001.png). anchor_center=False for anything whose
    # x/y is a bottom-left box corner elsewhere (hitboxes, AABB checks) ->
    # same reason load_image already has this flag
    key = (path_prefix, name_prefix, frame_numbers, duration, loop, anchor_center)
    if key not in _animation_cache:
        images = []
        for number in frame_numbers:
            image = pyglet.image.load(f"{path_prefix}/{name_prefix}{number:03d}.png")
            if anchor_center:
                image.anchor_x = image.width // 2
                image.anchor_y = image.height // 2
            images.append(image)
        _animation_cache[key] = pyglet.image.Animation.from_image_sequence(  # type: ignore
            images, duration, loop=loop  # type: ignore
        )
    return _animation_cache[key]


def load_image(path, anchor_center=True):
    key = (path, anchor_center)
    if key not in _image_cache:
        image = pyglet.image.load(path)
        if anchor_center:
            image.anchor_x = image.width // 2
            image.anchor_y = image.height // 2
        _image_cache[key] = image
    return _image_cache[key]

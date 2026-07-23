"""
steering_law.py – Steering Law task with a directional cursor.

The player must navigate a cursor through a series of narrow tunnel segments
without touching the walls. The cursor sprite rotates to face the direction
of mouse movement (implemented by the student in student.py).

Uses SDL3 for windowing and input, and input.py for raw mouse deltas.

Students do not need to edit this file.
The entry point is run(), called from student.py.
"""

import ctypes
import math
import sys
from base64 import b64decode
from io import BytesIO
from random import Random

import sdl3

from input import RawMouseInput

SEGMENT_TEMPLATES = [
    (0,    300),
    (45,   220),
    (-45,  220),
    (90,   260),
    (-90,  260),
    (135,  200),
    (-135, 200),
    (180,  300),
]

TUNNEL_WIDTH = 48          
NUM_SEGMENTS = 8           
CURSOR_RADIUS = 6          
LOGICAL_SIZE = 1080        
BASE_CURSOR_SIZE = 64     

def _point_segment_distance(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)

    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    closest_x = ax + t * dx
    closest_y = ay + t * dy
    return math.hypot(px - closest_x, py - closest_y)


def _segments_intersect(a0, a1, b0, b1):
    def ccw(p1, p2, p3):
        return (p3[1] - p1[1]) * (p2[0] - p1[0]) > (p2[1] - p1[1]) * (p3[0] - p1[0])

    return ccw(a0, b0, b1) != ccw(a1, b0, b1) and ccw(a0, a1, b0) != ccw(a0, a1, b1)


def _segment_distance(a0, a1, b0, b1):
    if _segments_intersect(a0, a1, b0, b1):
        return 0.0

    return min(
        _point_segment_distance(a0[0], a0[1], b0[0], b0[1], b1[0], b1[1]),
        _point_segment_distance(a1[0], a1[1], b0[0], b0[1], b1[0], b1[1]),
        _point_segment_distance(b0[0], b0[1], a0[0], a0[1], a1[0], a1[1]),
        _point_segment_distance(b1[0], b1[1], a0[0], a0[1], a1[0], a1[1]),
    )


def _has_clearance(candidate_start, candidate_end, segments, scale):
    min_gap = TUNNEL_WIDTH * scale * 2.65

    # The previous segment shares the start joint, so compare only against
    # older parts of the route where overlap would visually muddy the maze.
    for previous in segments[:-1]:
        if _segment_distance(candidate_start, candidate_end,
                             previous["start"], previous["end"]) < min_gap:
            return False

    return True


def _build_maze(rng: Random, width: int, height: int, scale: float):
    cx = width * 0.12
    cy = height * 0.5
    angle = 0.0  # pointing right

    segments = []
    angle_pool = [math.radians(a) for a, _ in SEGMENT_TEMPLATES]
    length_pool = [l * scale for _, l in SEGMENT_TEMPLATES]

    attempts = 0
    i = 0
    while i < NUM_SEGMENTS and attempts < 900:
        attempts += 1
        idx = rng.randrange(len(angle_pool))
        rel_angle = angle_pool[idx]

        # Avoid hard reversals that draw the corridor back over itself.
        if segments and abs(rel_angle) > math.radians(150):
            continue

        length = length_pool[idx]
        new_angle = angle + rel_angle

        ex = cx + math.cos(new_angle) * length
        ey = cy + math.sin(new_angle) * length

        margin = TUNNEL_WIDTH * scale * 2.8
        if not (margin < ex < width - margin and margin < ey < height - margin):
            continue

        if not _has_clearance((cx, cy), (ex, ey), segments, scale):
            continue

        tw = TUNNEL_WIDTH * scale
        perp = new_angle + math.pi / 2
        px, py = math.cos(perp) * tw, math.sin(perp) * tw

        seg = {
            "start": (cx, cy),
            "end":   (ex, ey),
            "angle": new_angle,
            "length": length,
            "left":  [(cx + px, cy + py), (ex + px, ey + py)],
            "right": [(cx - px, cy - py), (ex - px, ey - py)],
        }
        segments.append(seg)
        cx, cy = ex, ey
        angle = new_angle
        i += 1

    return segments


def _point_to_segment_dist(px, py, ax, ay, bx, by):
    """Signed distance of point P from the directed line A->B (positive = left)."""
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return math.hypot(px - ax, py - ay), 0.0
    # project onto segment
    t = ((px - ax) * dx + (py - ay) * dy) / (length * length)
    t = max(0.0, min(1.0, t))
    closest_x = ax + t * dx
    closest_y = ay + t * dy
    dist = math.hypot(px - closest_x, py - closest_y)
    # cross product for sign (positive = left of A->B)
    cross = (px - ax) * dy - (py - ay) * dx
    sign = 1.0 if cross >= 0 else -1.0
    return dist, sign * dist


def _in_tunnel(cursor_x, cursor_y, seg, scale):
    ax, ay = seg["start"]
    bx, by = seg["end"]
    tw = TUNNEL_WIDTH * scale
    r  = CURSOR_RADIUS * scale

    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return False
    cross = (cursor_x - ax) * dy - (cursor_y - ay) * dx
    lat = cross / length

    dot = (cursor_x - ax) * dx / length + (cursor_y - ay) * dy / length

    return abs(lat) <= (tw - r) and (-r <= dot <= length + r)


def _past_end(cursor_x, cursor_y, seg):
    ax, ay = seg["start"]
    bx, by = seg["end"]
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return False
    dot = (cursor_x - ax) * dx / length + (cursor_y - ay) * dy / length
    return dot >= length


def _hit_wall(cursor_x, cursor_y, seg, scale):
    ax, ay = seg["start"]
    bx, by = seg["end"]
    tw = TUNNEL_WIDTH * scale
    r  = CURSOR_RADIUS * scale

    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length == 0:
        return False
    cross = (cursor_x - ax) * dy - (cursor_y - ay) * dx
    lat = abs(cross / length)
    dot = (cursor_x - ax) * dx / length + (cursor_y - ay) * dy / length

    in_length = -r <= dot <= length + r
    return in_length and lat > (tw - r)


def _set_color(renderer, color):
    sdl3.SDL_SetRenderDrawColor(renderer, *color)


def _draw_circle(renderer, cx, cy, radius, color):
    _set_color(renderer, color)
    r = max(1, int(round(radius)))
    for y in range(-r, r + 1):
        span = math.sqrt(max(0, r * r - y * y))
        sdl3.SDL_RenderLine(renderer, cx - span, cy + y, cx + span, cy + y)


def _draw_thick_line(renderer, x0, y0, x1, y1, width, color):
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    if length == 0:
        _draw_circle(renderer, x0, y0, width / 2, color)
        return

    nx, ny = -dy / length, dx / length
    half = max(1, int(round(width / 2)))
    _set_color(renderer, color)
    for off in range(-half, half + 1):
        ox, oy = nx * off, ny * off
        sdl3.SDL_RenderLine(renderer, x0 + ox, y0 + oy, x1 + ox, y1 + oy)


def _draw_soft_background(renderer, width, height):
    _set_color(renderer, (28, 29, 27, 255))
    sdl3.SDL_RenderClear(renderer)

    band_h = max(16, height // 28)
    for y in range(0, height, band_h):
        shade = 32 + int(16 * (y / max(1, height)))
        _set_color(renderer, (shade, shade + 1, shade - 2, 255))
        band = sdl3.SDL_FRect(0, float(y), float(width), float(band_h))
        sdl3.SDL_RenderFillRect(renderer, ctypes.byref(band))


def _draw_segment_caps(renderer, seg, radius, color):
    sx, sy = seg["start"]
    ex, ey = seg["end"]
    _draw_circle(renderer, sx, sy, radius, color)
    _draw_circle(renderer, ex, ey, radius, color)


def _render(renderer, cursor_texture, cursor_w, cursor_h,
            width, height, scale,
            segments, current_seg,
            cursor_x, cursor_y,
            cursor_angle_rad,
            cursor_hotspot, cursor_scale,
            trial, max_trials, errors, collided):

    if hasattr(sdl3, "SDL_SetRenderDrawBlendMode") and hasattr(sdl3, "SDL_BLENDMODE_BLEND"):
        sdl3.SDL_SetRenderDrawBlendMode(renderer, sdl3.SDL_BLENDMODE_BLEND)
    _draw_soft_background(renderer, width, height)

    tw = TUNNEL_WIDTH * scale
    corridor_w = tw * 2
    shadow_w = corridor_w + max(14, 18 * scale)
    wall_w = max(3, round(5 * scale))

    # Draw a soft bed first so the route reads as one continuous path.
    for seg in segments:
        sx, sy = seg["start"]
        ex, ey = seg["end"]
        _draw_thick_line(renderer, sx, sy + 3 * scale, ex, ey + 3 * scale,
                         shadow_w, (0, 0, 0, 80))
        _draw_segment_caps(renderer, seg, shadow_w / 2, (0, 0, 0, 55))

    # Filled corridor surface with progress coloring.
    for i, seg in enumerate(segments):
        sx, sy = seg["start"]
        ex, ey = seg["end"]

        if i < current_seg:
            fill = (74, 111, 83, 255)
            highlight = (130, 178, 122, 255)
        elif i == current_seg:
            if collided:
                fill = (116, 62, 58, 255)
                highlight = (205, 103, 93, 255)
            else:
                fill = (72, 70, 64, 255)
                highlight = (199, 181, 126, 255)
        else:
            fill = (54, 55, 51, 255)
            highlight = (108, 108, 98, 255)

        _draw_thick_line(renderer, sx, sy, ex, ey, corridor_w, fill)
        _draw_segment_caps(renderer, seg, corridor_w / 2, fill)
        _draw_thick_line(renderer, sx, sy, ex, ey, max(2, 3 * scale), highlight)

    # Draw crisp tunnel walls and gates.
    for i, seg in enumerate(segments):
        if i < current_seg:
            wall = (147, 186, 122, 255)
        elif i == current_seg:
            wall = (198, 91, 82, 255) if collided else (222, 208, 165, 255)
        else:
            wall = (118, 119, 108, 255)

        lx0, ly0 = seg["left"][0]
        lx1, ly1 = seg["left"][1]
        rx0, ry0 = seg["right"][0]
        rx1, ry1 = seg["right"][1]

        _draw_thick_line(renderer, lx0, ly0, lx1, ly1, wall_w + 2, (0, 0, 0, 105))
        _draw_thick_line(renderer, rx0, ry0, rx1, ry1, wall_w + 2, (0, 0, 0, 105))
        _draw_thick_line(renderer, lx0, ly0, lx1, ly1, wall_w, wall)
        _draw_thick_line(renderer, rx0, ry0, rx1, ry1, wall_w, wall)

        if i >= current_seg:
            gate = (218, 178, 95, 220) if i == current_seg else (142, 121, 75, 150)
            _draw_thick_line(renderer, lx1, ly1, rx1, ry1, max(2, wall_w - 1), gate)

    seg0 = segments[0]
    _draw_thick_line(renderer,
        seg0["left"][0][0], seg0["left"][0][1],
        seg0["right"][0][0], seg0["right"][0][1],
        max(3, wall_w), (190, 178, 124, 255))

    # Cursor (rotated)
    dst = sdl3.SDL_FRect(
        cursor_x - cursor_hotspot[0] * cursor_scale,
        cursor_y - cursor_hotspot[1] * cursor_scale,
        float(cursor_w),
        float(cursor_h),
    )
    angle_deg = math.degrees(cursor_angle_rad)
    center = sdl3.SDL_FPoint(
        cursor_hotspot[0] * cursor_scale,
        cursor_hotspot[1] * cursor_scale,
    )
    sdl3.SDL_RenderTextureRotated(
        renderer, cursor_texture,
        None, ctypes.byref(dst),
        angle_deg,
        ctypes.byref(center),
        sdl3.SDL_FLIP_NONE,
    )

    _draw_hud(renderer, width, height, trial, max_trials, errors)

    sdl3.SDL_RenderPresent(renderer)


def _draw_hud(renderer, width, height, trial, max_trials, errors):
    bar_x = width * 0.05
    bar_y = height * 0.05
    bar_w = width * 0.4
    bar_h = max(10, height / 42)
    fill_w = bar_w * (trial / max_trials)

    bg = sdl3.SDL_FRect(bar_x, bar_y, bar_w, bar_h)
    _set_color(renderer, (22, 22, 20, 150))
    sdl3.SDL_RenderFillRect(renderer, ctypes.byref(bg))

    _set_color(renderer, (132, 174, 112, 255))
    filled = sdl3.SDL_FRect(bar_x, bar_y, fill_w, bar_h)
    sdl3.SDL_RenderFillRect(renderer, ctypes.byref(filled))

    _set_color(renderer, (205, 198, 178, 210))
    outline = sdl3.SDL_FRect(bar_x, bar_y, bar_w, bar_h)
    sdl3.SDL_RenderRect(renderer, ctypes.byref(outline))

    dot_size = bar_h * 0.45
    dot_y = bar_y + bar_h + dot_size * 1.5
    for e in range(errors):
        _draw_circle(renderer,
            bar_x + e * (dot_size * 1.8) + dot_size / 2,
            dot_y,
            dot_size / 2,
            (198, 91, 82, 235))



def _load_cursor_texture(renderer, cursor_png_bytes):
    try:
        from PIL import Image
        img = Image.open(BytesIO(cursor_png_bytes)).convert("RGBA")
        img.thumbnail((BASE_CURSOR_SIZE, BASE_CURSOR_SIZE), Image.LANCZOS)  # normalise, preserve aspect ratio
        w, h = img.size
        data = img.tobytes()
        surface = sdl3.SDL_CreateSurface(w, h, sdl3.SDL_PIXELFORMAT_ABGR8888)  # match Pillow byte order
        ctypes.memmove(surface.contents.pixels, data, len(data))
    except Exception as e:
        print("Cursor load failed, using fallback:", e)
        surface = sdl3.SDL_CreateSurface(8, 8, sdl3.SDL_PIXELFORMAT_ABGR8888)
        sdl3.SDL_FillSurfaceRect(surface, None, 0xFFFFFFFF)

    w = surface.contents.w if surface else 8
    h = surface.contents.h if surface else 8
    texture = sdl3.SDL_CreateTextureFromSurface(renderer, surface)
    sdl3.SDL_SetTextureBlendMode(texture, sdl3.SDL_BLENDMODE_BLEND)  # enable alpha transparency
    sdl3.SDL_DestroySurface(surface)
    return texture, w, h


DEFAULT_CURSOR_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAABwAAAAkCAYAAACaJFpUAAAErUlEQVR4nLWXT2hURxzHvzNvXExMstr8KcT0EDAWWQI91ZZArQTSWqRU4ZUKihdzy6Et7KmYjR7TS5NjE4QcVMiheNSwxIONodj0EFSIJAcDCc1mNyssNtn3Zubbg/OWdWPW1SQDP9h5O+/3me93fjOzCwAg6cG18s/71ki2kfydZIfrK5JiP4FxvmprJPvKnsv9Ah4mue6gDMNwKJVKKffd3lvsgC9I2jAMteP+mclkjkfQPbWY5GGt9QuSXFtbs+fPnw8XFhboJnGlbNzeqC0HbmxsWKUUhRD6+vXrkcu3nz572uzGqj0F5nI529LSQgAEYE+cOKEfPHhAks9IfuXGy10VVCXwyJEjFEJQKRWBw8uXL3N5eZkkh8reez+1bwICoBCCUkpKKQnAxONxc/PmTZK8S/I4APi+/+4FVQ3oFNLzvJLaM2fOcGZmJkvyhyjH5ORk7QVVCzDqO7CWUjKZTHJ1dXWMZCMAnDp1qjaLawVG4Sy2AHR3dzdHR0fnSJ4UQgCATKVS1QvqXYFRuKLSANjX1xeOjIz82NTUFKXdWe37KIxCKUXP8wwANjc3s6en5+6dO3balVLR9tleUG8Dep73VrXO4tC9twLgjQX11kX2PA/GmFJ/YGAA586dg7UWnvdaYQoASkppisViu1Lqdnd395etra0DQghNUgkh9I4KyyqSFy5cYCKRoBCCp0+fZkUzFWFJapIBSRpjZkl+sqOl2WzWtra2lqy6evUqSfLGjRslm9PpNMMwpNa6Er5T2yL5E8lD2yxVSiGfzyMej2NsbAy+78MYg7Nnz6KtrQ2ZTAbj4+O2t7dXPnz4cGp6eno2CIJ6rbWtzCWlhDHGSCnrEolE7NixYwe3KVxdXbU9PT189OjRq6ltbZkgCCxJ9vf3EwAbGhp0oVCg1vovAIcAHAbQVCUa3ThZAvLV3ceXL1/ara0tkrQRiCSttXzy5AljsRgB8Nq1a9GafeF5HmKxGDzPqxruYHgd6BbdRKDHjx/P5vP5f621JGl7e3sphGBnZ2fo1vA2AHH//n3lKrVabAcaY0Jn5X8TExMTANqNMcOOH966dau07+7du2dJFubn5z90eWq7NRww59RxZWXlme/7PwP4SEoJkiejst/c3GRXV1e0RTRJBkEw6PLUdmOQbDLGFElyamrqj4aGBh9As1IKqVRKkoyRXHAqzdDQUHSWmqWlJZJcWl5eriMpalJZKBTaSP6dz+e/A/ApgA+klAAg6G51kr9Gti4uLrK+vp5CCCaTSU2SuVzum5pVkqwjWQcAk5OTMVdNojwByc9IGq21IcmLFy8SAGOxmM5kMiSZduNq/61TNjtR8VxU2ppOp3n06FEODg5yfX3dkgyLxWKiZmg1799kaxiG3NjYiHZPqLW2xpjh8vHv3SptLd+nQRAYY0x0qBZItlcTUNNMhBDGJfgHwCKALmOM9jxPHThwQAJANptdmZ2dnWlsbJSlE2WXKiNbo0OAJPXz58/nh4eHf2tpafkeQKcTsXtima2fb25uZufm5qYvXbr0C4BvAXQBOKiUwp6oqwCrZDLZBeBrAB93dHTUlR3M+/cn1vf9Onc4vBPofzJx+j/OkRK+AAAAAElFTkSuQmCC"
)


def run(rotation_function=None,
        cursor_png_b64: str | None = None,
        cursor_png_path: str | None = None,
        cursor_hotspot=(4, 4),
        cursor_scale=1.0,
        num_mazes=3,
        seed=42):


    if rotation_function is None:
        def rotation_function(raw_dx, raw_dy, current_angle):
            return current_angle  # no rotation – stays fixed

    if cursor_png_path is not None:
        with open(cursor_png_path, "rb") as f:
            cursor_png_bytes = f.read()
    elif cursor_png_b64 is not None:
        cursor_png_bytes = b64decode(cursor_png_b64)
    else:
        cursor_png_bytes = b64decode(DEFAULT_CURSOR_PNG)

    if not sdl3.SDL_Init(sdl3.SDL_INIT_VIDEO):
        raise RuntimeError(f"SDL_Init failed: {sdl3.SDL_GetError()}")

    window = renderer = raw = cursor_texture = None

    try:
        window = sdl3.SDL_CreateWindow(b"Steering Law Task", 1280, 720,
                                       sdl3.SDL_WINDOW_FULLSCREEN)
        if not window:
            raise RuntimeError(f"SDL_CreateWindow failed")

        renderer = sdl3.SDL_CreateRenderer(window, None)
        if not renderer:
            raise RuntimeError(f"SDL_CreateRenderer failed")

        ww = ctypes.c_int()
        wh = ctypes.c_int()
        sdl3.SDL_GetWindowSize(window, ww, wh)
        width, height = ww.value, wh.value
        scale = min(width, height) / LOGICAL_SIZE

        if not sdl3.SDL_SetWindowRelativeMouseMode(window, True):
            raise RuntimeError("Could not enable relative mouse mode")

        cursor_texture, base_cw, base_ch = _load_cursor_texture(renderer, cursor_png_bytes)
        cursor_w = base_cw * cursor_scale
        cursor_h = base_ch * cursor_scale

        raw = RawMouseInput(window)
        raw.install()

        rng = Random(seed)
        total_errors = 0
        maze_index = 0

        while maze_index < num_mazes:
            segments = _build_maze(rng, width, height, scale)
            if not segments:
                break 

            sx, sy = segments[0]["start"]
            cursor_x, cursor_y = float(sx), float(sy)
            cursor_angle = segments[0]["angle"]  

            current_seg = 0
            collided = False
            collision_timer = 0  

            event = sdl3.SDL_Event()
            running = True

            while running:
                while sdl3.SDL_PollEvent(ctypes.byref(event)):
                    if event.type == sdl3.SDL_EVENT_QUIT:
                        maze_index = num_mazes  # exit all
                        running = False

                    elif event.type == sdl3.SDL_EVENT_KEY_DOWN:
                        if event.key.key == sdl3.SDLK_ESCAPE:
                            maze_index = num_mazes
                            running = False

                    elif event.type == sdl3.SDL_EVENT_MOUSE_MOTION:
                        raw.feed_sdl_motion(event.motion.xrel, event.motion.yrel)

                raw_dx, raw_dy = raw.consume()

                cursor_angle = rotation_function(raw_dx, raw_dy, cursor_angle)

                speed = math.hypot(raw_dx, raw_dy)
                cursor_x += raw_dx
                cursor_y += raw_dy
                cursor_x = max(0.0, min(float(width - 1), cursor_x))
                cursor_y = max(0.0, min(float(height - 1), cursor_y))

                seg = segments[current_seg]
                if _hit_wall(cursor_x, cursor_y, seg, scale):
                    total_errors += 1
                    collided = True
                    collision_timer = 20
                    cursor_x, cursor_y = seg["start"]

                if collision_timer > 0:
                    collision_timer -= 1
                    if collision_timer == 0:
                        collided = False

                if _past_end(cursor_x, cursor_y, seg):
                    current_seg += 1
                    if current_seg >= len(segments):
                        running = False 

                _render(renderer, cursor_texture, cursor_w, cursor_h,
                        width, height, scale,
                        segments, current_seg,
                        cursor_x, cursor_y,
                        cursor_angle,
                        cursor_hotspot, cursor_scale,
                        maze_index, num_mazes, total_errors, collided)

            maze_index += 1

    finally:
        if raw is not None:
            raw.close()
        if cursor_texture is not None:
            sdl3.SDL_DestroyTexture(cursor_texture)
        if window is not None:
            sdl3.SDL_SetWindowRelativeMouseMode(window, False)
        if renderer is not None:
            sdl3.SDL_DestroyRenderer(renderer)
        if window is not None:
            sdl3.SDL_DestroyWindow(window)
        sdl3.SDL_Quit()
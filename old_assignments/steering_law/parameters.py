# This is the only file you need to edit

import math

from steering_law import run

# Rotation funciton:
#   raw_dx       – raw horizontal mouse delta this frame (pixels, right = +)
#   raw_dy       – raw vertical mouse delta this frame (pixels, down = +)
#   current_angle_rad – the cursor's current rotation angle in radians.
#                       0 = pointing RIGHT, π/2 = pointing DOWN, etc.
#                       (standard math convention, measured from +x axis)
#   new_angle_rad – the new angle (in radians) the cursor should face.

def rotation_function(raw_dx: float, raw_dy: float,
                      current_angle_rad: float) -> float:
    
    #return math.radians(-5)  

    THRESHOLD = 1.5
    CURSOR_OFFSET = math.radians(-5)
    
    if math.hypot(raw_dx, raw_dy) > THRESHOLD:
        return math.atan2(raw_dy, raw_dx) + math.pi / 2 + CURSOR_OFFSET
    
    return current_angle_rad  # below threshold: keep current angle


CURSOR_PNG_PATH = "aero_arrow.png"
CURSOR_HOTSPOT = (4, 4)   # (x, y) of the cursor tip in the PNG, in pixels
CURSOR_SCALE   = 1.0       # overall size multiplier for the cursor sprite

if __name__ == "__main__":
    run(
        rotation_function=rotation_function,
        cursor_png_path=CURSOR_PNG_PATH,
        cursor_hotspot=CURSOR_HOTSPOT,
        cursor_scale=CURSOR_SCALE,
        num_mazes=3,    # how many maze layouts to complete
        seed=42,        # fixed seed → same mazes for everyone
    )

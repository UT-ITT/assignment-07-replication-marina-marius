# we can throw here all basic constant configs we need for all files that get used in multiple ones
# e.g gesture recognizer and audio input could/shoudl/would be added here
import pyglet
from pyglet.gl import GL_NEAREST

# pixel art tiles are small (e.g. 16x16) and get scaled up
# without they would look blurry (pyglet/OpenGL default to linear filtering)
pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST


pyglet.font.add_file("assets/Play-Regular.ttf")
FONT_NAME = "Play"

WIN_WIDTH = 1280
WIN_HEIGHT = 720
WIN_TITLE = "Insert super duper cool title"
FPS = 60

TILE_SIZE = 64

TEXT_COLOR = (240, 240, 240, 255)
ACCENT_COLOR = (255, 200, 60, 255)

P1_COLOR = (220, 60, 60, 255)  # singer, keyboard WASD
P2_COLOR = (60, 140, 220, 255)  # support, gesture / arrow keys

# put this here since its easier to fine tune later while playtesting
# instead of going into the individual files
# player
PLAYER_MAX_HEALTH = 100
PLAYER_SPEED = 200
PLAYER_HITBOX_SIZE = (48, 48)
PLAYER_INVULN_TIME = 1.0
# enemy
ENEMY_MAX_HEALTH = 60
ENEMY_SPEED = 80
ENEMY_HITBOX_SIZE = (48, 48)
ENEMY_CONTACT_DAMAGE = 10
# shield
SHIELD_MIN_SIZE = 32
SHIELD_MAX_SIZE = 96

# keep order fixed
SHIELD_COLORS = [
    (220, 60, 60, 255),
    (60, 140, 220, 255),
    (80, 200, 120, 255),
    (230, 200, 60, 255),
]
SHIELD_COLOR_NAMES = ["Red", "Blue", "Green", "Yellow"]

# center note per bucket
SHIELD_COLOR_NOTES = ["C", "D#", "F#", "A"]

PITCH_SILENCE_COLOR = (120, 120, 120)

SHIELD_MAX_VOLUME = 0.5
SHIELD_SIZE_GROW_TIME = 3.0

PITCH_LOCK_HOLD_TIME = 2.0

# melody-gate knobs (idea.md's "final gate": sing a short note sequence
# instead of holding one pitch) - length is randomized per gate between
# these two, and singing nothing (or holding one note) for longer than the
# timeout wipes whatever progress was made so far, same idea as the shield
# tune mechanic's sequence timeout above
MELODY_LENGTH_MIN = 2
MELODY_LENGTH_MAX = 4
MELODY_NOTE_TIMEOUT = 2.0

# dungeon combat
ENEMY_WANDER_RADIUS = 120
ENEMY_FIRE_INTERVAL = 2.0
PLAYER_BULLET_SPEED = 200  # P2's own shots - faster than what's coming back at them
ENEMY_BULLET_SPEED = 100
BULLET_RADIUS = 8
PROJECTILE_DISPLAY_SIZE = 32  # sprites are 64x64 source, scaled down to on-screen size
OBSTACLE_SIZE = 40
PLAYER_HEART_COUNT = 3

# health bar (shared object)
# maybe exhcanging later with sprites but no time for that now
HEALTH_BAR_WIDTH = 64
HEALTH_BAR_HEIGHT = 8
HEALTH_BAR_OFFSET_Y = 40
HEALTH_BAR_BG_COLOR = (40, 40, 40, 255)
HEALTH_BAR_BORDER_COLOR = (10, 10, 10, 255)
HEALTH_BAR_FG_COLOR = (80, 200, 120, 255)
HEALTH_BAR_LOW_COLOR = (220, 60, 60, 255)
HEALTH_BAR_LOW_THRESHOLD = 0.25

# we can throw here all basic constant configs we need for all files that get used in multiple ones
# e.g gesture recognizer and audio input could/shoudl/would be added here
import pyglet
from pyglet.gl import GL_NEAREST

# pixel art tiles are small (e.g. 16x16) and get scaled up
# without they would look blurry (pyglet/OpenGL default to linear filtering)
pyglet.image.Texture.default_min_filter = GL_NEAREST
pyglet.image.Texture.default_mag_filter = GL_NEAREST

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
ENEMY_SPEED = 120
ENEMY_HITBOX_SIZE = (48, 48)
ENEMY_CONTACT_DAMAGE = 10
# shield
SHIELD_MAX_HEALTH = 50
SHIELD_MIN_SIZE = 32
SHIELD_MAX_SIZE = 96
SHIELD_DEFAULT_DURATION = 3.0
SHIELD_COLORS = [
    (220, 60, 60, 255),
    (60, 140, 220, 255),
    (80, 200, 120, 255),
    (230, 200, 60, 255),
]
# names in the same order as SHIELD_COLORS, so a target color can be
# announced in text instead of just "go find the right shade yourself"
SHIELD_COLOR_NAMES = ["Red", "Blue", "Green", "Yellow"]
# what a "sing to match this color" object shows while its listening but
# nobody is actually singing right now, instead of just freezing on
# whatever color happened to be sung last
PITCH_SILENCE_COLOR = (120, 120, 120)
# scream this loud (audio_input.current_volume) and you've maxed out the size mechanic
SHIELD_MAX_VOLUME = 0.5
# tune-mechanic knobs, nudge these while playtesting the pitch ladder
SHIELD_TUNE_BOOST = 2.0
SHIELD_TUNE_PENALTY = 1.5
SHIELD_TUNE_SEQUENCE_TIMEOUT = 2.0

# dungeon combat
ENEMY_COUNT_MIN = 3
ENEMY_COUNT_MAX = 10
ENEMY_WANDER_RADIUS = 120
ENEMY_FIRE_INTERVAL = 2.0
BULLET_SPEED = 260
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

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

P1_COLOR = (220, 60, 60, 255) # singer, keyboard WASD
P2_COLOR = (60, 140, 220, 255) # support, gesture / arrow keys

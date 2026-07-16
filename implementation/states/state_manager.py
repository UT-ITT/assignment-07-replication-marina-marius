# holds the current screen (0 to 4) for better screen management
from states.game_stats import GameStats


class StateManager:
    def __init__(self, window):
        self.window = window
        self.states = {}
        self.current = None
        self.stats = GameStats()

    def register(self, name, state):
        self.states[name] = state

    def set_state(self, name, **kwargs):
        if self.current is not None and hasattr(self.current, "on_exit"):
            self.current.on_exit()
        self.current = self.states[name]
        if hasattr(self.current, "on_enter"):
            self.current.on_enter(**kwargs)

    def update(self, dt):
        self.current.on_update(dt) # type: ignore

    def draw(self):
        self.current.on_draw() # type: ignore

    def key_press(self, symbol, modifiers):
        if hasattr(self.current, "on_key_press"):
            self.current.on_key_press(symbol, modifiers) # type: ignore

    def mouse_press(self, x, y, button, modifiers):
        if hasattr(self.current, "on_mouse_press"):
            self.current.on_mouse_press(x, y, button, modifiers) # type: ignore

    def mouse_motion(self, x, y, dx, dy):
        if hasattr(self.current, "on_mouse_motion"):
            self.current.on_mouse_motion(x, y, dx, dy) # type: ignore

    def mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if hasattr(self.current, "on_mouse_drag"):
            self.current.on_mouse_drag(x, y, dx, dy, buttons, modifiers) # type: ignore

    def mouse_release(self, x, y, button, modifiers):
        if hasattr(self.current, "on_mouse_release"):
            self.current.on_mouse_release(x, y, button, modifiers) # type: ignore

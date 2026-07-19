# quick.py
# usage: comment out whichever state is currently active below and
# uncomment the one you actually want, then just run: python quick.py
import time

from input import audio_input
from input import gesture_tracking

import pyglet
import config
from world import music
from states.state_manager import StateManager
from states.state_startmenu import StartMenuState
from states.state_overworld import OverworldState
from states.state_dungeon import DungeonState
from states.state_treasure import TreasureState
from states.state_end import EndState

# pick which state to jump straight into: uncomment others
TARGET_STATE = "start_menu"
# TARGET_STATE = "overworld"
# TARGET_STATE = "dungeon"
# TARGET_STATE = "treasure"
# TARGET_STATE = "end"

window = pyglet.window.Window(config.WIN_WIDTH, config.WIN_HEIGHT, config.WIN_TITLE)
manager = StateManager(window)

manager.register("start_menu", StartMenuState(manager))
manager.register("overworld", OverworldState(manager))
manager.register("dungeon", DungeonState(manager))
manager.register("treasure", TreasureState(manager))
manager.register("end", EndState(manager))


@window.event
def on_draw():
    window.clear()
    manager.draw()


@window.event
def on_key_press(symbol, modifiers):
    manager.key_press(symbol, modifiers)


@window.event
def on_mouse_press(x, y, button, modifiers):
    manager.mouse_press(x, y, button, modifiers)


@window.event
def on_mouse_motion(x, y, dx, dy):
    manager.mouse_motion(x, y, dx, dy)


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    manager.mouse_drag(x, y, dx, dy, buttons, modifiers)


@window.event
def on_mouse_release(x, y, button, modifiers):
    manager.mouse_release(x, y, button, modifiers)


def update(dt):
    manager.update(dt)
    # see main.py's update() for why this has to happen every frame
    if gesture_tracking.activation_requested:
        gesture_tracking.activation_requested = False
        window.activate()


def main():
    print("starting audio stream")
    audio_input.start_audio_stream()

    print("starting gesture tracking")
    video_id = gesture_tracking.select_camera()
    window_x, window_y = window.get_location()
    gesture_tracking.start_tracking(
        screen_width=window.width, screen_height=window.height,
        origin_x=window_x, origin_y=window_y,
        video_id=video_id,
    )

    music.play("assets/sound/8BitSample_Cut.mp3")

    print(f"\njumping straight to '{TARGET_STATE}'")
    print("press ctrl+c to exit\n")

    try:
        manager.set_state(TARGET_STATE)
        pyglet.clock.schedule_interval(update, 1 / config.FPS)
        pyglet.app.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nstopping")
        music.stop()
        audio_input.stop_audio_stream()
        gesture_tracking.stop_tracking()
        time.sleep(0.2)
        print("done")


if __name__ == "__main__":
    main()

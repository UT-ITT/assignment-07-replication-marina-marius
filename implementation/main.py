import cv2
import time
from input import audio_input
from input import gesture_tracking

import pyglet
import config
from states.state_manager import StateManager
from states.state_startmenu import StartMenuState
from states.state_overworld import OverworldState
from states.state_dungeon import DungeonState
from states.state_treasure import TreasureState
from states.state_end import EndState

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


def update(dt):
    manager.update(dt)

    # TODO: once states actually consume these, feed them in here, e.g.
    # freq = audio_input.current_frequency
    # vol = audio_input.current_volume
    # cx, cy = gesture_tracking.cursor_x, gesture_tracking.cursor_y
    # pinch = gesture_tracking.is_pinching

def main():
    # start audio and gesture inputs
    print("starting audio stream")
    audio_input.start_audio_stream()

    print("starting gesture tracking")
    gesture_tracking.start_tracking(show_video=True)

    print("\nstarting main loop")
    print("press ctrl+c to exit\n")

    try:
        manager.set_state("start_menu")
        pyglet.clock.schedule_interval(update, 1 / config.FPS)
        pyglet.app.run()
        """
        while True:
            # break if tracking was stopped (via 'q' or window close)
            if not gesture_tracking.is_tracking:
                break
                
            # get current values from modules
            freq = audio_input.current_frequency
            vol = audio_input.current_volume
            
            cx = gesture_tracking.cursor_x
            cy = gesture_tracking.cursor_y
            pinch = gesture_tracking.is_pinching
            
            # print current states
            print(f"audio: freq={freq:.2f} hz vol={vol:.4f} | gesture: x={cx} y={cy} pinch={pinch}")
            
            time.sleep(0.1)
        """

    except KeyboardInterrupt:
        pass
    finally:
        # stop threads on exit
        print("\nstopping")
        audio_input.stop_audio_stream()
        gesture_tracking.stop_tracking()

        # small delay to let threads close cleanly
        time.sleep(0.2)
        print("done")

if __name__ == "__main__":
    main()

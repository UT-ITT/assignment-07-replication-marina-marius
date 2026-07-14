import cv2
import time
import argparse
from input import audio_input
from input import gesture_tracking
from entities import player_singer

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

debug_window = None
debug_label = None
debug_color = (0, 0, 255)
debug_pitch = 0.0

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


def create_debug_window():
    global debug_window, debug_label

    debug_window = pyglet.window.Window(420, 240, "Pitch Color Debug")
    debug_label = pyglet.text.Label(
        "",
        x=20,
        y=debug_window.height - 24,
        anchor_x="left",
        anchor_y="top",
        color=(255, 255, 255, 255),
    )

    @debug_window.event
    def on_draw():
        debug_window.clear()
        r, g, b = debug_color
        pyglet.shapes.Rectangle(20, 60, 180, 120, color=(r, g, b)).draw()
        debug_label.text = f"pitch: {debug_pitch:.2f} Hz\ncolor: rgb({r}, {g}, {b})"
        debug_label.draw()


def update(dt):
    global debug_color, debug_pitch

    manager.update(dt)
    # TODO: once states actually consume these, feed them in here, e.g.
    # freq = audio_input.current_frequency
    # vol = audio_input.current_volume
    # cx, cy = gesture_tracking.cursor_x, gesture_tracking.cursor_y
    # pinch = gesture_tracking.is_pinching

    # Print out current values for debugging
    # Audio input
    freq = audio_input.current_frequency
    debug_pitch = freq
    debug_color = player_singer.pitch_to_color(freq)
    # Gesture input
    cx = gesture_tracking.cursor_x
    cy = gesture_tracking.cursor_y
    pinch = gesture_tracking.is_pinching
    print(f"gesture: x={cx} y={cy} pinch={pinch}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="show debug windows")
    args = parser.parse_args()

    # start audio and gesture inputs
    print("starting audio stream")
    audio_input.start_audio_stream()

    print("starting gesture tracking")
    video_id = gesture_tracking.select_camera()
    gesture_tracking.start_tracking(show_video=True, video_id=video_id)

    if args.debug:
        create_debug_window()

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
            # print(f"audio: freq={freq:.2f} hz vol={vol:.4f} | gesture: x={cx} y={cy} pinch={pinch}")
            
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

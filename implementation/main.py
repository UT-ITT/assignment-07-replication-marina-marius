import cv2
import time
import audio_input
import gesture_tracking

def main():
    # start audio and gesture inputs
    print("starting audio stream")
    audio_input.start_audio_stream()
    
    print("starting gesture tracking")
    gesture_tracking.start_tracking(show_video=True)
    
    print("\nstarting main loop")
    print("press ctrl+c to exit\n")

    try:
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

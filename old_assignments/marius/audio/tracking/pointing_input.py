import os
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
import time
import urllib.request
import cv2
import mediapipe as mp
import sys
import threading
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pynput.mouse import Controller
from pynput.mouse import Button
from pynput import keyboard


# HAND_CONNECTIONS mapping for drawing connections manually
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Thumb
    (5, 6), (6, 7), (7, 8),                   # Index
    (9, 10), (10, 11), (11, 12),              # Middle
    (13, 14), (14, 15), (15, 16),             # Ring
    (17, 18), (18, 19), (19, 20),             # Pinky
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17) # Palm/Knuckles
]


def download_model():
    model_path = "hand_landmarker.task"
    if not os.path.exists(model_path):
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_path)

def draw_landmarks(frame, hand_landmarks):
    h, w, _ = frame.shape
    # Draw connections
    for start_idx, end_idx in HAND_CONNECTIONS:
        start = hand_landmarks[start_idx]
        end = hand_landmarks[end_idx]
        pt1 = (int(start.x * w), int(start.y * h))
        pt2 = (int(end.x * w), int(end.y * h))
        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
    # Draw joints
    for lm in hand_landmarks:
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)


def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def lerp(start, end, amount):
    return start + (end - start) * amount


def landmark_to_screen(landmark, screen_width, screen_height):
    x = int(clamp(landmark.x, 0.0, 1.0) * screen_width)
    y = int(clamp(landmark.y, 0.0, 1.0) * screen_height)
    return x, y


def interpolate_points(start_point, end_point, steps):
    points = []
    for index in range(1, steps + 1):
        amount = index / steps
        x = int(lerp(start_point[0], end_point[0], amount))
        y = int(lerp(start_point[1], end_point[1], amount))
        points.append((x, y))
    return points


def choose_pointer_landmark(hand_landmarks):
    return hand_landmarks[8]

def click_via_landmark(hand_landmarks, mouse, is_left_pressed, point):
    index_tip = hand_landmarks[8]
    thumb_tip = hand_landmarks[4]
    distance = ((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2) ** 0.5

    pinching = distance < 0.05
    
    if pinching and not is_left_pressed:
        mouse.press(Button.left)
        is_left_pressed = True

    elif pinching and is_left_pressed:
        pass
        
    elif not pinching and is_left_pressed:
        mouse.release(Button.left)
        is_left_pressed = False

    return is_left_pressed

stop_requested = False
active = True

def on_press(key):
    global stop_requested
    try:
        if key.char == "q":
            stop_requested = True
            return False
    except AttributeError:
        pass
    return True

listener = keyboard.Listener(on_press=on_press)
listener.start()

def select_camera():
    print("Scanning for available webcams...")
    available_cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            available_cams.append(i)
            cap.release()
            
    if not available_cams:
        print("No webcams found! Defaulting to 0.")
        return 0
        
    if len(available_cams) == 1:
        print(f"Only one webcam found (Camera {available_cams[0]}). Using it.")
        return available_cams[0]
        
    print("Available webcams:")
    for cam_id in available_cams:
        print(f"  [{cam_id}] Camera {cam_id}")
        
    while True:
        try:
            selection = input(f"Select webcam ID (default {available_cams[0]}): ").strip()
            if not selection:
                return available_cams[0]
            cam_id = int(selection)
            if cam_id in available_cams:
                return cam_id
            else:
                print(f"Invalid selection. Choose from {available_cams}.")
        except ValueError:
            print("Please enter a valid number.")

def hand_loop(show_video=False):
    global active
    print("skript wird ausgeführt")
    screen_width, screen_height = 1920, 1080
    mouse = Controller()

    download_model()

    if len(sys.argv) > 1:
        video_id = int(sys.argv[1])
    else:
        video_id = select_camera()

    capture = None

    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1
    )
    detector = vision.HandLandmarker.create_from_options(options)

    previous_point = None
    last_move_time = time.time()
    start_time = time.time()
    is_left_pressed = False

    while True:
        if not active:
            if capture is not None:
                capture.release()
                capture = None
            time.sleep(0.1)
            continue
            
        if capture is None:
            capture = cv2.VideoCapture(video_id, cv2.CAP_DSHOW)
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
        success, frame = capture.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        frame_timestamp_ms = int((time.time() - start_time) * 1000)
        results = detector.detect_for_video(mp_image, frame_timestamp_ms)

        if results.hand_landmarks:
            hand_landmarks = results.hand_landmarks[0]
            draw_landmarks(frame, hand_landmarks)

            pointer_landmark = choose_pointer_landmark(hand_landmarks)
            current_point = landmark_to_screen(pointer_landmark, screen_width, screen_height)

            if previous_point is None:
                mouse.position = current_point
                previous_point = current_point
            else:
                now = time.time()
                elapsed = now - last_move_time
                last_move_time = now

                steps = max(1, int(elapsed * 60))
                for point in interpolate_points(previous_point, current_point, steps):
                    mouse.position = point

                previous_point = current_point

            # Check for click gesture
            is_left_pressed= click_via_landmark(hand_landmarks, mouse, is_left_pressed, current_point)
        else:
            if is_left_pressed:
                mouse.release(Button.left)
                is_left_pressed = False
            previous_point = None

        if show_video:
            cv2.putText(
                frame,
                "press q to quit",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
            cv2.imshow("pointing input", frame)
            cv2.waitKey(1)
        
        if stop_requested:
            break

    if capture is not None:
        capture.release()
    cv2.destroyAllWindows()
    detector.close()

if __name__ == "__main__":
    import threading
    import recognizer as dr
    
    # Run the hand tracking in a background thread with webcam hidden
    threading.Thread(target=hand_loop, kwargs={"show_video": False}, daemon=True).start()
    
    # Start the gesture recognizer's UI window in the main thread
    dr.main()
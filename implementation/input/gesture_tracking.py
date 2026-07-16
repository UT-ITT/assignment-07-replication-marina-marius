import os
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
import time
import urllib.request
import sys
import cv2
import mediapipe as mp
import threading
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from ctypes import Structure, c_double, c_uint32, c_void_p, cdll


class Button:
    left = "left"


if sys.platform == "darwin":
    _core_graphics = cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")

    class CGPoint(Structure):
        _fields_ = [("x", c_double), ("y", c_double)]

    _core_graphics.CGEventCreateMouseEvent.restype = c_void_p
    _core_graphics.CGEventCreateMouseEvent.argtypes = [c_void_p, c_uint32, CGPoint, c_uint32]
    _core_graphics.CGEventPost.argtypes = [c_uint32, c_void_p]

    class Controller:
        def __init__(self):
            self._position = (0, 0)

        @property
        def position(self):
            return self._position

        @position.setter
        def position(self, value):
            x, y = int(value[0]), int(value[1])
            self._position = (x, y)
            point = CGPoint(x, y)
            event = _core_graphics.CGEventCreateMouseEvent(0, 5, point, 0)
            _core_graphics.CGEventPost(0, event)

        def press(self, button):
            if button == Button.left:
                x, y = self._position
                event = _core_graphics.CGEventCreateMouseEvent(0, 1, CGPoint(x, y), 0)
                _core_graphics.CGEventPost(0, event)

        def release(self, button):
            if button == Button.left:
                x, y = self._position
                event = _core_graphics.CGEventCreateMouseEvent(0, 2, CGPoint(x, y), 0)
                _core_graphics.CGEventPost(0, event)
else:
    class Controller:
        def __init__(self):
            self._position = (0, 0)

        @property
        def position(self):
            return self._position

        @position.setter
        def position(self, value):
            self._position = (int(value[0]), int(value[1]))

        def press(self, button):
            return None

        def release(self, button):
            return None

# global variables for game access
cursor_x = 0
cursor_y = 0
is_pinching = False
is_tracking = False

# hand connections for drawing
hand_connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),           
    (5, 6), (6, 7), (7, 8),                   
    (9, 10), (10, 11), (11, 12),              
    (13, 14), (14, 15), (15, 16),             
    (17, 18), (18, 19), (19, 20),             
    (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
]

def download_model():
    model_path = "hand_landmarker.task"
    if not os.path.exists(model_path):
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        urllib.request.urlretrieve(url, model_path)

def draw_landmarks(frame, hand_landmarks):
    h, w, _ = frame.shape
    # draw connections
    for start_idx, end_idx in hand_connections:
        start = hand_landmarks[start_idx]
        end = hand_landmarks[end_idx]
        pt1 = (int(start.x * w), int(start.y * h))
        pt2 = (int(end.x * w), int(end.y * h))
        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
    # draw joints
    for lm in hand_landmarks:
        cx, cy = int(lm.x * w), int(lm.y * h)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value

def landmark_to_screen(landmark, screen_width, screen_height):
    x = int(clamp(landmark.x, 0.0, 1.0) * screen_width)
    y = int(clamp(landmark.y, 0.0, 1.0) * screen_height)
    return x, y

def lerp(start, end, amount):
    return start + (end - start) * amount

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

def check_pinch(hand_landmarks):
    index_tip = hand_landmarks[8]
    thumb_tip = hand_landmarks[4]
    distance = ((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2) ** 0.5
    return distance < 0.05

def click_via_landmark(hand_landmarks, mouse, is_left_pressed):
    pinching = check_pinch(hand_landmarks)

    if pinching and not is_left_pressed:
        mouse.press(Button.left)
        is_left_pressed = True
    elif not pinching and is_left_pressed:
        mouse.release(Button.left)
        is_left_pressed = False

    return is_left_pressed

def camera_backend():
    if sys.platform == "darwin":
        return cv2.CAP_AVFOUNDATION
    if sys.platform.startswith("win"):
        return cv2.CAP_DSHOW
    return cv2.CAP_ANY

def camera_backends():
    backend = camera_backend()
    if backend == cv2.CAP_ANY:
        return [backend]
    return [backend, cv2.CAP_ANY]

def open_camera(video_id):
    for backend in camera_backends():
        capture = cv2.VideoCapture(video_id, backend)
        if capture.isOpened():
            return capture
        capture.release()
    return cv2.VideoCapture(video_id)

def select_camera():
    # used to scan cams 0-2 (opening + releasing each one) and then open the
    # chosen one AGAIN just to confirm it works, before hand_loop() opens it
    # a third time for real, opencv has no cheap "does this index exist"
    # query, so that was 3+ real AVFoundation session opens back to back,
    # which is exactly what made the webcam refuse to start at all sometimes
    # (see bugs.md). now we just ask, and let hand_loop() single open_camera()
    # call be the only time the camera hardware actually gets touched
    selection = input("select webcam id [0] ").strip()
    if not selection:
        return 0
    try:
        return int(selection)
    except ValueError:
        return 0

def hand_loop(screen_width=1920, screen_height=1080, origin_x=0, origin_y=0, show_video=False, video_id=None):
    global cursor_x, cursor_y, is_pinching, is_tracking

    download_model()
    if video_id is None:
        video_id = select_camera()

    mouse = Controller()
    
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1
    )
    detector = vision.HandLandmarker.create_from_options(options)
    
    capture = open_camera(video_id)
    if not capture.isOpened():
        print(f"failed to open camera {video_id}")
        is_tracking = False
        detector.close()
        return

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start_time = time.time()
    previous_point = None
    last_move_time = time.time()
    is_left_pressed = False
    
    while is_tracking:
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
            
            if show_video:
                draw_landmarks(frame, hand_landmarks)

            # update cursor position (window-relative, for anything that wants to read it)
            pointer_landmark = choose_pointer_landmark(hand_landmarks)
            cx, cy = landmark_to_screen(pointer_landmark, screen_width, screen_height)
            cursor_x = cx
            cursor_y = cy

            # the real OS cursor needs *global* desktop coordinates though,
            # so the window on-screen position gets added back in here
            # otherwise clicks land wherever (0, 0) happens to be instead of
            # actually on the game window (see bugs.md, this one was a doozy)
            current_point = (origin_x + cx, origin_y + cy)
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
            
            # update pinch state
            is_pinching = check_pinch(hand_landmarks)
            is_left_pressed = click_via_landmark(hand_landmarks, mouse, is_left_pressed)
        else:
            # reset pinch when no hands detected
            is_pinching = False
            if is_left_pressed:
                mouse.release(Button.left)
                is_left_pressed = False
            previous_point = None

        if show_video:
            try:
                cv2.imshow("pointing input", frame)

                # quit on q key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    is_tracking = False
                    break

                # quit on window close
                if cv2.getWindowProperty("pointing input", cv2.WND_PROP_VISIBLE) < 1:
                    is_tracking = False
                    break
            except cv2.error:
                print("video preview disabled because OpenCV windowing is unavailable")
                show_video = False
            
    capture.release()
    if show_video:
        cv2.destroyAllWindows()
    detector.close()

def start_tracking(screen_width=1920, screen_height=1080, origin_x=0, origin_y=0, show_video=False, video_id=None):
    global is_tracking
    is_tracking = True

    # run hand tracking in background thread
    thread = threading.Thread(
        target=hand_loop,
        kwargs={
            "screen_width": screen_width, "screen_height": screen_height,
            "origin_x": origin_x, "origin_y": origin_y,
            "show_video": show_video, "video_id": video_id,
        },
        daemon=True
    )
    thread.start()

def stop_tracking():
    global is_tracking
    # stop the hand tracking loop
    is_tracking = False
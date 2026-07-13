import os
os.environ['OPENCV_LOG_LEVEL'] = 'SILENT'
import time
import urllib.request
import cv2
import mediapipe as mp
import threading
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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

def check_pinch(hand_landmarks):
    index_tip = hand_landmarks[8]
    thumb_tip = hand_landmarks[4]
    distance = ((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2) ** 0.5
    return distance < 0.05

def select_camera():
    # scan for available webcams
    print("scanning for webcams")
    available_cams = []
    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            available_cams.append(i)
            cap.release()
            
    if not available_cams:
        print("no webcams found")
        return 0
        
    if len(available_cams) == 1:
        print(f"using camera {available_cams[0]}")
        return available_cams[0]
        
    # show available webcams
    for cam_id in available_cams:
        print(f"[{cam_id}] camera {cam_id}")
        
    while True:
        try:
            selection = input(f"select webcam id ").strip()
            if not selection:
                return available_cams[0]
            cam_id = int(selection)
            if cam_id in available_cams:
                return cam_id
        except ValueError:
            pass

def hand_loop(screen_width=1920, screen_height=1080, show_video=False):
    global cursor_x, cursor_y, is_pinching, is_tracking
    
    download_model()
    video_id = select_camera()
    
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1
    )
    detector = vision.HandLandmarker.create_from_options(options)
    
    capture = cv2.VideoCapture(video_id, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    start_time = time.time()
    
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

            # update cursor position
            pointer_landmark = hand_landmarks[8]
            cx, cy = landmark_to_screen(pointer_landmark, screen_width, screen_height)
            cursor_x = cx
            cursor_y = cy
            
            # update pinch state
            is_pinching = check_pinch(hand_landmarks)
        else:
            # reset pinch when no hands detected
            is_pinching = False

        if show_video:
            cv2.imshow("pointing input", frame)
            
            # quit on q key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                is_tracking = False
                break
                
            # quit on window close
            if cv2.getWindowProperty("pointing input", cv2.WND_PROP_VISIBLE) < 1:
                is_tracking = False
                break
            
    capture.release()
    if show_video:
        cv2.destroyAllWindows()
    detector.close()

def start_tracking(screen_width=1920, screen_height=1080, show_video=False):
    global is_tracking
    is_tracking = True
    
    # run hand tracking in background thread
    thread = threading.Thread(
        target=hand_loop, 
        kwargs={"screen_width": screen_width, "screen_height": screen_height, "show_video": show_video}, 
        daemon=True
    )
    thread.start()

def stop_tracking():
    global is_tracking
    # stop the hand tracking loop
    is_tracking = False
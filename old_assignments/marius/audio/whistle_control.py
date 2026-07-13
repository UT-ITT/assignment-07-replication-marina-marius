import numpy as np
import sounddevice as sd
import queue
from pynput.keyboard import Key, Controller

CHUNK_SIZE = 1024 
RATE = 44100 
CHANNELS = 1
THRESHOLD = 0.1
MIN_FREQ = 500
HIGH_FREQ = 3000

# init keyboard
keyboard = Controller()

frequency_list = []

print("Available input devices:\n")
devices = sd.query_devices()

input_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        print(f"{i}: {dev['name']}")
        input_devices.append(i)

input_device = int(input("\nSelect input device: "))

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata[:, 0].copy())

stream = sd.InputStream(
    device=input_device,
    channels=CHANNELS,
    samplerate=RATE,
    blocksize=CHUNK_SIZE,
    callback=audio_callback,
    latency='low'
)

with stream:
    print("\nStreaming... (Ctrl+C to stop)")
    try:
        while True:
            # get audio data from queue
            data = audio_queue.get()
            volume = np.max(np.abs(data))
            
            if volume > THRESHOLD:
                # apply window to audio data
                window = np.hanning(len(data))
                windowed_data = data * window
                
                # perform fast fourier transform
                fft_result = np.fft.rfft(windowed_data)
                magnitudes = np.abs(fft_result)
                frequencies = np.fft.rfftfreq(1024, 1.0/44100)
                
                # ignore frequencies outside valid range
                valid_mask = (frequencies >= MIN_FREQ) & (frequencies <= HIGH_FREQ)
                magnitudes[~valid_mask] = 0
                
                # get the actual peak frequency
                peak_index = np.argmax(magnitudes)
                peak_frequency = frequencies[peak_index]
                
                # save frequency to the list
                frequency_list.append(peak_frequency)
                
            else:
                # process when whistling stops
                if len(frequency_list) > 9:
                    # calculate difference between start and end
                    diff = frequency_list[0] - frequency_list [-1]
                    
                    if diff > 100:
                        # detect decreasing pitch whistle
                        print("High Whistel!")
                        keyboard.press(Key.down)
                        keyboard.release(Key.down)
                    elif diff < -100:
                        # detect increasing pitch whistle
                        print("Low Whistle!")
                        keyboard.press(Key.up)
                        keyboard.release(Key.up)
                        
                # reset list for next whistle
                frequency_list.clear()

    except KeyboardInterrupt:
        print("\nStream beendet.")
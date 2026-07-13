import numpy as np
import sounddevice as sd
import queue
import threading

chunk_size = 1024 
rate = 44100 
channels = 1
threshold = 0.1
min_freq = 500
high_freq = 3000

# global variables for game access
current_frequency = 0.0
current_volume = 0.0
is_running = False

audio_queue = queue.Queue()

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata[:, 0].copy())

def start_audio_stream():
    global is_running
    
    # print available input devices
    print("available input devices\n")
    devices = sd.query_devices()
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i} {dev['name']}")
            
    # get input device from user
    input_device = int(input("\nselect input device "))
    
    stream = sd.InputStream(
        device=input_device,
        channels=channels,
        samplerate=rate,
        blocksize=chunk_size,
        callback=audio_callback,
        latency='low'
    )
    
    is_running = True
    
    def process_audio():
        global current_frequency, current_volume
        
        with stream:
            print("\nstreaming")
            while is_running:
                # get audio data from queue
                data = audio_queue.get()
                volume = np.max(np.abs(data))
                current_volume = volume
                
                if volume > threshold:
                    # apply window to audio data
                    window = np.hanning(len(data))
                    windowed_data = data * window
                    
                    # perform fast fourier transform
                    fft_result = np.fft.rfft(windowed_data)
                    magnitudes = np.abs(fft_result)
                    frequencies = np.fft.rfftfreq(1024, 1.0/44100)
                    
                    # ignore frequencies outside valid range
                    valid_mask = (frequencies >= min_freq) & (frequencies <= high_freq)
                    magnitudes[~valid_mask] = 0
                    
                    # get the actual peak frequency
                    peak_index = np.argmax(magnitudes)
                    peak_frequency = frequencies[peak_index]
                    
                    # update current frequency
                    current_frequency = peak_frequency
                else:
                    # reset frequency when quiet
                    current_frequency = 0.0
                    
    # run audio processing in background thread
    thread = threading.Thread(target=process_audio, daemon=True)
    thread.start()

def stop_audio_stream():
    global is_running
    # stop the audio stream
    is_running = False

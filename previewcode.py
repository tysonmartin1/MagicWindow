import cv2
import numpy as np
from pynput import keyboard
import pyaudio
import threading

# Flags for camera and talk mode
show_camera = False
talk_mode = False

# Audio stream variables
chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
p = pyaudio.PyAudio()
stream = None

def start_audio_stream():
    global stream
    stream = p.open(format=sample_format, channels=channels, rate=fs, 
                    frames_per_buffer=chunk, input=True, output=True)

def stop_audio_stream():
    global stream
    if stream:
        stream.stop_stream()
        stream.close()
    stream = None

def audio_thread():
    while talk_mode:
        data = stream.read(chunk)
        stream.write(data, chunk)

def on_press(key):

    global show_camera, talk_mode
    # When the motion sensor is active turn show_camera to true 
    if key == keyboard.KeyCode.from_char('k'):
        show_camera = not show_camera 

    # If screen is on check for talk button 
    elif key == keyboard.KeyCode.from_char('t'):
        # Turn on microphone and speaker
        talk_mode = not talk_mode
        if talk_mode:
            print("Talk mode ON")
            start_audio_stream()
            threading.Thread(target=audio_thread).start()
        else:
            print("Talk mode OFF")
            stop_audio_stream()

# Set up keyboard listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Set up camera capture
cap = cv2.VideoCapture(0)

# Black frame for when camera is off
black_frame = np.zeros((480, 640, 3), dtype=np.uint8)

while True:
    if show_camera:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Door Camera', frame)
    else:
        cv2.imshow('Door Camera', black_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
p.terminate()
listener.stop()

import cv2
import pyaudio
import wave
import threading
import keyboard
import numpy as np

cap = cv2.VideoCapture(0)
display_camera = False
def handle_camera():
    global display_camera
    window_created = False 
    while True:
        if display_camera:
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Camera', frame)
                window_created = True  
            if cv2.waitKey(1) & 0xFF == ord('q'):  
                break
        else:
            if window_created:  
                cv2.destroyWindow('Camera')
                window_created = False  

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
audio = pyaudio.PyAudio()
stream_play = None
stream_record = None
audio_streaming = False
def toggle_audio_streaming():
    global audio_streaming, stream_play, stream_record
    if audio_streaming:
        stream_record.stop_stream()
        stream_record.close()
        stream_play.stop_stream()
        stream_play.close()
        audio_streaming = False
    else:
        input_device_index = 1 
        output_device_index = 8  
        input_channels = 1 
        output_channels = 2  
        try:
            stream_record = audio.open(format=FORMAT, channels=input_channels,
                                       rate=RATE, input=True,
                                       frames_per_buffer=CHUNK, input_device_index=input_device_index)
            stream_play = audio.open(format=FORMAT, channels=output_channels,
                                     rate=RATE, output=True,
                                     frames_per_buffer=CHUNK, output_device_index=output_device_index)
            audio_streaming = True
            threading.Thread(target=stream_audio).start()
        except OSError as e:
            print(f"Failed to open audio streams: {e}")

def stream_audio():
    while audio_streaming:
        data = stream_record.read(CHUNK)
        stream_play.write(data, CHUNK)
def on_key_event(event):
    global display_camera
    if event.name == 'k':
        display_camera = not display_camera
    elif event.name == 't':
        toggle_audio_streaming()
keyboard.on_press(on_key_event)
threading.Thread(target=handle_camera, daemon=True).start()
keyboard.wait('q')
cap.release()
cv2.destroyAllWindows()
if audio_streaming:
    toggle_audio_streaming()
audio.terminate()

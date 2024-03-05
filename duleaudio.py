import cv2
import pyaudio
import wave
import threading
import keyboard
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0) #Camera 0 is the default camera

# Flag to control the display of the camera feed
display_camera = False #Iniltialized to camera off when app is run

# Function to handle camera display
def handle_camera():
    global display_camera 
    window_created = False  # Track if the camera window is open
    while True:
        if display_camera:
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Camera', frame)
                window_created = True  # Mark that the window is now created
            if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit on 'q'
                break
        else:
            if window_created:  # Only destroy the window if it was created
                cv2.destroyWindow('Camera')
                window_created = False  # Reset the flag as the window is now destroyed


# Audio handling
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100

audio = pyaudio.PyAudio()

# Stream for playing audio
stream_play = None

# Stream for recording audio
stream_record = None

# Flag to control audio streaming
audio_streaming = False

# Function to toggle audio streaming
def toggle_audio_streaming():
    global audio_streaming, stream_play, stream_record
    if audio_streaming:
        stream_record.stop_stream()
        stream_record.close()
        stream_play.stop_stream()
        stream_play.close()
        audio_streaming = False
    else:
        # Use the device index for Echo Cancelling Speakerphone (Input)
        input_device_index = 4  # or 16, depending on which one works for you
        # Use the device index for Speakers (Realtek(R) Audio) (Output)
        output_device_index = 7  # Adjust if necessary based on your setup

        # Set the number of channels based on device capabilities
        input_channels = 1  # Echo Cancelling Speakerphone supports 1 input channel
        output_channels = 2  # Speakers (Realtek(R) Audio) support 2 output channels

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
            # Handle failure (e.g., by choosing different devices or settings)



# Function to stream audio
def stream_audio():
    while audio_streaming:
        data = stream_record.read(CHUNK)
        stream_play.write(data, CHUNK)

# Keyboard event handling
def on_key_event(event):
    global display_camera
    if event.name == 'k':
        display_camera = not display_camera
    elif event.name == 't':
        toggle_audio_streaming()

keyboard.on_press(on_key_event)

# Start camera handling in a separate thread
threading.Thread(target=handle_camera, daemon=True).start()

print("Press 'k' to toggle the camera display, 't' to toggle audio streaming, and 'q' to quit.")

keyboard.wait('q')  # Wait until 'q' is pressed to quit

# Cleanup
cap.release()
cv2.destroyAllWindows()
if audio_streaming:
    toggle_audio_streaming()
audio.terminate()

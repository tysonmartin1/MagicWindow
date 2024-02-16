import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

try:
    while True:
        if GPIO.input(17) == GPIO.LOW:  
            print("Button was pushed!")
        time.sleep(0.1)  
finally:
    GPIO.cleanup()  

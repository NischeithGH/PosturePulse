import RPi.GPIO as GPIO
import time

BUTTON_PIN = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Button test started")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            print("BUTTON PRESSED")
            time.sleep(0.3)

except KeyboardInterrupt:
    GPIO.cleanup()

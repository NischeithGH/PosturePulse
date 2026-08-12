from hardware.ultrasonic import UltrasonicSensor
import time

sensor = UltrasonicSensor(
    trig_pin=14,
    echo_pin=15,
)

while True:
    distance = sensor.get_distance()

    print(f"Distance: {distance} cm")

    time.sleep(0.5)
from __future__ import annotations

import time

from hardware.gpio_compat import GPIO


class UltrasonicSensor:
    def __init__(self, trig_pin: int, echo_pin: int):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

        GPIO.output(self.trig_pin, GPIO.LOW)

        time.sleep(2)

    def get_distance(self) -> float:
        # Send pulse
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        pulse_start = time.time()
        pulse_end = time.time()

        timeout = time.time()

        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()

            if time.time() - timeout > 0.05:
                return 999

        timeout = time.time()

        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()

            if time.time() - timeout > 0.05:
                return 999

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150

        return round(distance, 2)

    def human_detected(self, max_distance: float = 50.0) -> bool:
        distance = self.get_distance()

        print(f"Distance: {distance} cm")

        return distance <= max_distance

    def is_present(self, threshold_cm: float = 80.0) -> bool:
        return self.human_detected(threshold_cm)
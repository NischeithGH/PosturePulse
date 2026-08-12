from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from hardware.gpio import GpioPlatform

logger = logging.getLogger("rgb_led")


class LEDColor(Enum):
    OFF = "off"
    GREEN = "green"
    BLUE = "blue"
    RED = "red"


class RGBLEDService:
    def __init__(
        self,
        green_pin: int = 6,
        blue_pin: int = 13,
        red_pin: int = 5,
        gpio: Optional[GpioPlatform] = None,
    ) -> None:
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.red_pin = red_pin
        self._gpio = gpio
        self.enabled = False

        self._init_leds()

    def _init_leds(self) -> None:
        try:
            from hardware.gpio_compat import GPIO

            if self._gpio is not None:
                self._gpio.setup_output_low(self.green_pin)
                self._gpio.setup_output_low(self.blue_pin)
                self._gpio.setup_output_low(self.red_pin)
            else:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.green_pin, GPIO.OUT)
                GPIO.setup(self.blue_pin, GPIO.OUT)
                GPIO.setup(self.red_pin, GPIO.OUT)

                GPIO.output(self.green_pin, GPIO.HIGH)
                GPIO.output(self.blue_pin, GPIO.HIGH)
                GPIO.output(self.red_pin, GPIO.HIGH)

            self.enabled = True
            logger.info("RGB LED initialized successfully")

            # System ready
            self.set_color(LEDColor.GREEN)

        except Exception as exc:
            logger.error(f"Failed to initialize RGB LED: {exc}")
            self.enabled = False

    def set_color(self, color: LEDColor) -> None:
        from hardware.gpio_compat import GPIO

        if not self.enabled:
            return

        try:
            green_state = GPIO.HIGH
            blue_state = GPIO.HIGH
            red_state = GPIO.HIGH

            if color == LEDColor.GREEN:
                green_state = GPIO.LOW
            elif color == LEDColor.BLUE:
                blue_state = GPIO.LOW
            elif color == LEDColor.RED:
                red_state = GPIO.LOW

            GPIO.output(self.green_pin, green_state)
            GPIO.output(self.blue_pin, blue_state)
            GPIO.output(self.red_pin, red_state)

            logger.debug(f"RGB LED set to {color.value}")

        except Exception as exc:
            logger.error(f"Failed to set RGB LED color: {exc}")

    def set_ready(self) -> None:
        self.set_color(LEDColor.GREEN)

    def set_active(self) -> None:
        self.set_color(LEDColor.BLUE)

    def set_error(self) -> None:
        self.set_color(LEDColor.RED)

    def set_off(self) -> None:
        self.set_color(LEDColor.OFF)

    def cleanup(self) -> None:
        if self.enabled:
            self.set_off()

            if self._gpio is None:
                from hardware.gpio_compat import GPIO

                GPIO.cleanup()
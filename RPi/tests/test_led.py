from hardware.led import RGBLEDService, LEDColor

led = RGBLEDService(
    green_pin=13,
    blue_pin=5,
    red_pin=6,
)

input("GREEN")
led.set_ready()

input("BLUE")
led.set_active()

input("RED")
led.set_error()
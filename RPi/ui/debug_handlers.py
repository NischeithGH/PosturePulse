from __future__ import annotations

import socket

from hardware.ultrasonic import UltrasonicSensor
from ui.context import AppContext


class DebugHandlers:
    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        try:
            self.ultrasonic = UltrasonicSensor(
                trig_pin=14,
                echo_pin=15,
            )
        except Exception:
            self.ultrasonic = None

    def test_green_led(self):
        try:
            if self.ctx.led is None:
                return "❌ LED not available (is None)"            
            if not self.ctx.led.enabled:
                return "❌ LED disabled - GPIO init failed"
            self.ctx.led.set_ready()
            return "✅ Green LED test successful"
        except Exception as exc:
            
            return f"❌ Green LED Error: {exc}"

    def test_blue_led(self):
        try:
            if self.ctx.led is None:
                return "❌ LED not available (is None)"        
            if not self.ctx.led.enabled:
                return "❌ LED disabled - GPIO init failed"
            
            self.ctx.led.set_active()
            return "✅ Blue LED test successful"
        except Exception as exc:
            return f"❌ Blue LED Error: {exc}"

    def test_red_led(self):
        try:
            if self.ctx.led is None:
                return "❌ LED not available"

            self.ctx.led.set_error()
            return "✅ Red LED test successful"
        except Exception as exc:
            return f"❌ Red LED Error: {exc}"

    def buzzer_test(self):
        if self.ctx.buzzer is None:
            return "❌ Buzzer not available"

        self.ctx.buzzer.play("success")

        return "✅ Buzzer test successful"

    def lcd_test(self, message: str):
        if self.ctx.lcd is None:
            return "❌ LCD not available"

        try:
            # Split message into 2 lines if longer, or pad to 2 lines
            lines = message.split('\n') if '\n' in message else [message, ""]
            if len(lines) == 1:
                lines.append("")
            
            self.ctx.lcd.show_lines(
                lines[0][:20],  # Limit to 20 chars per line
                lines[1][:20],
                force=True,
            )

            return f"✅ LCD displayed: {message}"
        except Exception as exc:
            return f"❌ LCD Error: {exc}"

    def ultrasonic_test(self):
        if self.ultrasonic is None:
            return "❌ Ultrasonic sensor unavailable"

        try:
            distance = self.ultrasonic.get_distance()

            return f"📏 Distance: {distance:.2f} cm"

        except Exception as exc:
            return f"❌ Sensor Error: {exc}"

    def pi_info(self):
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)

            try:
                with open(
                    "/sys/class/thermal/thermal_zone0/temp"
                ) as f:
                    temp = f"{float(f.read()) / 1000:.1f} °C"
            except Exception:
                temp = "Unavailable"

            markdown = f"""
🌡 CPU Temperature: {temp}

🌐 IP Address: {ip}

💻 Hostname: {hostname}
"""
            return markdown

        except Exception as exc:
            return f"❌ Error: {exc}"

    def diagnostics_test(self):
        """Run all hardware diagnostics and return results"""
        
        results = []
        

        green_result = self.test_green_led()
        results.append(f"🟢 Green LED: {green_result}")
        

        blue_result = self.test_blue_led()
        results.append(f"🔵 Blue LED: {blue_result}")
        

        red_result = self.test_red_led()
        results.append(f"🔴 Red LED: {red_result}")

        buzzer_result = self.buzzer_test()
        results.append(f"🔊 Buzzer: {buzzer_result}")
        

        lcd_result = self.lcd_test("Test Successful")
        results.append(f"📟 LCD: {lcd_result}")
        

        ultrasonic_result = self.ultrasonic_test()
        results.append(f"📏 Ultrasonic: {ultrasonic_result}")
        
        return "\n\n".join(results)
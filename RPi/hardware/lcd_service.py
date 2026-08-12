from __future__ import annotations
 
import threading
import time
import traceback
from typing import Optional

try:
    import smbus  # type: ignore
except Exception:  # pragma: no cover
    try:
        import smbus2 as smbus  # type: ignore
    except Exception:  # pragma: no cover
        smbus = None
 
 
class I2CLCD:
    LCD_CHR = 1
    LCD_CMD = 0
    LINE_1 = 0x80
    LINE_2 = 0xC0
    BACKLIGHT_ON = 0x08
    ENABLE = 0b00000100
    E_PULSE = 0.0005
    E_DELAY = 0.0005
 
    def __init__(self, addr: int = 0x27, bus: int = 1, width: int = 20) -> None:
        if smbus is None:
            raise RuntimeError("smbus/smbus2 not available")
        self.addr = addr
        self.bus = smbus.SMBus(bus)
        self.width = width
        self.backlight_state = self.BACKLIGHT_ON
        self._init_lcd()
 
    def _init_lcd(self) -> None:
        self._toggle_enable(0x30)
        self._toggle_enable(0x30)
        self._toggle_enable(0x30)
        self._toggle_enable(0x20)
        self.send_command(0x28)
        self.send_command(0x0C)
        self.send_command(0x06)
        self.clear()
 
    def _toggle_enable(self, bits: int) -> None:
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.addr, bits | self.ENABLE)
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.addr, bits & ~self.ENABLE)
        time.sleep(self.E_DELAY)
 
    def _send_byte(self, bits: int, mode: int) -> None:
        hi = mode | (bits & 0xF0) | self.backlight_state
        lo = mode | ((bits << 4) & 0xF0) | self.backlight_state
        self._toggle_enable(hi)
        self._toggle_enable(lo)
 
    def send_command(self, cmd: int) -> None:
        self._send_byte(cmd, self.LCD_CMD)
 
    def clear(self) -> None:
        self.send_command(0x01)
        self.send_command(0x02)
        time.sleep(0.002)
 
    def message(self, text: str, line: int) -> None:
        self.send_command(self.LINE_1 if line == 1 else self.LINE_2)
 
        padded = text.ljust(self.width, " ")[: self.width]
 
        for char in padded:
            self._send_byte(ord(char), self.LCD_CHR)
    
    def backlight_off(self) -> None:
        self.backlight_state = 0x00
        self.bus.write_byte(self.addr, 0x00)

class LCDService:
    def __init__(
        self,
        addr: int,
        bus: int,
        width: int = 20,
        min_update_interval: float = 0.15,
    ) -> None:
        self.width = width
        self.min_update_interval = min_update_interval
        self._lock = threading.Lock()
        self._last_update_ts = 0.0
        self._lcd: Optional[I2CLCD] = None
        self.enabled = False
        self._last_line1 = ""
        self._last_line2 = ""
 
        try:
            self._lcd = I2CLCD(addr=addr, bus=bus, width=width)
            self.enabled = True
            print(f"[LCD] Successfully initialized at address {hex(addr)} on i2c bus {bus}")
        except Exception as exc:
            print(f"[LCD] Failed to initialize at address {hex(addr)} on i2c bus {bus}: {exc}")
            traceback.print_exc()
            print("[LCD] Disabled")
 
    def _normalize(self, text: str) -> str:
        return text[: self.width].ljust(self.width, " ")
 
    def show_lines(self, line1: str, line2: str, force: bool = False) -> None:
        if not self.enabled or self._lcd is None:
            return
        now = time.time()
        if not force and (now - self._last_update_ts) < self.min_update_interval:
            return
        if (
            not force
            and line1 == self._last_line1
            and line2 == self._last_line2
            ):
            return
        with self._lock:
            self._lcd.message(self._normalize(line1), line=1)
            self._lcd.message(self._normalize(line2), line=2)
            self._last_line1 = line1
            self._last_line2 = line2
            self._last_update_ts = time.time()
 
    def show_startup_ip(self, lan_ip: str, wifi_ip: str) -> None:
        self.show_lines(f"LAN:{lan_ip}", f"WIFI:{wifi_ip}", force=True)
 
    def show_waiting(self) -> None:
        self.show_lines("Posture Pulse", "System Ready")
 
    def show_processing(self, mode: str) -> None:
        self.show_lines("Monitoring",mode)
 
    def show_result(self, result_text: str) -> None:
        self.show_lines("Posture Status", result_text)
 
    def show_mute(self, muted: bool) -> None:
        self.show_lines("Audio", "Muted" if muted else "Unmuted")
 
    def show_shutdown(self) -> None:
        self.show_lines("Shutdown requested", "Powering off...", force=True)
 
    def show_error(self, message: str) -> None:
        self.show_lines("AI error", message[: self.width], force=True)
        
    def clear(self) -> None:
        if not self.enabled or self._lcd is None:
            return

        with self._lock:
            self._lcd.clear()
            self._last_line1 = ""
            self._last_line2 = ""
    
    def backlight_off(self) -> None:
        if not self.enabled or self._lcd is None:
            return

        self._lcd.backlight_off()
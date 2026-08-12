from models.registry import MODEL_POSE
import time

import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"


class PostureService:

    def __init__(self, ctx):
        self.ctx = ctx
        self.current_session_id = None
        self.last_saved_posture = None
        self.last_presence_time = None
        self.posture_map = {
    "good_posture": 1,
    "slouching": 2,
    "looking_down": 3,
    "looking_up": 4,
    "leaning_forward": 5,
    "leaning_sideways": 6,
}
        self.last_session_end_time = None
        self.session_start_time = None

    def process_frame(self, frame_rgb):

        result = self.ctx.models[MODEL_POSE].run(
            frame_rgb
        )

        lm_count = int(
            result.payload.get(
                "landmark_count",
                0
            )
        )

        posture = result.payload.get(
            "posture",
            "Unknown"
        )

        confidence = result.payload.get(
            "confidence",
            0.0
        )

        self.handle_monitoring(
            posture,
            confidence,
            lm_count,
        )

        return (
            result,
            posture,
            confidence,
            lm_count,
        )

    def handle_monitoring(
        self,
        posture,
        confidence,
        lm_count,
    ):

        if not self.ctx.monitoring_enabled:
            return

        sensor = self.ctx.ultrasonic

        if sensor is None:
            raise RuntimeError(
                "Ultrasonic sensor not initialized"
            )

        ultrasonic_detected = sensor.human_detected(
            max_distance=110
        )

        camera_detected = (
            lm_count > 0
            and posture != "No Person"
        )

        if self.current_session_id is None:
            person_near = (
                ultrasonic_detected
                and camera_detected
            )
        else:
            person_near = ultrasonic_detected

        print(
            "PERSON NEAR =",
            person_near,
        )

        print(
            "LAST PRESENCE =",
            self.last_presence_time,
        )

        if person_near:

            self.last_presence_time = time.time()

            if self.current_session_id is None:

                if (
                    self.last_session_end_time is not None
                    and time.time() - self.last_session_end_time < 10
                ):
                    return

                self.current_session_id = (
                    self.start_db_session()
                )
                self.session_start_time = time.time()

                self.ctx.lcd.show_lines(
                    "Session",
                    "Started",
                    force=True,
                )
                time.sleep(2)

                print(
                    "Started Session",
                    self.current_session_id,
                )

        else:

            if (
                self.last_presence_time
                is not None
            ):

                absent_seconds = (
                    time.time()
                    - self.last_presence_time
                )

                if absent_seconds >= 15:

                    print(
                        "Ended Session",
                        self.current_session_id,
                    )

                    self.end_db_session()
                    self.session_start_time = None

                    self.ctx.lcd.show_lines(
                        "Session",
                        "Ended",
                        force=True,
                    )

                    self.last_session_end_time = time.time()

                    self.current_session_id = None

                    self.last_presence_time = None


        if self.current_session_id is not None:

            if posture == "No Person":
                self.update_led(None)
            elif posture == "good_posture":
                self.update_led(posture)
            else:
                self.update_led(posture)

            if (
                posture != "good_posture"
                and posture != "No Person"
            ):
                if self.ctx.buzzer is not None:
                    self.ctx.buzzer.play_cooldown(
                        "error",
                        "bad_posture",
                        3.0,
                        target="passive",
                    )

            if lm_count == 0:
                self.ctx.lcd.show_result(
                    "No person"
                )
            else:
                self.ctx.lcd.show_result(
                    posture
                )

        else:

            self.ctx.lcd.show_result(
                "Waiting User"
            )

        if (
            self.current_session_id is not None
            and person_near
            and posture != "No Person"
            and posture != self.last_saved_posture
        ):

            self.save_posture_event(
                posture,
                confidence,
                person_near,
            )

            self.last_saved_posture = posture

            print(
                "Saved posture:",
                posture,
            )
            
    def update_led(self, posture_class: str | None) -> None:
        if self.ctx.led is None:
            return

        if posture_class is None:
            self.ctx.led.set_active()  # Blue = no person

        elif posture_class == "good_posture":
            self.ctx.led.set_ready()  # Green

        else:
            self.ctx.led.set_error()  # Red
            
    def start_db_session(self):
        response = requests.post(
            f"{API_URL}/sessions/start"
        )

        response.raise_for_status()

        self.session_start_time = time.time()

        return response.json()["session_id"]
 
 
    def end_db_session(self):
        if self.current_session_id is None:
            return
        
        print("ENDING SESSION:", self.current_session_id)
        
        requests.put(f"{API_URL}/sessions/{self.current_session_id}/end")
        self.current_session_id = None
        self.session_start_time = None
        self.last_saved_posture = None
    

    def save_posture_event(self,posture: str,confidence: float,person_near):
        if self.current_session_id is None:
            return
        
        posture_id = self.posture_map.get(posture)
        
        if posture_id is None:
            return
        
        response = requests.post(f"{API_URL}/posture-events/",
            json={
                "session_id": self.current_session_id,
                "posture_id": posture_id,
                "detected_at": (
                    datetime.utcnow()
                    .isoformat()
                ),
                "confidence": confidence,
                "sensor_presence": person_near,
                "alert_triggered": (
                    posture != "good_posture"
                ),
            },
        )
        response.raise_for_status()
        
    def get_session_duration(self):

        if self.session_start_time is None:
            return "00:00:00"

        elapsed = int(
            time.time() - self.session_start_time
        )

        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60

        return (
            f"{hours:02}:"
            f"{minutes:02}:"
            f"{seconds:02}"
        )
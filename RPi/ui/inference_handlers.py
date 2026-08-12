from __future__ import annotations

import threading
import time
from typing import Any

import requests
from datetime import datetime
import gradio as gr
import numpy as np

from hardware.network import request_sudo_poweroff
from inputs import pick_source_frame
from models.registry import MODEL_POSE
from ui.constants import ERROR_DELETE_BUTTON_SLOTS
from ui.context import AppContext
from ui.history import HistoryStore, render_history_accordion

from hardware.ultrasonic import UltrasonicSensor
API_URL = "http://127.0.0.1:8000"
from services.posture_service import PostureService
from services.monitoring_service import MonitoringService

# Must match gpio_timer.tick outputs in ui/dashboard.py (18 total).
_GPIO_DISPATCH_OUTPUT_COUNT = 10 + ERROR_DELETE_BUTTON_SLOTS  # 3 model + 6 shared + tabs + delete buttons


class InferenceHandlers:
    def __init__(self, ctx: AppContext, history: HistoryStore) -> None:
        self._ctx = ctx
        self._history = history
        self._last_lcd_posture = None
        self.current_session_id = None
        self.last_saved_posture = None
        self.last_presence_time = None
        self.posture_map = {"good_posture": 1,"slouching": 2,"looking_down": 3,"looking_up": 4,"leaning_forward": 5,"leaning_sideways": 6,}
        self.posture_service = PostureService(self._ctx)
        self.monitoring_service = MonitoringService(self._ctx,self.posture_service)
        self.monitoring_service.start()
        self.session_start_time = None
    # def shutdown_now(self) -> str:
    #     if not self._ctx.shared.mark_shutdown():
    #         return "Shutdown already requested."
    #     self._ctx.lcd.show_shutdown()

    #     def _worker() -> None:
    #         time.sleep(0.5)
    #         request_sudo_poweroff()

    #     threading.Thread(target=_worker, daemon=True).start()
    #     return "Shutdown requested."
    
    def shutdown_now(self) -> str:
        if not self._ctx.shared.mark_shutdown():
            return "Shutdown already requested."

        if self.current_session_id is not None:
            self.end_db_session()

        self._ctx.lcd.show_shutdown()

        def _worker() -> None:

            self._ctx.lcd.show_lines(
                "Shutting Down",
                "Goodbye",
                force=True,
            )

            time.sleep(2)

            self._ctx.lcd.clear()

            if self._ctx.led is not None:
                self._ctx.led.set_off()
                
            self._ctx.lcd.backlight_off()

            time.sleep(1)

            request_sudo_poweroff()

        threading.Thread(target=_worker, daemon=True).start()
        return "Shutdown requested."

    @staticmethod
    def _gpio_dispatch_no_op():
        return (gr.update(),) * _GPIO_DISPATCH_OUTPUT_COUNT

    def sync_selected_model(self, _model: str = MODEL_POSE) -> str:
        """MediaPipe is the only available inference pipeline."""
        self._ctx.runtime.set_selected_model(MODEL_POSE)
        return MODEL_POSE

    # def on_gpio_short_press(self) -> None:
    #     # Called from GPIO poll thread — only set a flag; Gradio runs inference via Timer.
    #     if self._ctx.runtime.request_gpio_inference():
    #         snap = self._ctx.runtime.read_inference_snapshot()
    #         print(f"[GPIO] Short press -> queue {snap.selected_model} inference")
    
    def on_gpio_short_press(self) -> None:
        if self._ctx.monitoring is None:
            return

        enabled = self._ctx.monitoring.toggle()

        if enabled:
            print("[MONITORING] Enabled")

            self._ctx.lcd.show_lines(
                "Monitoring",
                "Enabled",
                force=True,
            )

        else:
            print("[MONITORING] Disabled")

            self._ctx.lcd.show_lines(
                "Monitoring",
                "Disabled",
                force=True,
            )

    # def update_led(self, posture_class: str | None) -> None:
    #     if self._ctx.led is None:
    #         return

    #     if posture_class is None:
    #         self._ctx.led.set_active()  # Blue = no person

    #     elif posture_class == "good_posture":
    #         self._ctx.led.set_ready()  # Green

    #     else:
    #         self._ctx.led.set_error()  # Red
            
    # def start_db_session(self):
    #     response = requests.post(f"{API_URL}/sessions/start")
    #     response.raise_for_status()
    #     return response.json()["session_id"]
 
 
    # def end_db_session(self):
    #     if self.current_session_id is None:
    #         return
        
    #     print("ENDING SESSION:", self.current_session_id)
        
    #     requests.put(f"{API_URL}/sessions/{self.current_session_id}/end")
    #     self.current_session_id = None
    #     self.last_saved_posture = None
    

    # def save_posture_event(self,posture: str,confidence: float,person_near):
    #     if self.current_session_id is None:
    #         return
        
    #     posture_id = self.posture_map.get(posture)
        
    #     if posture_id is None:
    #         return

        # response = requests.post(f"{API_URL}/posture-events/",
        #     json={
        #         "session_id": self.current_session_id,
        #         "posture_id": posture_id,
        #         "detected_at": (
        #             datetime.utcnow()
        #             .isoformat()
        #         ),
        #         "confidence": confidence,
        #         "sensor_presence": person_near,
        #         "alert_triggered": (
        #             posture != "good_posture"
        #         ),
        #     },
        # )
        # response.raise_for_status()
        
        
            
    def run_pose(
        self,
        source_type: str,
        latest_capture_rgb: np.ndarray | None,
        upload_rgb: np.ndarray | None,
        browser_webcam_rgb: np.ndarray | None,
        ai_history: list[dict[str, Any]],
        error_history: list[dict[str, Any]],
    ):
        try:
            if source_type == "browser_upload" and upload_rgb is None:
                return (
                    None,
                    "Waiting for an uploaded image...",
                    self._history.server_status_update({}),
                    ai_history,
                    error_history,
                    render_history_accordion("AI responses", ai_history),
                    gr.update(),
                    *self._history.error_button_updates(error_history),
                )
            src_rgb = pick_source_frame(
                self._ctx.providers,
                source_type,
                latest_capture_rgb,
                upload_rgb,
                browser_webcam_rgb,
            )
            # result = self._ctx.models[MODEL_POSE].run(src_rgb)
            # lm_count = int(result.payload.get("landmark_count", 0))
            # posture = result.payload.get("posture", "Unknown")
            # confidence = result.payload.get("confidence", 0.0)  
            result, posture, confidence, lm_count = (self.posture_service.process_frame(src_rgb))
            
            if source_type == "browser_upload":
                if lm_count == 0:
                    self._ctx.lcd.show_result("No Person")
                else:
                    self._ctx.lcd.show_result(
                    posture.replace("_", " ")
                )
            
        #     if posture == "No Person":
        #         self.update_led(None)
        #     elif posture == "good_posture":
        #         self.update_led(posture)
        #     else:
        #         self.update_led(posture)  
            
        #     if posture != "good_posture" and posture != "No Person":
        #         self._ctx.buzzer.play_cooldown(
        #             "error",
        #             "bad_posture",
        #             3.0,
        #             target = 'passive'
        #         )
                
            
        #     if lm_count == 0:
        #         self._ctx.lcd.show_result("No person")
        #     else:
        #         self._ctx.lcd.show_result(posture)
                
        #     if not self._ctx.monitoring_enabled:
        #         return (
        #         result.annotated_rgb,
        #         f"{confidence:.2%}",
        #         posture,
        #         "00:00:00",
        #         "Monitoring Disabled",
        #         self._history.server_status_update({}),
        #         ai_history,
        #         error_history,
        #         render_history_accordion("AI responses", ai_history),
        #         gr.update(),
        #         *self._history.error_button_updates(error_history),
        #     )
            
        #     sensor = self._ctx.ultrasonic
        #     if sensor is None:
        #         raise RuntimeError("Ultrasonic sensor not initialized")
            
        #     person_near = sensor.human_detected(max_distance=80)
        #     print("PERSON NEAR =", person_near)
        #     print("LAST PRESENCE =", self.last_presence_time)
        #     if person_near:
        #         self.last_presence_time = time.time()
        #         if self.current_session_id is None:
        #             self.current_session_id = self.start_db_session()
        #             print("Started session:",self.current_session_id)
                    
                
            
        #     else:
        #         if self.last_presence_time is not None:
        #             absent_seconds = (time.time()- self.last_presence_time)
        #             if absent_seconds>=15:
        #                 self.end_db_session()
        #                 print("Ended session after",absent_seconds)
        #                 self.current_session_id = None
        #                 self.last_presence_time = None
        #             print(
        #     "ABSENT FOR:",
        #     absent_seconds
        # )
            
        #     if self.current_session_id is not None and posture != "No Person" and posture != self.last_saved_posture:
        #         self.save_posture_event(posture,confidence,person_near,)
        #         self.last_saved_posture = posture
        #         print("Saved posture:",posture)
                    
                    
            
            # lcd_text = "No person" if lm_count == 0 else posture
            # if lcd_text!=self._last_lcd_posture:
            #     self._ctx.lcd.show_result(lcd_text)
            #     self._last_lcd_posture = lcd_text
            payload = {**result.payload, "source_type": source_type}
            ai_history = self._history.append_ai(
                ai_history, "MediaPipe Pose response", payload, result.annotated_rgb
            )
            return (
                result.annotated_rgb,
                self.build_confidence_card(confidence),
                self.build_posture_card(posture),
                self.posture_service.get_session_duration(),
                result.status_text,
                self._history.server_status_update(payload),
                ai_history,
                error_history,
                render_history_accordion("AI responses", ai_history),
                gr.update(),
                *self._history.error_button_updates(error_history),
            )
        except Exception as exc:
            msg = str(exc)
            self._ctx.lcd.show_result("pose error")
            error_history = self._history.append_error(error_history, "Pose inference failed", msg)
            return (
                None,  
                "",  
                "",  
                "00:00:00",  
                f"Pose error: {msg}", 
                self._history.server_status_update(
                    {
                        "error": msg,
                        "model": "mediapipe_pose",
                    }
                ),
                ai_history,
                error_history,
                gr.update(),  
                render_history_accordion(
                    "Errors",
                    error_history,
                ),
                *self._history.error_button_updates(
                    error_history
                ),
            )
        
    def get_monitoring_status(self):

        enabled = self._ctx.monitoring_enabled

        if enabled:
            return (
                True,
                """
                <div style="
                padding:20px;
                border-radius:12px;
                background:#f8fafc;
                border:1px solid #e5e7eb;
                text-align:center;
                ">
                    <h3>Monitoring Status</h3>
                    <h2 style="color:#16a34a;">🟢 Enabled</h2>
                </div>
                """,
                gr.update(value="🔴 Disable Monitoring")
            )

        return (
            False,
            """
            <div style="
            padding:20px;
            border-radius:12px;
            background:#f8fafc;
            border:1px solid #e5e7eb;
            text-align:center;
            ">
                <h3>Monitoring Status</h3>
                <h2 style="color:#dc2626;">🔴 Disabled</h2>
            </div>
            """,
            gr.update(value="🟢 Enable Monitoring")
    )
    def toggle_monitoring(self, enabled: bool):
        self._ctx.monitoring_enabled = (not self._ctx.monitoring_enabled)

        new_state = self._ctx.monitoring_enabled
        
        if new_state:
            self._ctx.lcd.show_lines(
            "Monitoring",
            "Enabled",
            force=True,
        )
        else:
            self._ctx.lcd.show_lines(
            "Monitoring",
            "Disabled",
            force=True,
        )

        if new_state:
            return (
                True,
                """
                <div style="
                padding:20px;
                border-radius:12px;
                background:#f8fafc;
                border:1px solid #e5e7eb;
                text-align:center;
                ">
                    <h3>Monitoring Status</h3>
                    <h2 style="color:#16a34a;">🟢 Enabled</h2>
                </div>
                """,
                gr.update(value="🔴 Disable Monitoring")
            )

        return (
            False,
            """
            <div style="
            padding:20px;
            border-radius:12px;
            background:#f8fafc;
            border:1px solid #e5e7eb;
            text-align:center;
            ">
                <h3>Monitoring Status</h3>
                <h2 style="color:#dc2626;">🔴 Disabled</h2>
            </div>
            """,
            gr.update(value="🟢 Enable Monitoring")
        )
        
    def on_gpio_short_press(self) -> None:
        self._ctx.monitoring_enabled = (
            not self._ctx.monitoring_enabled
        )

        if self._ctx.monitoring_enabled:
            print("[MONITORING] Enabled")

            self._ctx.lcd.show_lines(
                "Monitoring",
                "Enabled",
                force=True,
            )
        else:
            print("[MONITORING] Disabled")

            self._ctx.lcd.show_lines(
                "Monitoring",
                "Disabled",
                force=True,
            )
            
    def build_posture_card(self, posture):

        color = "#16a34a"
        icon = "✅"

        if posture != "good_posture":
            color = "#dc2626"
            icon = "⚠️"

        label = posture.replace("_", " ").title()

        return f"""
        <div style="
        padding:20px;
        border-radius:12px;
        background:#f8fafc;
        border:1px solid #e5e7eb;
        text-align:center;
        ">
            <h3>Current Posture</h3>
            <h2 style="color:{color};">
                {icon} {label}
            </h2>
        </div>
        """
        
    def build_confidence_card(self, confidence):

        percent = int(confidence * 100)

        if percent >= 80:
            color = "#16a34a"
        elif percent >= 50:
            color = "#f59e0b"
        else:
            color = "#dc2626"

        return f"""
        <div style="
        padding:20px;
        border-radius:12px;
        background:#f8fafc;
        border:1px solid #e5e7eb;
        ">
            <h3>Confidence</h3>

            <div style="
                width:100%;
                height:18px;
                background:#e5e7eb;
                border-radius:10px;
            ">
                <div style="
                    width:{percent}%;
                    height:18px;
                    background:{color};
                    border-radius:10px;
                "></div>
            </div>

            <p style="text-align:center;">
                {percent}%
            </p>
        </div>
        """
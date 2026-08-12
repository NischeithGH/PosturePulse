from __future__ import annotations

import threading
import time

from inputs.registry import INPUT_RPI_CAMERA


class MonitoringService:

    def __init__(
        self,
        ctx,
        posture_service,
    ):
        self.ctx = ctx
        self.posture_service = posture_service

        self._running = False
        self._thread = None

    def start(self):

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

        print(
            "[MONITORING] Service started"
        )

    def stop(self):
        self._running = False

    def _run(self):

        camera = self.ctx.providers[
            INPUT_RPI_CAMERA
        ]

        while self._running:

            try:

                if not self.ctx.monitoring_enabled:
                    time.sleep(0.5)
                    continue

                frame_rgb = camera.read_frame()

                if frame_rgb is None:
                    time.sleep(0.1)
                    continue

                self.posture_service.process_frame(
                    frame_rgb
                )

            except Exception as exc:

                print(
                    "[MONITORING ERROR]",
                    exc,
                )

            time.sleep(0.5)
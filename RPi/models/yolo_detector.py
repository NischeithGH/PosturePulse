from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from .base import InferenceResult


class YoloDroneModel:
    def __init__(self, model_path: Path) -> None:
        self._model = YOLO(str(model_path))

    def run(self, frame_rgb: np.ndarray, conf: float, iou: float) -> InferenceResult:
        src_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        result = self._model.predict(
            source=src_bgr,
            conf=float(conf),
            iou=float(iou),
            imgsz=640,
            verbose=False,
        )[0]
        annotated_rgb = cv2.cvtColor(result.plot(),cv2.COLOR_BGR2RGB)
        cls_ids = (result.boxes.cls.cpu().tolist()if result.boxes is not None else [])
        counts: dict[str, int] = {}
        for cls_id in cls_ids:
            name = self._model.names[int(cls_id)]
            counts[name] = counts.get(name, 0) + 1
        
        payload = {
            "model": "best.pt",
            "detection_count": len(cls_ids),
            "counts": counts,
            "conf": float(conf),
            "iou": float(iou),
        }
        return InferenceResult(
            annotated_rgb=annotated_rgb,
            payload=payload,
            status_text=f"YOLO done. detections={len(cls_ids)}",
        )

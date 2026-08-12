from __future__ import annotations

from pathlib import Path
from unittest import result
from urllib.request import urlretrieve

import cv2
import numpy as np

from .base import InferenceResult

import joblib  

from pathlib import Path

import math
import time
from collections import Counter



def calculate_angle(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(dy, dx))

try:
    import mediapipe as mp
except Exception:
    mp = None

DEFAULT_TASK_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)

POSE_CONNECTIONS: tuple[tuple[int, int], ...] = (         
    (11, 12),(11,23),(0, 11),(0, 12), (7,0),(8,0),(12,24)
)#need to change

RELEVANT_LANDMARK_IDS: tuple[int, ...] = (0,7,8,11,12,23,24)#need to change

class MediaPipePoseModel:
    def __init__(self, base_dir: Path) -> None:
        self.mode = "unavailable"
        self.detector = None
        self.init_error: str | None = None
        self.bad_posture_start = None
        self.current_posture = None
        self.classifier = joblib.load(base_dir / "ai" / "posture_model.pkl")
        if mp is None:
            self.init_error = (
                "MediaPipe import failed. Install `mediapipe` (or `mediapipe-rpi4`) in this venv. "
                "If wheels are unavailable, use Python 3.11/3.12."
            )
            return
        self._init_tasks(base_dir)
        if self.mode == "unavailable":
            self._init_solutions()
        self.bad_posture_start = None
        self.current_posture = None

    def _init_tasks(self, base_dir: Path) -> None:
        try:
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            task_model_path = base_dir / "ai" / "pose_landmarker_lite.task"
            if not task_model_path.exists():
                urlretrieve(DEFAULT_TASK_MODEL_URL, str(task_model_path))
            options = vision.PoseLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=str(task_model_path)),
                running_mode=vision.RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.detector = vision.PoseLandmarker.create_from_options(options)
            self.mode = "tasks"
        except Exception as exc:
            self.init_error = f"MediaPipe tasks init failed: {exc}"

    def _init_solutions(self) -> None:
        try:
            if not hasattr(mp, "solutions"):
                raise RuntimeError("mp.solutions not available")
            self.detector = mp.solutions.pose.Pose(  # type: ignore[union-attr]
                static_image_mode=False,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
            self.mode = "solutions"
        except Exception as exc:
            self.init_error = f"{self.init_error or ''} | solutions init failed: {exc}".strip(" |")

    def _draw_pose(self, frame_bgr: np.ndarray, points: dict[int, tuple[int, int]]) -> np.ndarray:
        out = frame_bgr.copy()
        for start, end in POSE_CONNECTIONS:
            a = points.get(start)
            b = points.get(end)
            if a is None or b is None:
                continue
            cv2.line(out, a, b, (0, 220, 255), 2, cv2.LINE_AA)
        for pt in points.values():
            cv2.circle(out, pt, 4, (0, 255, 0), -1, cv2.LINE_AA)
        return out

    def run(self, frame_rgb: np.ndarray) -> InferenceResult:
        if self.detector is None:
            raise ValueError(self.init_error or "MediaPipe pose detector unavailable.")

        src_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = src_bgr.shape
        points: dict[int, tuple[int, int]] = {}
        landmark_features : dict[int, tuple[float, float,float]] = {}

        if self.mode == "tasks":
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            task_result = self.detector.detect(mp_image)
            if task_result.pose_landmarks:
                for idx, lm in enumerate(task_result.pose_landmarks[0]):
                    if idx not in RELEVANT_LANDMARK_IDS:
                        continue
                    visibility = float(getattr(lm, "visibility", 1.0))
                    # if visibility < 0.3:
                    #     continue
                    points[idx] = (int(lm.x * w), int(lm.y * h))
                    landmark_features[idx] = (lm.x, lm.y, lm.z)
        elif self.mode == "solutions":
            result = self.detector.process(frame_rgb)
            if result.pose_landmarks:
                for idx, lm in enumerate(result.pose_landmarks.landmark):
                    if idx not in RELEVANT_LANDMARK_IDS:
                        continue
                    visibility = float(getattr(lm, "visibility", 1.0))
                    if visibility < 0.3:
                        continue
                    points[idx] = (int(lm.x * w), int(lm.y * h))
                    landmark_features[idx] = (lm.x, lm.y, lm.z)
        else:
            raise ValueError(self.init_error or "MediaPipe pose detector unavailable.")

        ann_rgb = cv2.cvtColor(self._draw_pose(src_bgr, points), cv2.COLOR_BGR2RGB)
        
        if len(landmark_features) > 0:

            xs = [lm[0] for lm in landmark_features.values()]
            ys = [lm[1] for lm in landmark_features.values()]

            body_width = max(xs) - min(xs)
            body_height = max(ys) - min(ys)

            body_area = body_width * body_height

            print(f"BODY AREA = {body_area:.4f}")
        
        keypoints = []
        # for idx in RELEVANT_LANDMARK_IDS:
        #     landmark = landmark_features.get(idx)
        #     if landmark:
        #         keypoints.extend([landmark[0], landmark[1],landmark[2]])
        #     else:
        #         keypoints.extend([0]*3)

        if all(idx in landmark_features for idx in [0, 7,8, 11, 12, 23, 24]):
            ear_x      = (landmark_features[7][0]  + landmark_features[8][0])  / 2
            ear_y      = (landmark_features[7][1]  + landmark_features[8][1])  / 2
            shoulder_x = (landmark_features[11][0] + landmark_features[12][0]) / 2
            shoulder_y = (landmark_features[11][1] + landmark_features[12][1]) / 2
            hip_x      = (landmark_features[23][0] + landmark_features[24][0]) / 2
            hip_y      = (landmark_features[23][1] + landmark_features[24][1]) / 2
            
            y_top       = landmark_features[0][1]
            y_bottom    = hip_y
            x_ref       = hip_x
            body_height = (y_bottom - y_top) + 1e-6
            
            def norm_y(y): return (y - y_top)  / body_height
            def norm_x(x): return (x - x_ref) / body_height
            
            for idx in RELEVANT_LANDMARK_IDS:
                lm = landmark_features.get(idx)
                if lm:
                    keypoints.extend([norm_x(lm[0]), norm_y(lm[1]), lm[2]])
                else:
                    keypoints.extend([0.0, 0.0, 0.0])

            nose_xn     = norm_x(landmark_features[0][0])
            nose_yn     = norm_y(landmark_features[0][1])   
            ear_xn      = norm_x(ear_x)
            ear_yn      = norm_y(ear_y)
            shoulder_xn = norm_x(shoulder_x)
            shoulder_yn = norm_y(shoulder_y)
            hip_xn      = norm_x(hip_x)                     
            hip_yn      = norm_y(hip_y) 
            
            head_angle     = calculate_angle((ear_xn,      ear_yn),
                                             (nose_xn,     nose_yn))
            neck_angle     = calculate_angle((shoulder_xn, shoulder_yn),
                                             (ear_xn,      ear_yn))
            torso_angle    = calculate_angle((hip_xn,      hip_yn),
                                             (shoulder_xn, shoulder_yn))
            shoulder_angle = calculate_angle(
                (norm_x(landmark_features[11][0]), norm_y(landmark_features[11][1])),
                (norm_x(landmark_features[12][0]), norm_y(landmark_features[12][1]))
            )
            
            forward_lean         = nose_xn - shoulder_xn
            spine_curve          = (nose_xn - shoulder_xn) - (shoulder_xn - hip_xn)
            lateral_shift_norm   = shoulder_xn - hip_xn
            shoulder_height_diff = norm_y(landmark_features[11][1]) - norm_y(landmark_features[12][1])

            keypoints.extend([
                head_angle,
                neck_angle,
                torso_angle,
                shoulder_angle,
                forward_lean,
                spine_curve,
                lateral_shift_norm,
                shoulder_height_diff,
            ])

        else:
            for idx in RELEVANT_LANDMARK_IDS:
                lm = landmark_features.get(idx)
                if lm:
                    keypoints.extend([lm[0], lm[1], lm[2]])
                else:
                    keypoints.extend([0.0, 0.0, 0.0])
            keypoints.extend([0] * 8)
        confidence = 0.0
        prediction = 'No Person'
        print(f"Points detected: {len(points)}")
        print(f"Features: {len(keypoints)}")
        if len(points) > 0:
            try:
                probs = self.classifier.predict_proba([keypoints])[0]
                print("classes:", self.classifier.classes_)
                print("probs:", probs)
                # max_prob = max(probs)
                # if max_prob < 0.5:
                #     prediction = 'Uncertain'
                # else:

                prediction = self.classifier.predict([keypoints])[0]
                confidence = float(np.max(probs))
                
                BAD_POSTURES = {
                    "slouching",
                    "looking_down",
                    "looking_up",
                    "leaning_forward",
                    "leaning_sideways",
                }

                
                now = time.time()
                

                if prediction in BAD_POSTURES:
                    if self.current_posture != prediction:
                        self.current_posture = prediction
                        self.bad_posture_start = now
                    else:
                        if self.bad_posture_start is not None:
                            elapsed = now - self.bad_posture_start
                            if elapsed >= 4:
                                print("BUZZER SHOULD TURN ON")
                else:
                    self.current_posture = None
                    self.bad_posture_start = None

                print(f"Prediction: {prediction}")
            except Exception as exc:
                print("Prediction error")
                print(exc)
        else:
            print("No landmarks detected, skipping prediction.")
                
        payload = {
            "model": "mediapipe_pose",
            "pose_mode": self.mode,
            "found_person": len(points) > 0,
            "landmark_count": len(points),
            "posture": prediction,
            "confidence":confidence,
        }
        return InferenceResult(
            annotated_rgb=ann_rgb,
            payload=payload,
            status_text=f"Pose done. landmarks={len(points)}",
        )

    def close(self) -> None:
        if self.detector is not None and hasattr(self.detector, "close"):
            self.detector.close()
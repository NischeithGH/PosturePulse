from __future__ import annotations

from pathlib import Path

from .pose_detector import MediaPipePoseModel

MODEL_POSE = "pose"
MODEL_IDS = (MODEL_POSE,)


def build_models(base_dir: Path) -> dict[str, MediaPipePoseModel]:
    """Load the MediaPipe pose detector and Random Forest posture classifier."""
    return {MODEL_POSE: MediaPipePoseModel(base_dir)}

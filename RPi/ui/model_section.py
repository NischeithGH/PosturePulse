from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import gradio as gr

from models.registry import MODEL_POSE, MODEL_YOLO


@dataclass
class ModelSection:
    model_tabs: gr.Tabs
    selected_model: gr.Radio  # synced to runtime on tab/radio change (not GPIO timer input)
    yolo_conf: gr.Slider
    yolo_iou: gr.Slider
    yolo_run: gr.Button
    yolo_output: gr.Image
    yolo_count_output: gr.Textbox
    monitoring_status: gr.HTML
    monitoring_toggle: gr.Button
    pose_output: gr.Image
    posture_output: gr.HTML
    confidence_output: gr.HTML
    session_output: gr.Textbox
    analyze_btn: gr.Button
    upload_image: gr.Image
    monitoring_enabled: gr.State


def tab_value_to_model(value: Any) -> str:
    # """Map Tabs value (id, label, or index) to MODEL_* — used by select event and GPIO timer."""
    # if value is None:
    #     return MODEL_YOLO
    # if isinstance(value, int):
    #     return MODEL_YOLO if value == 0 else MODEL_POSE
    # token = str(value).strip().lower()
    # if token in (MODEL_YOLO, "yolo", "0"):
    #     return MODEL_YOLO
    # if token in (MODEL_POSE, "pose", "1"):
    #     return MODEL_POSE
    # if "yolo" in token or "drone" in token or "best.pt" in token:
    #     return MODEL_YOLO
    # if "pose" in token or "mediapipe" in token:
    #     return MODEL_POSE
    return MODEL_POSE


def _tab_id_to_model(evt: gr.SelectData) -> str:
    return tab_value_to_model(evt.value)


def model_to_tab_id(model_id: str) -> str:
    # return MODEL_YOLO if tab_value_to_model(model_id) == MODEL_YOLO else MODEL_POSE
    return MODEL_POSE


def build_model_section() -> ModelSection:
    selected_model = gr.Radio(
        choices=[("MediaPipe Pose", MODEL_POSE)],
        value=MODEL_POSE,
        label="GPIO short press runs",
        visible=False
    )
    monitoring_enabled = gr.State(False)
    with gr.Tabs() as model_tabs:
        
        # with gr.TabItem("Drone YOLO (best.pt)", id="yolo"):
        #     with gr.Row():
        #         yolo_conf = gr.Slider(0.0, 1.0, value=0.25, step=0.05, label="Confidence threshold")
        #         yolo_iou = gr.Slider(0.0, 1.0, value=0.45, step=0.05, label="IoU threshold")
        #     yolo_run = gr.Button("Run Drone YOLO", variant="primary")
        #     yolo_output = gr.Image(label="YOLO output", type="numpy")
        #     yolo_count_output = gr.Textbox(label="Drone count summary", lines=2)
        with gr.TabItem("", id="pose"):
            with gr.Row():
                with gr.Column(scale=7):
                    
                    upload_image = gr.Image(
                        label="Uploaded Image",
                        type="numpy",
                        visible=False,
                        height=750
                    )

                    pose_output = gr.Image(
                        label="Live Monitoring Feed",
                        type="numpy",
                        visible=True,
                        height=750
                    )

                    with gr.Row():
                        analyze_btn = gr.Button(
                            "Detect Posture",
                            variant="primary",
                            visible=False
                        )
                with gr.Column(scale=3):

                    monitoring_status = gr.HTML("""
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
                    """)

                    # posture_output = gr.Textbox(
                    #     label="Current Posture",
                    #     interactive=False
                    # )
                    
                    posture_output = gr.HTML("""
                                            <div style="
                                            padding:20px;
                                            border-radius:12px;
                                            background:#f8fafc;
                                            border:1px solid #e5e7eb;
                                            text-align:center;
                                            ">
                                                <h3>Current Posture</h3>
                                                <h2 style="color:#6b7280;">Waiting...</h2>
                                            </div>
                                            """)

                    # confidence_output = gr.Textbox(
                    #     label="Confidence",
                    #     interactive=False
                    # )
                    
                    confidence_output = gr.HTML("""
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
            width:0%;
            height:18px;
            background:#16a34a;
            border-radius:10px;
        "></div>
    </div>
    <p style="text-align:center;">0%</p>
</div>
""")

                    session_output = gr.Textbox(
                        label="Session Duration",
                        interactive=False
                    )

                    monitor_toggle = gr.Button(
                        "🟢 Enable Monitoring",
                        variant="primary",
                        size="lg"
                    )


    return ModelSection(
        model_tabs=model_tabs,
        selected_model=selected_model,
        yolo_conf=None,
        yolo_iou=None,
        yolo_run=None,
        yolo_output=None,
        yolo_count_output=None,
        monitoring_status=monitoring_status,
        monitoring_toggle=monitor_toggle,
        pose_output=pose_output,
        posture_output=posture_output,
        confidence_output=confidence_output,
        session_output=session_output,
        analyze_btn=analyze_btn,
        upload_image=upload_image,
        monitoring_enabled=monitoring_enabled
        
    )

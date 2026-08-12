from __future__ import annotations

import base64
from pathlib import Path

import gradio as gr


def _img_to_base64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def build_about_page():

    posture_dir = Path(__file__).parent / "assets" / "postures"

    good = _img_to_base64(posture_dir / "good_posture.png")
    down = _img_to_base64(posture_dir / "looking_down.png")
    up = _img_to_base64(posture_dir / "looking_up.png")
    side = _img_to_base64(posture_dir / "leaning_sideways.png")
    slouch = _img_to_base64(posture_dir / "slouching.png")
    forward = _img_to_base64(posture_dir / "leaning_forward.png")

    gr.Markdown("""
# 🚀 PosturePulse

### AI-Powered Real-Time Posture Monitoring System

PosturePulse is an AI-powered posture monitoring system designed to help users maintain healthier sitting habits. By combining computer vision, machine learning, and real-time monitoring, the system detects posture, records monitoring sessions automatically, and presents detailed analytics through an interactive dashboard.

---

# ⚙️ How It Works

### 1️⃣ Presence Detection
The ultrasonic sensor detects when a user is seated in front of the workstation.

### 2️⃣ Posture Analysis
The camera captures images and the posture model analyzes the user's posture in real time.

### 3️⃣ Session Recording
Monitoring sessions and posture events are automatically stored in the PostgreSQL database.

### 4️⃣ Analytics Dashboard
Session statistics, posture distributions, and monitoring history are visualized through the dashboard.

---

# 🪑 Supported Postures
""")

    gr.HTML(f"""
    <div style="
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:40px 30px;
        justify-items:center;
        margin-top:20px;
    ">

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{good}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ✅ Good Posture
            </p>
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{down}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ⚠️ Looking Down
            </p>
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{up}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ⚠️ Looking Up
            </p>
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{side}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ⚠️ Leaning Sideways
            </p>
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{slouch}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ⚠️ Slouching
            </p>
        </div>

        <div style="display:flex;flex-direction:column;align-items:center;">
            <img src="data:image/png;base64,{forward}"
                 style="width:280px;height:280px;object-fit:contain;background:white;">
            <p style="margin:10px 0 0 0;text-align:center;font-size:20px;font-weight:bold;width:280px;">
                ⚠️ Leaning Forward
            </p>
        </div>

    </div>
    """)

    gr.Markdown("""
---

# ⚡ Quick Start Guide

### Step 1
Enable monitoring using the physical push button.

### Step 2
Sit in front of the camera and ultrasonic sensor.

### Step 3
The system automatically detects your presence and starts a monitoring session using the ultrasonic sensor.

### Step 4
Maintain a healthy sitting posture while studying or working.

### Step 5
Review statistics, posture history, and session details on the Data page.

---

# 🔧 Hardware Components

• Raspberry Pi 5

• USB Camera

• Ultrasonic Sensor

• RGB LED

• Buzzer

• I²C LCD Display

• Push Button

---

# 🤖 Software Stack

• Python

• MediaPipe

• FastAPI

• PostgreSQL

• Gradio

---

# ✨ Key Features

✓ Real-Time Posture Detection

✓ Automatic Session Management

✓ Presence-Based Monitoring

✓ Session History Tracking

✓ Interactive Dashboard Analytics

✓ RGB LED Feedback

✓ Audio Posture Alerts

✓ LCD Status Display

✓ Physical Button Control

✓ Safe Raspberry Pi Shutdown

✓ Automatic Startup on Boot

---

### Healthy Posture. Smarter Work. Better Habits.
""")
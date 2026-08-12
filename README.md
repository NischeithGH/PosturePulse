# Posture-Pulse 🪑

AI-powered posture monitoring system that watches how you sit in real time and nudges you back into a healthy position — running entirely on a Raspberry Pi.

**By Nischeith Ravindra Boddapati** · CTAI, Howest University of Applied Sciences

<!-- Swap this for a real demo GIF/photo of the enclosure once you have one -->
<!-- ![demo](docs/demo.gif) -->

---

## The problem

People sit at desks for hours and slowly slouch, lean, or crane their neck without noticing — until their back or neck starts hurting. Posture-Pulse watches passively in the background and gives an immediate nudge the moment posture goes bad, instead of relying on willpower or periodic reminders.

## What it does

- Detects when someone sits down in front of it using an **ultrasonic presence sensor**, then automatically starts the camera
- Extracts body landmarks from the camera feed with **MediaPipe**
- Classifies posture into one of **six classes**: good posture, slouching, leaning forward, leaning sideways, looking down, looking up
- Gives instant feedback through an **LED + buzzer** and shows live status on an **I²C LCD**
- Logs every posture event (timestamp, confidence, session, sensor presence, whether an alert fired) to a **Postgres database**
- Serves a **Gradio dashboard** for live monitoring, posture history, and hardware debugging — with a **FastAPI** backend behind it

## How the AI works

1. **Landmark extraction** — MediaPipe pulls body keypoints (nose, ears, shoulders, hips) from each frame
2. **Feature engineering** — 8 features are computed from those landmarks per frame:
   `head_angle`, `neck_angle`, `torso_angle`, `shoulder_angle`, `forward_lean`, `spine_curve`, `lateral_shift_norm`, `shoulder_height_diff`
3. **Classification** — a **Random Forest** classifier (`posture_model.pkl`) trained on those features predicts the current posture class
4. **Feedback loop** — a sustained bad-posture reading triggers the LED/buzzer and updates the LCD in real time

A second model (YOLO, `best.pt`) also runs in the same dashboard as an alternate detection pipeline, selectable from the UI.

## Architecture

```
Ultrasonic sensor ──(presence detected)──► Camera activates
                                                  │
                                                  ▼
                                    MediaPipe (landmark extraction)
                                                  │
                                                  ▼
                                   8-feature engineering pipeline
                                                  │
                                                  ▼
                                    Random Forest classifier
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    ▼                              ▼                             ▼
          LED + buzzer alert              I²C LCD status display        FastAPI → Postgres (Docker)
                                                                                  │
                                                                                  ▼
                                                                    Gradio dashboard (live + history + debug)
```

**Database schema:** `sessions` → `posture_events` → `posture_classes`, tracking confidence, sensor presence, and whether an alert was triggered for every detection.

## Tech stack

| Layer | Tools |
|---|---|
| Computer vision | OpenCV, MediaPipe, Ultralytics YOLO |
| ML | scikit-learn (Random Forest) |
| Backend | FastAPI (routers/repositories/models), SQLModel |
| Database | PostgreSQL (Docker Compose) |
| Dashboard | Gradio |
| Hardware | Raspberry Pi 5, USB webcam, ultrasonic sensor, I²C LCD, LED, buzzer, push button |
| Deployment | Docker, systemd (autostart on boot) |

## Hardware

- Raspberry Pi 5
- USB webcam — posture capture
- Ultrasonic sensor — detects when a user sits down, auto-starts monitoring
- I²C LCD — live posture status
- LED + buzzer — bad-posture alert
- Push button — start/stop, shutdown (long-press)
- Custom laser-cut enclosure housing all components

## Results

<!-- TODO: fill in real numbers once you have them, e.g. -->
- Classifier accuracy on held-out test data: **[XX%]**
- Classes most often confused: **[e.g. leaning-sideways vs. leaning-forward]**
- Real-time inference rate on the Pi: **[X FPS]**

## Running it

```bash
# On the Raspberry Pi, from RPi/
cp api/.env.example api/.env
docker compose up -d --build     # Postgres + Adminer + FastAPI
python app.py                    # Gradio dashboard on :7860
```

Full setup docs (SD image prep, kickoff, autostart) are in [`Docs/`](Docs/).

## What I'd improve next

- [ ] Collect a larger, more varied training set (lighting, camera angle, body types)
- [ ] Clean up leftover naming from the course starter template (e.g. `YoloDroneModel`)
- [ ] Add proper unit tests for the feature-engineering pipeline
- [ ] Measure and record real classifier accuracy / confusion matrix

## About this project

Built as my **Project One** for the CTAI (Creative Technologies & AI) bachelor's programme at Howest University of Applied Sciences — covering computer vision, applied ML, embedded hardware/IoT, and full-stack deployment from a single-board computer.

The official course-required project definition and setup documentation are in [`PD.md`](PD.md) and [`Docs/`](Docs/).

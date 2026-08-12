# Posture Pulse

A Raspberry Pi posture-monitoring system that detects unhealthy sitting posture in real time and provides immediate physical feedback.

Posture Pulse combines computer vision, machine learning, embedded hardware, and a browser dashboard in one deployable project.

## Highlights

- Detects a person's presence with an ultrasonic sensor and starts monitoring automatically
- Classifies six posture states: good posture, slouching, leaning forward, leaning sideways, looking down, and looking up
- Uses MediaPipe landmarks and a trained Random Forest classifier for the primary posture pipeline
- Gives feedback through an I2C LCD, LED, and buzzer
- Records sessions and posture events in PostgreSQL through a FastAPI service
- Provides a Gradio dashboard for monitoring, history, data views, and hardware debugging

## Hardware

- Raspberry Pi 5
- USB webcam
- Ultrasonic distance sensor
- I2C LCD
- LED, buzzer, and push button

## Project structure

```text
RPi/
├── ai/          trained models used by the application
├── api/         FastAPI service and database integration
├── hardware/    Raspberry Pi sensor and actuator drivers
├── inputs/      camera and upload input sources
├── models/      MediaPipe pose detection and classification
├── services/    monitoring lifecycle and application bootstrap
├── ui/          Gradio dashboard
├── tests/       manual hardware smoke tests
├── app.py       dashboard entry point
└── docker-compose.yml
```

## Run on a Raspberry Pi

The hardware dashboard is intended for Raspberry Pi OS with the camera and GPIO devices connected.

```bash
git clone https://github.com/<your-username>/PosturePulse.git
cd PosturePulse/RPi

python3 -m venv --system-site-packages ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt

cp api/.env.example api/.env
docker compose up -d --build

python app.py
```

The dashboard is available at `http://<pi-ip>:7860`. FastAPI documentation is available at `http://<pi-ip>:8000/docs`.

Before running it, update the USB-camera fields in `config.py` if your device path or camera index differs. Use `python list_cameras.py` on the Pi to discover connected cameras.

## Models

The main pipeline extracts pose landmarks with MediaPipe and derives geometric features such as head, neck, torso, and shoulder angles. Those features are classified by the included Random Forest model.

## Notes

This repository contains the application code, configuration examples, dashboard assets, and the model files needed to run the prototype. Environment secrets, Python virtual environments, cache files, and local database data are excluded from Git.

Built by Nischeith Ravindra Boddapati.

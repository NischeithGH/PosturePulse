from __future__ import annotations

from sqlmodel import Session

import gradio as gr
import plotly.express as px
import pandas as pd

from database import engine
from api.repositories.session_repository import SessionRepository
from api.repositories.posture_event_repository import PostureEventRepository
from api.repositories.posture_class_repository import PostureClassRepository



class DataHandlers:

    def __init__(self):
        pass

    def load_overview_statistics(self):

        with Session(engine) as db:

            session_repo = SessionRepository(db)
            event_repo = PostureEventRepository(db)

            sessions = session_repo.get_all()
            events = event_repo.get_all()

        total_sessions = len(sessions)

        total_seconds = 0

        for session in sessions:

            if session.ended_at is None:
                continue

            total_seconds += (
                session.ended_at - session.started_at
            ).total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        if total_seconds < 60:
            monitoring_time = f"{int(total_seconds)} sec"
        else:
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            monitoring_time = f"{hours}h {minutes}m"

        completed_sessions = [
            session
            for session in sessions
            if session.ended_at is not None
        ]

        if completed_sessions:
            avg_seconds = (
                total_seconds /
                len(completed_sessions)
            )
        else:
            avg_seconds = 0

        if avg_seconds < 60:
            average_duration = f"{int(avg_seconds)} sec"
        else:
            average_duration = f"{int(avg_seconds // 60)} min"
            

        total_alerts = sum(
            1
            for event in events
            if event.alert_triggered
        )

        good_events = sum(
            1
            for event in events
            if event.posture_id == 1
        )

        total_events = len(events)

        if total_events > 0:
            good_percentage = round(
                good_events * 100 / total_events
            )
        else:
            good_percentage = 0

        return (
    f"### 📅\n\n## {total_sessions}\n\nTotal Sessions",
    f"### ⏱️\n\n## {monitoring_time}\n\nMonitoring Time",
    f"### ⌛\n\n## {average_duration}\n\nAvg Duration",
    f"### 🚨\n\n## {total_alerts}\n\nAlerts",
    f"### 🪑\n\n## {good_percentage}%\n\nGood Posture",
)


    def load_session_history(self):

        with Session(engine) as db:

            session_repo = SessionRepository(db)
            event_repo = PostureEventRepository(db)

            sessions = session_repo.get_all()

            rows = []

            for session in sessions:

                events = event_repo.get_by_session(
                    session.session_id
                )

                if session.ended_at is not None:
                    duration_seconds = int(
                        (
                            session.ended_at
                            - session.started_at
                        ).total_seconds()
                    )
                else:
                    duration_seconds = 0

                alerts = sum(
                    1
                    for event in events
                    if event.alert_triggered
                )

                total_events = len(events)

                good_events = sum(
                    1
                    for event in events
                    if event.posture_id == 1
                )

                good_percentage = (
                    round(
                        good_events * 100 / total_events
                    )
                    if total_events > 0
                    else 0
                )

                rows.append(
                    [
                        session.session_id,
                        session.started_at.strftime(
                            "%Y-%m-%d"
                        ),
                        f"{duration_seconds}s",
                        alerts,
                        f"{good_percentage}%",
                    ]
                )

            return rows
    
    def load_session_dropdown(self):

        with Session(engine) as db:

            session_repo = SessionRepository(db)

            sessions = session_repo.get_all()

            choices = [
                str(session.session_id)
                for session in sessions
            ]

            print("CHOICES =", choices)

            return gr.update(
                choices=choices,
                value=choices[0] if choices else None,
                interactive=True,
            )
    
    def load_session_details(self, session_id):
        
        if session_id is None:
            return "Select a session."

        with Session(engine) as db:

            session_repo = SessionRepository(db)
            event_repo = PostureEventRepository(db)

            session = session_repo.get_one(
                int(session_id)
            )

            events = event_repo.get_by_session(
                int(session_id)
            )

            duration = 0

            if session.ended_at is not None:

                duration = int(
                    (
                        session.ended_at
                        - session.started_at
                    ).total_seconds()
                )

            alerts = sum(
                1
                for event in events
                if event.alert_triggered
            )

            total_events = len(events)

            good_events = sum(
                1
                for event in events
                if event.posture_id == 1
            )

            good_percentage = (
                round(
                    good_events * 100 / total_events
                )
                if total_events > 0
                else 0
            )

        return f"""
        ## Session {session.session_id}

        🕒 **Duration:** {duration} sec<br>
        🚨 **Alerts:** {alerts}<br>
        🪑 **Good Posture:** {good_percentage}%<br><br>
        🗓️ **Started:** {session.started_at.strftime("%Y-%m-%d %H:%M:%S")}<br>
        🗓️ **Ended:** {session.ended_at.strftime("%Y-%m-%d %H:%M:%S") if session.ended_at else "Active"}
        """
    
    def load_session_breakdown_plot(self, session_id):
        if session_id is None:
            return None

        with Session(engine) as db:

            event_repo = PostureEventRepository(db)
            posture_repo = PostureClassRepository(db)

            events = event_repo.get_by_session(
                int(session_id)
            )

            posture_classes = posture_repo.get_all()

            posture_lookup = {
                posture.posture_id: posture.posture
                for posture in posture_classes
            }

            counts = {}

            for event in events:

                posture_name = posture_lookup.get(
                    event.posture_id,
                    "Unknown",
                )

                counts[posture_name] = (
                    counts.get(posture_name, 0) + 1
                )

            if not counts:
                df = pd.DataFrame(
            {
                "Posture": ["No Events"],
                "Count": [1],
            }
    )

                fig = px.pie(
                    df,
                    names="Posture",
                    values="Count",
                )

                fig.update_layout(
                    template="plotly_dark"
                )

                return fig

            df = pd.DataFrame(
                {
                    "Posture": list(counts.keys()),
                    "Count": list(counts.values()),
                }
            )

            fig = px.pie(
                df,
                names="Posture",
                values="Count",
                title="Session Breakdown",
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )

            return fig
            
    def load_posture_distribution_plot(self):

        with Session(engine) as db:

            event_repo = PostureEventRepository(db)
            posture_repo = PostureClassRepository(db)

            events = event_repo.get_all()
            posture_classes = posture_repo.get_all()

            posture_lookup = {
                posture.posture_id: posture.posture
                for posture in posture_classes
            }

            counts = {}

            for event in events:

                posture_name = posture_lookup.get(
                    event.posture_id,
                    "Unknown",
                )

                counts[posture_name] = (
                    counts.get(posture_name, 0) + 1
                )

            if not counts:

                df = pd.DataFrame(
                    {
                        "Posture": ["No Data"],
                        "Count": [1],
                    }
                )

                return px.pie(
                    df,
                    names="Posture",
                    values="Count",
                )

            df = pd.DataFrame(
                {
                    "Posture": list(counts.keys()),
                    "Count": list(counts.values()),
                }
            )

            fig = px.pie(
                df,
                names="Posture",
                values="Count",
                title="Posture Distribution",
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )

            return fig
    def load_alerts_per_session_plot(self):

        with Session(engine) as db:

            session_repo = SessionRepository(db)
            event_repo = PostureEventRepository(db)

            sessions = session_repo.get_all()

            session_ids = []
            alert_counts = []

            for session in sessions:

                events = event_repo.get_by_session(
                    session.session_id
                )

                alerts = sum(
                    1
                    for event in events
                    if event.alert_triggered
                )

                session_ids.append(
                    f"S{session.session_id}"
                )

                alert_counts.append(alerts)

            df = pd.DataFrame(
                {
                    "Session": session_ids,
                    "Alerts": alert_counts,
                }
            )

            fig = px.bar(
                df,
                x="Session",
                y="Alerts",
            )

            fig.update_layout(
                xaxis_title="Session",
                yaxis_title="Alerts",
            )

        return fig 


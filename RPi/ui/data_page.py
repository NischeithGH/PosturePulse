from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


@dataclass
class DataPage:

    refresh_button: gr.Button

    total_sessions: gr.Markdown
    total_time: gr.Markdown
    average_duration: gr.Markdown
    total_alerts: gr.Markdown
    good_posture_percentage: gr.Markdown

    confidence_analysis_plot: gr.Plot
    alerts_per_session_plot: gr.Plot

    session_history_table: gr.Dataframe

    session_dropdown: gr.Dropdown
    session_details: gr.Markdown
    session_breakdown_plot: gr.Plot
    
def build_data_page() -> DataPage:
    with gr.Row():
        gr.Markdown("## Data Analytics")
        refresh_button = gr.Button(
        "🔄 Refresh",
        variant="secondary",
        scale=1,
        min_width=120      
    )
    with gr.Row():
            total_sessions = gr.Markdown("""
            ### 📅

            ## 0

            Total Sessions
            """,
            elem_classes=["stat-card"])

            total_time = gr.Markdown("""
            ### ⏱️

            ## 0h

            Monitoring Time
            """,
            elem_classes=["stat-card"])

            average_duration = gr.Markdown("""
            ### ⌛

            ## 0m

            Avg Duration
            """,
            elem_classes=["stat-card"])

            total_alerts = gr.Markdown("""
            ### 🚨

            ## 0

            Alerts
            """,
            elem_classes=["stat-card"])

            good_posture_percentage = gr.Markdown("""
            ### 🪑

            ## 0%

            Good Posture
            """,
            elem_classes=["stat-card"])

    gr.Markdown("### Analytics")
    with gr.Row(equal_height=True):
        confidence_analysis_plot = gr.Plot(label="Overall Posture Distribution")
        alerts_per_session_plot = gr.Plot(label="Alerts Triggered Per Session")
    gr.Markdown("### Session Analysis")
    with gr.Row(equal_height=True):
        with gr.Column(scale=4):
            session_history_table = gr.Dataframe(
            headers=[
                "Session",
                "Date",
                "Duration",
                "Alerts",
                "Good %",
            ],
            label="Session History",
            max_height = 500,
            interactive=False
        )

        with gr.Column(scale=3):
            session_dropdown = gr.Dropdown(label="Select Session",choices=[],)
            session_details = gr.Markdown("Select a session to view details.")
            session_breakdown_plot = gr.Plot(label="Selected Session Breakdown")
    return DataPage(
    refresh_button=refresh_button,
    total_sessions=total_sessions,
    total_time=total_time,
    average_duration=average_duration,
    total_alerts=total_alerts,
    good_posture_percentage=good_posture_percentage,
    confidence_analysis_plot=confidence_analysis_plot,
    alerts_per_session_plot=alerts_per_session_plot,
    session_history_table=session_history_table,
    session_dropdown=session_dropdown,
    session_details=session_details,
    session_breakdown_plot=session_breakdown_plot,
)
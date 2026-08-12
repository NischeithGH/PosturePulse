from __future__ import annotations

from pathlib import Path

import gradio as gr

from hardware.setup import start_gpio
from models.registry import MODEL_POSE
from ui.context import AppContext
from ui.history import HistoryStore
from ui.inference_handlers import InferenceHandlers
from ui.input_handlers import InputHandlers
from ui.input_section import build_input_section
from ui.model_section import build_model_section
#from ui.model_section import model_to_tab_id, tab_value_to_model
from ui.output_section import build_output_section
from ui.debug_page import build_debug_page
from ui.debug_handlers import DebugHandlers
from gradio.themes import Soft
from ui.data_page import build_data_page
from ui.data_handlers import DataHandlers
from ui.about_page import build_about_page


def _wire_callbacks(inp, model, out, input_handlers, inference, history) -> None:
    inp.shutdown_button.click(
        fn=inference.shutdown_now,
        inputs=None,
        outputs=[out.status_output],
        show_progress="hidden",
    )

    inp.target_fps.change(
        fn=input_handlers.timer_interval_update,
        inputs=[inp.target_fps],
        outputs=[inp.timer],
        show_progress="hidden",
    )
    inp.timer.tick(
        fn=input_handlers.sync_video_preview,
        inputs=[
            inp.resolution,
            inp.input_source,
            inp.browser_webcam_input,
            inp.latest_capture_frame,
            inp.perf_state,
            inp.target_fps,
        ],
        outputs=[
            inp.input_preview,
            inp.camera_status_output,
            inp.latest_capture_frame,
            inp.perf_state,
        ],
        show_progress="hidden",
    )
    inp.input_source.change(
        fn=input_handlers.source_visibility,
        inputs=[inp.input_source],
        outputs=[
            inp.rpi_note,
            inp.upload_input,
            inp.browser_webcam_input,
            inp.input_preview,
            inp.camera_status_output,
            inp.resolution,
            inp.target_fps,
            model.analyze_btn,
            model.session_output,
            model.monitoring_toggle,
            model.monitoring_status,
        ],
        show_progress="hidden",
    )
    def continuous_pose(
        monitoring_enabled,
        source_type,
        latest_capture_rgb,
        upload_rgb,
        browser_webcam_rgb,
        ai_history,
        error_history,
    ):
            print("CONTINUOUS_POSE CALLED")
            if not (monitoring_enabled or inference._ctx.monitoring_enabled):
                return (
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                gr.update(),
                ai_history,
                error_history,
                gr.update(),
                gr.update(),
                *([gr.update()] * len(out.error_delete_buttons))
            )
        
            print("SOURCE TYPE =", source_type)
            if inference._ctx.monitoring_enabled:
                source_type ="rpi_camera"
            if source_type != "rpi_camera":
                return (
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    gr.update(),
                    ai_history,
                    error_history,
                    gr.update(),
                    gr.update(),
                    *([gr.update()] * len(out.error_delete_buttons))
                    )
            print("CALLING RUN_POSE")
    
            return inference.run_pose(
                source_type,
                latest_capture_rgb,
                upload_rgb,
                browser_webcam_rgb,
                ai_history,
                error_history,
        )
    

    # def on_model_tab(evt: gr.SelectData) -> str:
    #     return inference.sync_selected_model(tab_value_to_model(evt.value))

    # def on_gpio_model_radio(model: str) -> tuple[str, dict]:
    #     model_id = inference.sync_selected_model(model)
    #     return model_id, gr.Tabs(selected=model_to_tab_id(model_id))

    # model.model_tabs.select(on_model_tab, None, model.selected_model, show_progress="hidden")
    #     None,
    #     model.selected_model,
    #     show_progress="hidden",
    # )


    #     inputs=[
    #         inp.input_source,
    #         inp.latest_capture_frame,
    #         inp.upload_input,
    #         inp.browser_webcam_input,
    #         out.ai_history_state,
    #         out.error_history_state,
    #     ],
    #     outputs=[
    #         out.status_output,
    #         out.server_status_output,
    #         out.ai_history_state,
    #         out.error_history_state,
    #         out.ai_accordion_output,
    #         out.error_accordion_output,
    #         *out.error_delete_buttons,
    #     ],
    #     show_progress="hidden",
    # )
    model.monitoring_toggle.click(
    fn=inference.toggle_monitoring,
    inputs=[model.monitoring_enabled],
    outputs=[
        model.monitoring_enabled,
        model.monitoring_status,
        model.monitoring_toggle,
    ],
)
    
    model.analyze_btn.click(
    fn=inference.run_pose,
    inputs=[
        inp.input_source,
        inp.latest_capture_frame,
        inp.upload_input,
        inp.browser_webcam_input,
        out.ai_history_state,
        out.error_history_state,
    ],
    outputs=[
        model.pose_output,
        model.confidence_output,
        model.posture_output,
        model.session_output,
        out.status_output,
        out.server_status_output,
        out.ai_history_state,
        out.error_history_state,
        out.ai_accordion_output,
        out.error_accordion_output,
        *out.error_delete_buttons,
    ],
    show_progress="hidden",
)
    gr.Timer(value=0.5, active=True).tick(
    fn=continuous_pose,
    inputs=[
        model.monitoring_enabled,
        inp.input_source,
        inp.latest_capture_frame,
        inp.upload_input,
        inp.browser_webcam_input,
        out.ai_history_state,
        out.error_history_state,
    ],
outputs=[
    model.pose_output,
    model.confidence_output,
    model.posture_output,
    model.session_output,
    out.status_output,
    out.server_status_output,
    out.ai_history_state,
    out.error_history_state,
    out.ai_accordion_output,
    out.error_accordion_output,
    *out.error_delete_buttons,
],
    show_progress="hidden",
    )
    
    gr.Timer(value=1.0, active=True).tick(
    fn=inference.get_monitoring_status,
    inputs=None,
    outputs=[
        model.monitoring_enabled,
        model.monitoring_status,
        model.monitoring_toggle,
    ],
    show_progress="hidden",
)
    for idx, delete_button in enumerate(out.error_delete_buttons):
        delete_button.click(
            fn=lambda errors, idx=idx: history.delete_error_at_index(errors, idx),
            inputs=[out.error_history_state],
            outputs=[out.error_history_state, out.error_accordion_output, *out.error_delete_buttons],
            show_progress="hidden",
        )


def build_dashboard(ctx: AppContext) -> tuple[gr.Blocks, InferenceHandlers]:
    history = HistoryStore()
    input_handlers = InputHandlers(ctx)
    inference = InferenceHandlers(ctx, history)
    debug_handlers = DebugHandlers(ctx)
    data_handlers = DataHandlers()
    
    css1 = """
header {display:none !important;}
footer {display:none !important;}

.app-header{
    text-align:center;
    background:linear-gradient(135deg,#2563eb,#1d4ed8);
    color:white;
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}

.app-header h1{
    margin:0;
    font-size:32px;
    font-weight:700;
}

.app-header p{
    margin-top:10px;
    margin-bottom:0;
    font-size:24px;
    opacity:0.95;
}

.status-panel{
    background:white;
    border-radius:15px;
    padding:20px;
    text-align:center;
    box-shadow:0 2px 10px rgba(0,0,0,.08);
    margin-bottom:15px;
}

.status-panel h3{
    margin:0;
    font-size:16px;
}

.status-panel h2{
    margin-top:10px;
}

.metric-card{
    border-radius:15px !important;
}

.pi-card{
    background:white;
    border-radius:12px;
    padding:15px !important;
    border:1px solid #e5e7eb;
}

.stat-card{
    background:rgba(255,255,255,0.05);
    border:1px solid rgba(255,255,255,0.10);
    border-radius:16px;
    padding:16px;
    text-align:center;
    min-height:130px;
    box-shadow:0 2px 8px rgba(0,0,0,0.15);
}

.stat-card h1,
.stat-card h2,
.stat-card h3,
.stat-card p{
    margin:0;
}

.stat-card h2{
    margin-top:8px;
    margin-bottom:8px;
}

.gradio-dataframe{
    border-radius:12px !important;
}

.gr-plot{
    border-radius:12px !important;
}
    """

    with gr.Blocks(title="Posture Pulse",theme=Soft(primary_hue="blue",secondary_hue="blue"),head="""
    <script>
    if (!window.location.search.includes("__theme=")) {
        const url = new URL(window.location.href);
        url.searchParams.set("__theme", "light");
        window.location.replace(url.toString());
    }
    </script>
    """,css=css1) as demo:
        gr.HTML("""
            <div class="app-header">
                <h1>Posture Pulse</h1>
                <p>AI-Powered Real-Time Posture Monitoring System</p>
            </div>
            """)
        with gr.Tabs():
            with gr.Tab("About & Onboarding"):
                build_about_page()
                
            
            with gr.Tab("Operating"):
                inp = build_input_section(ctx.cfg)
                model = build_model_section()
                out = build_output_section()
            
            with gr.Tab("Data"):
                data = build_data_page()
            with gr.Tab("Debugging"):
                debug = build_debug_page()
        _wire_callbacks(inp, model, out, input_handlers, inference, history)
        demo.load(
            fn=input_handlers.source_visibility,
            inputs=[inp.input_source],
            outputs=[
                inp.rpi_note,
                inp.upload_input,
                inp.browser_webcam_input,
                inp.input_preview,
                inp.camera_status_output,
                inp.resolution,
                inp.target_fps,
                model.analyze_btn,
                model.session_output,
                model.monitoring_toggle,
                model.monitoring_status,
            ],
        )
        # demo.load(
        #     inputs=None,
        #     outputs=model.selected_model,
        #     show_progress="hidden",
        # )
        
        debug.led_green.click(fn=debug_handlers.test_green_led,outputs=[debug.debug_status],)
        debug.led_blue.click(fn=debug_handlers.test_blue_led,outputs=[debug.debug_status],)
        debug.led_red.click(fn=debug_handlers.test_red_led,outputs=[debug.debug_status],)
        debug.buzzer_test.click(fn=debug_handlers.buzzer_test,outputs=[debug.debug_status],)
        debug.lcd_test.click(fn=debug_handlers.lcd_test,inputs=[debug.lcd_text],outputs=[debug.debug_status],)
        debug.ultrasonic_test.click(fn=debug_handlers.ultrasonic_test,outputs=[debug.debug_status],)
        debug.pi_refresh.click(fn=debug_handlers.pi_info,outputs=[debug.pi_info],)
        debug.diagnostics_test.click(fn=debug_handlers.diagnostics_test,outputs=[debug.debug_status],)    
        data.refresh_button.click(
        fn=data_handlers.load_overview_statistics,
        inputs=None,
        outputs=[
            data.total_sessions,
            data.total_time,
            data.average_duration,
            data.total_alerts,
            data.good_posture_percentage,
        ],
        show_progress="hidden",
    )
        
        demo.load(
        fn=data_handlers.load_overview_statistics,
        inputs=None,
        outputs=[
            data.total_sessions,
            data.total_time,
            data.average_duration,
            data.total_alerts,
            data.good_posture_percentage,
        ],
        show_progress="hidden",
    )

        data.refresh_button.click(
            fn=data_handlers.load_session_history,
            inputs=None,
            outputs=[
                data.session_history_table
            ],
            show_progress="hidden",
        )
        
        demo.load(
    fn=data_handlers.load_session_history,
    inputs=None,
    outputs=[
        data.session_history_table
    ],
    show_progress="hidden",
    )
        demo.load(
        fn=data_handlers.load_session_dropdown,
        inputs=None,
        outputs=data.session_dropdown,
    )
        
        data.session_dropdown.change(
        fn=data_handlers.load_session_details,
        inputs=data.session_dropdown,
        outputs=data.session_details,
    )
    
        data.session_dropdown.change(
        fn=data_handlers.load_session_breakdown_plot,
        inputs=data.session_dropdown,
        outputs=data.session_breakdown_plot,
    )
        demo.load(
        fn=data_handlers.load_session_breakdown_plot,
        inputs=data.session_dropdown,
        outputs=data.session_breakdown_plot,
    )
        
        data.refresh_button.click(
    fn=data_handlers.load_posture_distribution_plot,
    inputs=None,
    outputs=data.confidence_analysis_plot,
    )
    
        demo.load(
        fn=data_handlers.load_posture_distribution_plot,
        inputs=None,
        outputs=data.confidence_analysis_plot,
    )
    
        data.refresh_button.click(
        fn=data_handlers.load_alerts_per_session_plot,
        inputs=None,
        outputs=data.alerts_per_session_plot,
    )
    
        demo.load(
        fn=data_handlers.load_alerts_per_session_plot,
        inputs=None,
        outputs=data.alerts_per_session_plot,
    )
        
    ctx.gpio, ctx.buzzer,ctx.led = start_gpio(
        ctx.cfg,
        on_short_press=inference.on_gpio_short_press,
        on_hold_press=inference.shutdown_now,
    )
    return demo, inference


def launch_dashboard(ctx: AppContext, demo: gr.Blocks) -> None:
    demo.queue().launch(
        server_name=ctx.cfg.gradio_host,
        server_port=ctx.cfg.gradio_port,
        show_error=True,
        allowed_paths=[str(Path(__file__).resolve().parent / "assets")]
    )

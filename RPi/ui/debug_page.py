from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


@dataclass
class DebugPage:
    led_green: gr.Button
    led_blue: gr.Button
    led_red: gr.Button
    buzzer_test: gr.Button

    lcd_text: gr.Textbox
    lcd_test: gr.Button
    ultrasonic_test: gr.Button

    pi_info: gr.Markdown
    pi_refresh: gr.Button

    diagnostics_test: gr.Button

    debug_status: gr.Textbox


def build_debug_page() -> DebugPage:

    with gr.Column():

        gr.Markdown("## Hardware Diagnostics")
        gr.HTML("""
            <div style="
            display:flex;
            justify-content:space-around;
            padding:15px;
            background:white;
            border-radius:12px;
            margin-bottom:15px;
            ">
            <div>📷 Camera</div>
            <div>💡 RGB LED</div>
            <div>📟 LCD</div>
            <div>🔊 Buzzer</div>
            <div>📏 Ultrasonic</div>
            </div>
            """)

        # Row 1: LED Tests
        gr.Markdown("#### LED Tests")
        with gr.Row():
            led_green = gr.Button(
                "🟢 Test Green LED",
                variant="secondary",
            )

            led_blue = gr.Button(
                "🔵 Test Blue LED",
                variant="secondary",
            )

            led_red = gr.Button(
                "🔴 Test Red LED",
                variant="secondary",
            )

        # Row 2: LCD Message Input
        gr.Markdown("#### LCD Display")
        with gr.Row():
            lcd_text = gr.Textbox(
                label="Message to Display",
                placeholder="Type your message here...",
                value="",
                max_lines=1,
            )
            lcd_test = gr.Button(
                "📟 Send to LCD",
                variant="secondary",
            )

        # Row 3: Other Hardware Tests
        gr.Markdown("#### Other Hardware")
        with gr.Row():
            buzzer_test = gr.Button(
                "🔊 Test Buzzer",
                variant="secondary",
            )

            ultrasonic_test = gr.Button(
                "📏 Read Distance",
                variant="secondary",
            )

        # Row 4: Pi Status
        gr.Markdown("#### 🖥 Raspberry Pi Status")
        with gr.Row():
            pi_info = gr.Markdown(elem_classes=["pi-card"])

        with gr.Row():
            pi_refresh = gr.Button(
                "Refresh Pi Status",
                variant="primary",
            )

        # Row 5
        diagnostics_test = gr.Button(
            "Run Full Diagnostics",
            variant="primary",
        )

        # Row 6
        debug_status = gr.Textbox(
            label="Diagnostics Console",
            lines=8,
            value="System Ready",
            interactive=False,
        )

    return DebugPage(
        led_green=led_green,
        led_blue=led_blue,
        led_red=led_red,
        buzzer_test=buzzer_test,
        lcd_text=lcd_text,
        lcd_test=lcd_test,
        ultrasonic_test=ultrasonic_test,
        pi_info=pi_info,
        pi_refresh=pi_refresh,
        diagnostics_test=diagnostics_test,
        debug_status=debug_status,
    )
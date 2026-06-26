from shiny import App, ui, reactive, render
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

from tabs.chatbot import chatbot_ui, chatbot_server
from tabs.visualizations import viz_ui, viz_server
from tabs.collection import collection_ui, collection_server

load_dotenv(Path(__file__).parent.parent.parent / ".env")

ENV_USER = os.getenv("APP_USERNAME")
ENV_PASS = os.getenv("APP_PASSWORD")

FOOTER = ui.p(
    ui.HTML("""
        Kendama Collection | Author: Harrison Li | 
        Repository: <a href="https://github.com/Harrisonlee0530/kendama" target="_blank">https://github.com/Harrisonlee0530/kendama</a> | 
        Last updated: 2026-03-05
        """),
    class_="text-center text-muted",
    style="margin-top: 2rem; padding: 1rem; border-top: 1px solid #eee;",
)


# ---- UI ----
app_ui = ui.page_navbar(
    viz_ui(), chatbot_ui(), collection_ui(), title="Kendama Collection Dashboard"
)


# ---- Server ----
def server(input, output, session):
    ui.modal_show(
        ui.modal(
            ui.input_text("username", "Username"),
            ui.input_password("password", "Password"),
            ui.output_text("error_text"),
            title="Login Required",
            footer=ui.input_action_button("login_btn", "Log In", class_="btn-primary"),
            easy_close=False,  # Prevents clicking outside to close it
        )
    )

    # 2. Check credentials when clicking "Log In"
    @reactive.effect
    @reactive.event(input.login_btn)
    def check_credentials():
        if input.username() == ENV_USER and input.password() == ENV_PASS:
            ui.modal_remove()  # Closes popup and lets them see the dashboard
        else:
            @output
            @render.text
            def error_text():
                return "Incorrect username or password."

    viz_server(input, output, session)
    chatbot_server(input, output, session)
    collection_server(input, output, session)


# ---- App ----
app = App(app_ui, server)

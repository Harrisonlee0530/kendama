from shiny import App, ui, reactive, render
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

from tabs.chatbot import chatbot_ui, chatbot_server
from tabs.visualizations import viz_ui, viz_server
from tabs.collection import collection_ui, collection_server

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

    viz_server(input, output, session)
    chatbot_server(input, output, session)
    collection_server(input, output, session)


# ---- App ----
app = App(app_ui, server)

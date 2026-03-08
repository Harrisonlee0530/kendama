"""
AI Chatbot Tab for the Kendama Collection Dashboard.

This module contains the querychat-powered AI tab which allows users to
filter collection using natural language queries.

Setup: 
Requires a .env file in the project root with the following key:
    GITHUB_TOKEN=your_github_token_here
"""


from pathlib import Path
from shiny import ui, render
import querychat
from chatlas import ChatGithub
from dotenv import load_dotenv
import pandas as pd

# Load API keys from .env (project root)
# .env should exist at the root of the directory, not inside src/
load_dotenv(Path(__file__).parent.parent / ".env")

raw_data = pd.read_csv("data/kendama_collection.csv")

qc = querychat.QueryChat(
    raw_data.copy(),
    "kendama_collection",
    greeting="""
This dataset keeps tracks of kendama related collections I purchased or 
received. 

You can ask questions about prices, brands, woods, purchases, or event prizes I have.

* <span class="suggestion">What is the average price of my kendamas?</span>
* <span class="suggestion">Which items were obtained at Van Jam events?</span>
* <span class="suggestion">List kendamas made from Maple or Beech</span>
* <span class="suggestion">What items were prizes from events?</span>
* <span class="suggestion">What did I buy from Kendama Depot?</span>
""",
    data_description="""
This dataset records a personal collection of kendamas and related skill toys.

Each row represents an item acquired through purchase, event prizes, or gifts. Items may be complete kendamas, individual parts (ken or tama), or other related objects such as juggling props or accessories.

Key fields include:

- product_name: Name or model of the item.
- brand: Brand or maker of the kendama or item.
- wood: Wood type used for the ken or tama when available.
- ken_weight_g: Weight of the ken (handle) in grams.
- tama_weight_g: Weight of the tama (ball) in grams.
- price: Price paid for the item.
- currency: Currency used for the purchase (CAD, USD, JPY, TWD, EUR).
- purchased_date: Date the item was acquired.
- purchased_from: Store, vendor, or event booth where it was obtained.
- order_id: Order number if purchased online.
- event: Event where the item was obtained (e.g., Van Jam, KWC).
- prize: Indicates whether the item was won as a prize.
- kendama: Indicates whether the item is a complete kendama.
- ken_only: Indicates the item is only a ken.
- tama_only: Indicates the item is only a tama.
- other: Indicates non-kendama items such as accessories or other skill toys.
- comment: Additional notes such as shipping, materials, or prize context.

The dataset allows analysis of collecting trends, spending, event prizes, brand distribution, and equipment characteristics such as wood types and weights.
""",
    client=ChatGithub(model="gpt-4.1-mini"),    
)

FOOTER = ui.p(
    ui.HTML(
        """
        Kendama Collection | Author: Harrison Li | 
        Repository: <a href="https://github.com/Harrisonlee0530/kendama" target="_blank">https://github.com/Harrisonlee0530/kendama</a> | 
        Last updated: 2026-03-05
        """
    ),
    class_="text-center text-muted",
    style="margin-top: 2rem; padding: 1rem; border-top: 1px solid #eee;"
)
    

def chatbot_ui():
    """
    Return the AI Assistant nav_panel to be added to page_navbar in app.py

    Contains the querychat sidebar for natural language filtering, a download
    button to export the filtered data as CSV, and a dataframe card showing 
    the current filtered dataset. 
    """
    return ui.nav_panel(
        "AI Chatbot",
        ui.layout_sidebar(
            qc.sidebar(),
            ui.download_button("download_data", "Download filtered data as CSV"),
            ui.card(
                ui.card_header(ui.output_text("chatbot_title")),
                ui.output_data_frame("chatbot_table"),
                full_screen=True,
            ),
            fillable=True,
        ),
        FOOTER,
    )


def chatbot_server(input, output, session):
    """
    Register all server-side logic for the AI Chatbot tab.

    Calls qc.server() to initialize the querychat reactive values, then
    wires up the dataframe output, the card title, and the CSV download
    handler. Returns qc_vals so callers can access the filtered dataframe.

    Parameters
    ----------
    input, output, session: Shiny session objects
        Passed in from the main server() function in app.py

    Returns
    -------
    qc_vals: querychat reactive values
        Exposes qc_vals.df() (filtered dataframe) and qc_vals.title()
        for use in app.py if needed.
    """
    qc_vals = qc.server()

    @render.text
    def chatbot_title():
        return qc_vals.title() or "Kendama Collections"
    
    @render.data_frame
    def chatbot_table():
        return qc_vals.df()
    
    @render.download(filename="kendama_collection_filtered.csv")
    def download_data():
        yield qc_vals.df().to_csv(index=False)
    
    # Expose qc_vals so app.py can use the filtered df
    return qc_vals
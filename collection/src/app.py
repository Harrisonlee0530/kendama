from shiny import App, ui, reactive, render
import pandas as pd
import os
from datetime import date
from chatbot import chatbot_ui, chatbot_server
from vizualizations import viz_ui, viz_server
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

CSV_FILE = "data/kendama_collection.csv"

# ---- Expected columns ----
COLUMNS = [
    "product_name",
    "brand",
    "wood",
    "ken_weight_g",
    "tama_weight_g",
    "price",
    "currency",
    "purchased_date",
    "purchased_from",
    "order_id",
    "event",
    "prize",
    "kendama",
    "ken_only",
    "tama_only",
    "other",
    "comment",
]

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


# ---- Load existing data if file exists ----
if os.path.exists(CSV_FILE):
    df_initial = pd.read_csv(CSV_FILE, parse_dates=["purchased_date"])
else:
    df_initial = pd.DataFrame(columns=COLUMNS)

# ---- UI ----
app_ui = ui.page_navbar(
    viz_ui(), 
    chatbot_ui(), 
    ui.nav_panel(
        "Collection",
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_text("product_name", "Product Name"),
                ui.input_text("brand", "Brand"),
                ui.input_text("wood", "Wood Type"),
                ui.hr(),
                ui.h5("Category"),
                ui.input_radio_buttons(
                    "category",
                    None,
                    choices={
                        "kendama": "Full Kendama",
                        "ken_only": "Ken Only",
                        "tama_only": "Tama Only",
                        "other": "Other",
                    },
                    selected="kendama",
                ),
                ui.hr(),
                ui.input_numeric("ken_weight_g", "Ken Weight (g)", value=None),
                ui.input_numeric("tama_weight_g", "Tama Weight (g)", value=None),
                ui.input_numeric("price", "Price", value=None),
                ui.input_text("currency", "Currency (e.g. USD, CAD, JPY, TWD)"),
                ui.input_date(
                    "purchased_date",
                    "Purchased Date",
                    value=date.today(),
                    format="yyyy-mm-dd",
                ),
                ui.hr(),
                ui.input_text("purchased_from", "Purchased From"),
                ui.input_text("order_id", "Order ID"),
                ui.hr(),
                ui.input_text("event", "Event (if applicable)"),
                ui.input_checkbox("prize", "Prize Item"),
                ui.hr(),
                ui.input_text_area("comment", "Comment", rows=3),
                ui.br(),
                ui.input_action_button(
                    "add", "Add to Collection", class_="btn-primary"
                ),
                ui.br(),
                ui.download_button("download_csv", "Download CSV"),
                ui.br(),
                ui.input_action_button("deselect", "Deselect Row"),
                ui.input_action_button(
                    "delete", "Delete Selected Row", class_="btn-danger"
                ),
            ),
            ui.h4("Current Collection"),
            ui.output_data_frame("table"),
        ),
        FOOTER, 
    ),
    title="Kendama Collection Dashboard"
)


# ---- Server ----
def server(input, output, session):

    viz_server(input, output, session)
    chatbot_server(input, output, session)

    data = reactive.Value(df_initial)

    # add row
    @reactive.effect
    @reactive.event(input.add)
    def add_row():
        new_row = pd.DataFrame(
            [
                {
                    "product_name": input.product_name(),
                    "brand": input.brand(),
                    "kendama": input.category() == "kendama",
                    "ken_only": input.category() == "ken_only",
                    "tama_only": input.category() == "tama_only",
                    "other": input.category() == "other",
                    "ken_weight_g": input.ken_weight_g(),
                    "tama_weight_g": input.tama_weight_g(),
                    "price": input.price(),
                    "currency": input.currency(),
                    "purchased_date": input.purchased_date(),
                    "purchased_from": input.purchased_from(),
                    "order_id": input.order_id(),
                    "event": input.event(),
                    "prize": input.prize(),
                    "comment": input.comment(),
                }
            ]
        )

        updated_df = pd.concat([data(), new_row], ignore_index=True)
        data.set(updated_df)
        updated_df.to_csv(CSV_FILE, index=False)

    # delete Selected Row
    @reactive.effect
    @reactive.event(input.delete)
    def delete_row():
        selected = list(input.table_selected_rows())
        # print(selected)
        if selected:
            df = data()
            df = df.drop(selected).reset_index(drop=True)
            data.set(df)
            df.to_csv(CSV_FILE, index=False)

    # render table
    @output
    @render.data_frame
    def table():
        _ = input.deselect()
        rendered_df = data().copy()
        rendered_df["purchased_date"] = (
            rendered_df["purchased_date"].astype(str).str.replace(" 00:00:00", "")
        )
        return render.DataGrid(rendered_df, selection_mode="rows")

    # save file
    @output
    @render.download(filename="kendama_collection.csv")
    def download_csv():
        output_data = data().copy()
        output_data["purchased_date"] = (
            output_data["purchased_date"].astype(str).str.replace(" 00:00:00", "")
        )
        yield output_data().to_csv(index=False)


# ---- App ----
app = App(app_ui, server)

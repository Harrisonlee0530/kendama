"""
Visualization Tab for the Kendama Collection Dashboard.
"""

import requests
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
from shiny import ui, render, reactive
from shinywidgets import render_altair, output_widget


raw_data = pd.read_csv("data/kendama_collection.csv")

raw_data["price"] = pd.to_numeric(raw_data["price"])
raw_data["brand"] = raw_data["brand"].fillna("Other")
raw_data["purchased_from"] = raw_data["purchased_from"].fillna("Other")

FOOTER = ui.p(
    ui.HTML(
        """
        Kendama Collection | Author: Harrison Li | 
        Repository: <a href="https://github.com/Harrisonlee0530/kendama" target="_blank">https://github.com/Harrisonlee0530/kendama</a> | 
        Last updated: 2026-03-05
        """
    ),
    class_="text-center text-muted",
    style="margin-top: 2rem; padding: 1rem; border-top: 1px solid #eee;",
)


def clean_for_altair(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make dataframe safe for Altair/Vega JSON serialization
    """
    df = df.copy()

    # Replace NaN / inf with None
    df = df.replace([np.nan, np.inf, -np.inf], None)
    return df


def convert_prices(df: pd.DataFrame, target: str) -> pd.Series:
    """
    Convert mixed-currency prices to a target currency.

    Parameters
    ----------
    df : DataFrame
        Must contain 'price' and 'currency'
    target : str
        Target ISO currency code

    Returns
    -------
    pd.Series
        Converted prices
    """
    url = f"https://open.er-api.com/v6/latest/{target}"
    rates = requests.get(url).json()["rates"]

    # map currency -> rate
    rate_series = df["currency"].map(rates)

    # convert prices
    return df["price"] / rate_series


BLUE_THEME = ui.tags.style(
    """
    :root {
        --primary-blue: #1f4fa3;
        --light-blue: #e8f1fb;
        --accent-blue: #3b82f6;
    }

    body {
        background-color: var(--light-blue);
    }

    .navbar {
        background-color: var(--primary-blue) !important;
    }

    .navbar-brand, .nav-link {
        color: white !important;
    }

    .card {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .card-header {
        background-color: var(--primary-blue);
        color: white;
        font-weight: 600;
    }

    .sidebar {
        background-color: white;
        border-right: 1px solid #e2e8f0;
    }

    .form-select {
        border-radius: 6px;
    }

    .value-box {
        background-color: white;
        border-left: 5px solid var(--accent-blue);
        padding: 12px;
        font-size: 20px;
        font-weight: 600;
    }

    footer {
        color: #64748b;
    }
    """
)


def viz_ui():

    return ui.nav_panel(
        "Homepage",
        BLUE_THEME, 
        ui.layout_sidebar(
            ui.sidebar(
                ui.input_select(
                    "target_currency",
                    "Target Currency",
                    choices=["CAD", "USD", "JPY", "TWD", "EUR"],
                    selected="CAD",
                )
            ),
            ui.div(
                # ----------------------
                # Summary statistics
                # ----------------------
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Total Collection Value"),
                        ui.output_text("total_value"),
                    ),
                    ui.card(
                        ui.card_header("Total Purchased Value (Excluding Prizes)"),
                        ui.output_text("total_value_no_prizes"),
                    ),
                ),
                # ----------------------
                # Row 1: Pie charts
                # ----------------------
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Brand Distribution"),
                        output_widget("brand_pie"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Vendor Distribution"),
                        output_widget("vendor_pie"),
                        full_screen=True,
                    ),
                ),
                # ----------------------
                # Row 2–3: Bar charts (2x2)
                # ----------------------
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Full Kendama Price Distribution"),
                        output_widget("kendama_price_bar"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Ken Only Price Distribution"),
                        output_widget("ken_price_bar"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Tama Only Price Distribution"),
                        output_widget("tama_price_bar"),
                        full_screen=True,
                    ),
                    ui.card(
                        ui.card_header("Other Item Price Distribution"),
                        output_widget("other_price_bar"),
                        full_screen=True,
                    ),
                    col_widths=[3, 3, 3, 3],
                ),
            ),
            fillable=True,
        ),
        FOOTER,
    )


def viz_server(input, output, session):

    # -----------------------------
    # Currency conversion
    # -----------------------------
    @reactive.calc
    def data_converted():
        df = raw_data.copy()
        target = input.target_currency()
        df["price_target"] = convert_prices(df, target).round(2)
        df = clean_for_altair(df)
        return df

    # -----------------------------
    # Summary statistics
    # -----------------------------
    @output
    @render.text
    def total_value():
        df = data_converted()

        total = df["price_target"].dropna().sum()
        currency = input.target_currency()

        return f"{total:,.2f} {currency}"

    @output
    @render.text
    def total_value_no_prizes():
        df = data_converted()

        total = df[df["prize"] != True]["price_target"].dropna().sum()

        currency = input.target_currency()

        return f"{total:,.2f} {currency}"

    # -----------------------------
    # Brand Pie Chart
    # -----------------------------
    @render_altair
    def brand_pie():
        df = data_converted()
        brand = (
            df["brand"]
            .fillna("Other")
            .replace("", "Other")
            .value_counts()
            .reset_index()
        )
        brand.columns = ["brand", "count"]

        return (
            alt.Chart(brand)
            .mark_arc()
            .encode(
                theta="count",
                color="brand",
                tooltip=["brand", "count"],
            )
        )

    # -----------------------------
    # Vendor Pie Chart
    # -----------------------------
    @render_altair
    def vendor_pie():
        df = data_converted()
        vendor = (
            df["purchased_from"]
            .fillna("Other")
            .replace("", "Other")
            .value_counts()
            .reset_index()
        )
        vendor.columns = ["vendor", "count"]

        return (
            alt.Chart(vendor)
            .mark_arc()
            .encode(
                theta="count",
                color="vendor",
                tooltip=["vendor", "count"],
            )
        )

    # -----------------------------
    # Helper for bar charts
    # -----------------------------
    def price_bar(df):
        df = df.dropna(subset=["price_target"])
        df = df[["price_target"]]

        return (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("price_target:Q", bin=True, title="Price"),
                y="count()",
                tooltip=["count()"],
            )
        )

    # -----------------------------
    # Full Kendama
    # -----------------------------
    @render_altair
    def kendama_price_bar():
        df = data_converted()
        subset = df[df["kendama"] == True]

        return price_bar(subset)

    # -----------------------------
    # Ken Only
    # -----------------------------
    @render_altair
    def ken_price_bar():
        df = data_converted()
        subset = df[df["ken_only"] == True]

        return price_bar(subset)

    # -----------------------------
    # Tama Only
    # -----------------------------
    @render_altair
    def tama_price_bar():
        df = data_converted()
        subset = df[df["tama_only"] == True]

        return price_bar(subset)

    # -----------------------------
    # Other Items
    # -----------------------------
    @render_altair
    def other_price_bar():
        df = data_converted()
        subset = df[df["other"] == True]

        return price_bar(subset)

from datetime import datetime
from pathlib import Path

import faicons
import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import shiny.experimental as x
from ipyleaflet import DivIcon, basemaps
from shiny import reactive, ui, App
from shinywidgets import output_widget, render_widget

from plotly_streaming import render_plotly_streaming



# --- Define property type categories once ---
property_types = ["Composite", "Detached", "Semi-Detached", "Townhouse", "Apartment"]

# --- Map property types to indices for color assignment ---
property_colors = {
    "Composite": 0,
    "Detached": 1,
    "Semi-Detached": 2,
    "Townhouse": 3,
    "Apartment": 4,
}
BASE_PATH = Path(__file__).resolve().parent


def read_housing_data():
    """Load housing CSV and preprocess dates and normalized location names."""

    # Use BASE_PATH instead of redefining it
    csv_path = BASE_PATH / "data" / "Toronto 2015-2025 - MLS_Google_MLS_FULL.csv"
    df = pd.read_csv(csv_path)

    # Ensure Date column is datetime
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Year"] = df["Date"].dt.year

    # Normalize location names
    df["Location_norm"] = (
        df["Location"].astype(str)
        .str.lower()
        .str.replace(r"^(city of |town of |township of )", "", regex=True)
        .str.strip()
    )

    # Clean column names of leading/trailing spaces
    df.columns = df.columns.str.strip()

    return df



category_colors = {
    "Apartment": 0,
    "Townhouse": 1,
    "Semi-Detached": 2,
    "Detached": 3,
    "Composite": 4,   # 👈 add this
}

def get_color_theme(theme, list_categories=None):

    global list_colors
    if theme == "Custom":
        list_colors = [
            "#F6AA54",
            "#2A5D78",
            "#9FDEF1",
            "#B9E52F",
            "#E436BB",
            "#6197E2",
            "#863CFF",
            "#30CB71",
            "#ED90C7",
            "#DE3B00",
            "#25F1AA",
            "#C2C4E3",
            "#33AEB1",
            "#8B5011",
            "#A8577B",
        ]
    elif theme == "RdBu":
        list_colors = px.colors.sequential.RdBu.copy()
        del list_colors[5]  # Remove color position 5
    elif theme == "GnBu":
        list_colors = px.colors.sequential.GnBu
    elif theme == "RdPu":
        list_colors = px.colors.sequential.RdPu
    elif theme == "Oranges":
        list_colors = px.colors.sequential.Oranges
    elif theme == "Blues":
        list_colors = px.colors.sequential.Blues
    elif theme == "Reds":
        list_colors = px.colors.sequential.Reds
    elif theme == "Hot":
        list_colors = px.colors.sequential.Hot
    elif theme == "Jet":
        list_colors = px.colors.sequential.Jet
    elif theme == "Rainbow":
        list_colors = px.colors.sequential.Rainbow

    if list_categories is not None:
        final_list_colors = [
            list_colors[category_colors[category] % len(list_colors)]
            for category in list_categories
        ]
    else:
        final_list_colors = list_colors

    return final_list_colors


def get_color_template(mode):
    if mode == "light":
        return "plotly_white"
    else:
        return "plotly_dark"


def get_background_color_plotly(mode):
    if mode == "light":
        return "white"
    else:
        return "rgb(29, 32, 33)"


def get_map_theme(mode):
    print(mode)
    if mode == "light":
        return basemaps.CartoDB.Positron
    else:
        return basemaps.CartoDB.DarkMatter


def create_custom_icon(count):

    size_circle = 45 + (count / 10)

    # Define the HTML code for the icon
    html_code = f"""
    <div style=".leaflet-div-icon.background:transparent !important;
        position:relative; width: {size_circle}px; height: {size_circle}px;">
        <svg width="{size_circle}" height="{size_circle}" viewBox="0 0 42 42"
            class="donut" aria-labelledby="donut-title donut-desc" role="img">
            <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954"
                fill="white" role="presentation"></circle>
            <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954"
                fill="transparent" stroke="color(display-p3 0.9451 0.6196 0.2196)"
                stroke-width="3" role="presentation"></circle>
            <text x="50%" y="60%" text-anchor="middle" font-size="13"
                font-weight="bold" fill="#000">{count}</text>
        </svg>
    </div>
    """

    # Create a custom DivIcon
    return DivIcon(
        icon_size=(50, 50), icon_anchor=(25, 25), html=html_code, class_name="dummy"
    )


app_ui = ui.page_fillable(
    ui.page_navbar(
        ui.nav_panel(
            "Dashboard",
            ui.row(
                ui.layout_columns(
                    ui.value_box(
                        title="Total Listings",
                        showcase=faicons.icon_svg(
                            "people-group", width="50px", fill="#FD9902 !important"
                        ),
                        value=len(read_housing_data()),
                    ),
                    ui.value_box(
                        title="Locations",
                        showcase=faicons.icon_svg(
                            "globe", width="50px", fill="#FD9902 !important"
                        ),
                        value=read_housing_data()["Location"].nunique(),
                    ),
                    ui.value_box(
                        title="Housing Types",
                        showcase=faicons.icon_svg(
                            "list", width="50px", fill="#FD9902 !important"
                        ),
                        value=5,
                    ),
                    ui.value_box(
                        title="Time Periods (Monthly)",
                        showcase=faicons.icon_svg(
                            "calendar", width="50px", fill="#FD9902 !important"
                        ),
                        value=read_housing_data()["Date"].nunique(),

                    ),
                    col_widths=(3, 3, 3, 3),
                ),
            ),
            ui.row(
                ui.layout_columns(
                    x.ui.card(output_widget("plot_0")),
                    x.ui.card(output_widget("plot_1")),
                    x.ui.card(output_widget("plot_2")),
                    col_widths=(4, 4, 4),
                ),
            ),
            ui.row(
                ui.layout_columns(
                    x.ui.card(output_widget("plot_3")),
                    x.ui.card(output_widget("plot_4")),
                    col_widths=(6, 6),
                ),
            ),
        ),
        ui.nav_panel(
            "Map",
            ui.row(
                ui.card(
                    output_widget("map_full"),
                    id="card_map",
                ),
            ),
        ),
        title=ui.img(src="images/housing-icon.png", style="max-width:100px;width:100%"),
        id="page",
        sidebar=ui.sidebar(
      ui.input_select(
                id="selected_year",
                label="Select Year",
                choices=[str(y) for y in range(2015, 2026)],  # 2015-2025
                selected="2025",
        ),

            ui.input_dark_mode(id="dark_mode", mode="light"),
            open="open",
        ),
        footer=ui.h6(
            f"Made by Yonatan Verch © {datetime.now().year}",
            style="color: white !important; text-align: center;",
        ),
        window_title="Toronto Housing Price Analysis (2015–2025)",
    ),
    ui.tags.style(
        """
        .collapse-toggle {
            color: #FD9902 !important;
        }
        .main {
            /* Background image */
            background-image: url("images/background_dark_full.png");
            height: 100%;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
        }
        div#map_full.html-fill-container {
              height: 600px !important;   /* or 100vh for full viewport height */
        }
        div#main_panel.html-fill-container {
            height: -webkit-fill-available !important;
        }
        """
    ),
    icon="images/favicon.ico",
)

## MAP ##


def server(input, output, session):

    # --- Step 2: Load housing data ---
    housing_df = read_housing_data()

    df_map = pd.read_csv(
        Path(__file__).parent / "data" / "location_coords.csv"
    )

    housing_df["Date"] = pd.to_datetime(housing_df["Date"])
    housing_df["Year"] = housing_df["Date"].dt.year

    # --- Step 3: Merge housing counts with shapefile coordinates ---
    housing_by_region = (
        housing_df.groupby("Location")  # use the correct column
        .size()
        .reset_index(name="count")
        .rename(columns={"Location": "NAME"})  # match the shapefile NAME column
    )


    base_path = Path(__file__).parent

    df_map = pd.read_csv(base_path / "data" / "location_coords.csv")
    housing_df = pd.read_csv(base_path / "data" / "Toronto 2015-2025 - MLS_Google_MLS_FULL.csv")
    housing_df["Date"] = pd.to_datetime(housing_df["Date"])
    housing_df["Year"] = housing_df["Date"].dt.year

    # Precompute avg benchmark per location for all years
    precomputed_avg = {}

    for year in housing_df['Year'].unique():
        housing_year = housing_df[housing_df["Year"] == year]
        avg_year = housing_year.groupby("Location", as_index=False)[[
            "CompBenchmark", "SFDetachBenchmark", "SFAttachBenchmark",
            "THouseBenchmark", "ApartBenchmark"
        ]].mean().fillna(0)

        # Convert to dictionary for faster lookup
        precomputed_avg[year] = avg_year.set_index("Location").to_dict('index')

    @reactive.Calc
    @output
    @render_widget
    def map_full():
        from ipyleaflet import Map, Marker, Popup
        from ipywidgets import HTML

        selected_year = int(input.selected_year())
        year_data = precomputed_avg.get(selected_year, {})

        map_widget = Map(center=(43.7, -79.4), zoom=9, scroll_wheel_zoom=True)

        for _, row in df_map.iterrows():
            lat, lon, name = row["LAT"], row["LON"], row["Location"]
            loc_data = year_data.get(name)

            if loc_data:
                table_html = "<table>"
                table_html += f"<tr><th>Property Type</th><th>Avg Benchmark Price {selected_year}</th></tr>"
                table_html += f"<tr><td>Composite</td><td>${loc_data['CompBenchmark']:,.0f}</td></tr>"
                table_html += f"<tr><td>Detached</td><td>${loc_data['SFDetachBenchmark']:,.0f}</td></tr>"
                table_html += f"<tr><td>Semi-Detached</td><td>${loc_data['SFAttachBenchmark']:,.0f}</td></tr>"
                table_html += f"<tr><td>Townhouse</td><td>${loc_data['THouseBenchmark']:,.0f}</td></tr>"
                table_html += f"<tr><td>Apartment</td><td>${loc_data['ApartBenchmark']:,.0f}</td></tr>"
                table_html += "</table>"
            else:
                table_html = f"<i>No data available for {selected_year}</i>"

            marker = Marker(location=(lat, lon), draggable=False)
            popup_content = HTML(f"<b>{name}</b><br>{table_html}")
            popup = Popup(location=(lat, lon), child=popup_content, max_width=300)
            marker.popup = popup
            map_widget.add_layer(marker)

        return map_widget

    ## MAP ##

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_0():
        # Ensure Date is datetime
        housing_df["Date"] = pd.to_datetime(housing_df["Date"])

        # Use most recent date in dataset
        latest_date = housing_df["Date"].max()

        latest = housing_df[housing_df["Date"] == latest_date]

        # Average benchmark prices across locations
        composition = pd.DataFrame({
            "Property Type": [
                "Composite",
                "Detached",
                "Semi-Detached",
                "Townhouse",
                "Apartment"
            ],
            "Benchmark Value": [
                latest["CompBenchmark"].mean(),
                latest["SFDetachBenchmark"].mean(),
                latest["SFAttachBenchmark"].mean(),
                latest["THouseBenchmark"].mean(),
                latest["ApartBenchmark"].mean(),
            ]
        })

        fig0 = px.pie(
            composition,
            names="Property Type",
            values="Benchmark Value",
            hole=0.3,
            labels={
                "Benchmark Value": "Benchmark Price ($)"
            },
            title=f"Housing Market Composition by Property Type ({latest_date.year})",
            template=get_color_template(input.dark_mode()),
            color_discrete_sequence=get_color_theme("Custom")
        )

        fig0.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()),
            title_x=0.5,
        )

        fig0.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=15),
        )

        fig0.update_layout(showlegend=False)

        return fig0

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_2():
        # Ensure Date is datetime
        housing_df["Date"] = pd.to_datetime(housing_df["Date"])

        # Most recent date
        latest_date = housing_df["Date"].max()
        latest = housing_df[housing_df["Date"] == latest_date]

        # New metric: Price Spread (Max - Min) across locations
        composition = pd.DataFrame({
            "Property Type": [
                "Composite",
                "Detached",
                "Semi-Detached",
                "Townhouse",
                "Apartment"
            ],
            "Price Spread ($)": [
                latest["CompBenchmark"].max() - latest["CompBenchmark"].min(),
                latest["SFDetachBenchmark"].max() - latest["SFDetachBenchmark"].min(),
                latest["SFAttachBenchmark"].max() - latest["SFAttachBenchmark"].min(),
                latest["THouseBenchmark"].max() - latest["THouseBenchmark"].min(),
                latest["ApartBenchmark"].max() - latest["ApartBenchmark"].min()
            ]
        })

        fig0 = px.pie(
            composition,
            names="Property Type",
            values="Price Spread ($)",
            hole=0.3,
            labels={"Price Spread ($)": "Price Spread ($)"},
            title=f"Price Spread by Property Type ({latest_date.year})",
            template=get_color_template(input.dark_mode()),
            color_discrete_sequence=get_color_theme("Custom")
        )

        fig0.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()),
            title_x=0.5,
        )

        fig0.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=15),
        )

        fig0.update_layout(showlegend=False)

        return fig0



    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_1():
        # Ensure Date is datetime
        housing_df["Date"] = pd.to_datetime(housing_df["Date"])

        # Use most recent date in dataset
        latest_date = housing_df["Date"].max()
        latest = housing_df[housing_df["Date"] == latest_date]

        # Total market value per property type (sum of benchmarks across locations)
        composition = pd.DataFrame({
            "Property Type": [
                "Composite",
                "Detached",
                "Semi-Detached",
                "Townhouse",
                "Apartment"
            ],
            "Total Market Value ($)": [
                latest["CompBenchmark"].sum(),
                latest["SFDetachBenchmark"].sum(),
                latest["SFAttachBenchmark"].sum(),
                latest["THouseBenchmark"].sum(),
                latest["ApartBenchmark"].sum(),
            ]
        })

        fig = px.pie(
            composition,
            names="Property Type",
            values="Total Market Value ($)",
            hole=0.3,
            labels={"Total Market Value ($)": "Total Market Value ($)"},
            title=f"Total Market Value by Property Type ({latest_date.year})",
            template=get_color_template(input.dark_mode()),
            color_discrete_sequence=get_color_theme("Custom")
        )

        fig.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()),
            title_x=0.5,
        )

        fig.update_traces(
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=15),
        )

        fig.update_layout(showlegend=False)

        return fig

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_4():
        # Ensure Date is datetime
        housing_df["Date"] = pd.to_datetime(housing_df["Date"])

        # Most recent date
        latest_date = housing_df["Date"].max()
        latest = housing_df[housing_df["Date"] == latest_date]

        # Melt the dataframe to long format: Location x Property Type x Benchmark
        df_long = latest.melt(
            id_vars=["Location"],
            value_vars=[
                "CompBenchmark",
                "SFDetachBenchmark",
                "SFAttachBenchmark",
                "THouseBenchmark",
                "ApartBenchmark"
            ],
            var_name="Property Type",
            value_name="Benchmark Value"
        )

        # Clean Property Type names
        df_long["Property Type"] = df_long["Property Type"].replace({
            "CompBenchmark": "Composite",
            "SFDetachBenchmark": "Detached",
            "SFAttachBenchmark": "Semi-Detached",
            "THouseBenchmark": "Townhouse",
            "ApartBenchmark": "Apartment"
        })

        # Aggregate: average benchmark per location & property type
        df_counts = df_long.groupby(["Location", "Property Type"], as_index=False)["Benchmark Value"].mean()
        # 1️⃣ Compute total per location
        location_totals = df_counts.groupby('Location')['Benchmark Value'].sum()

        # 2️⃣ Keep only top N locations (e.g., top 10)
        top_locations = location_totals.sort_values(ascending=False).head(5).index
        df_counts_filtered = df_counts[df_counts['Location'].isin(top_locations)]

        # 3️⃣ Recompute total per location for text labels
        total_location = df_counts_filtered.groupby('Location', as_index=False)["Benchmark Value"].sum()

        # Create stacked bar chart
        fig3 = px.bar(
            df_counts,
            x="Location",
            y="Benchmark Value",
            color="Property Type",
            text="Benchmark Value",
            text_auto=".2s",
            labels={
                "Location": "Location",
                "Benchmark Value": "Average Benchmark Price ($)",
                "Property Type": "Property Type",
            },
            title="Average Benchmark Price by Property Type and Location (2025)",
            template=get_color_template(input.dark_mode()),
            color_discrete_sequence=get_color_theme("Custom")
        )

        fig3.update_traces(textposition="inside")

        # Add total benchmark per location on top
        fig3.add_trace(
            go.Scatter(
                x=total_location["Location"],
                y=total_location["Benchmark Value"],
                text=total_location["Benchmark Value"].round(0),
                mode="text",
                textposition="top center",
                textfont=dict(size=15),
                showlegend=False,
            )
        )

        fig3.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()),
            title_x=0.5,
            xaxis_tickangle=-45  # rotate labels 45° counterclockwise

        )
        fig3.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")
        fig3.update_yaxes(range=[0, max(total_location["Benchmark Value"]) * 1.1])

        return fig3

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def plot_3():
        # Ensure datetime
        housing_df["Date"] = pd.to_datetime(housing_df["Date"])
        housing_df["Year"] = housing_df["Date"].dt.year

        # Use a benchmark metric (Composite is safest)
        df_yearly = (
            housing_df
            .groupby(["Location", "Year"], as_index=False)["CompBenchmark"]
            .mean()
        )

        # Pick top 10 locations by latest year
        latest_year = df_yearly["Year"].max()
        top_locations = (
            df_yearly[df_yearly["Year"] == latest_year]
            .sort_values("CompBenchmark", ascending=False)
            .head(10)["Location"]
        )

        df_top = df_yearly[df_yearly["Location"].isin(top_locations)]

        fig = px.bar(
            df_top,
            x="Location",
            y="CompBenchmark",
            color="Year",
            barmode="group",  # <-- important for year comparison
            text_auto=".2s",
            labels={
                "Location": "Toronto Region",
                "CompBenchmark": "Average Benchmark Price ($)",
                "Year": "Year",
            },
            title="Top 10 Toronto Regions by Composite Benchmark Price (Yearly Comparison)",
            template=get_color_template(input.dark_mode()),
            color_discrete_sequence=get_color_theme("Custom")
        )

        fig.update_layout(
            paper_bgcolor=get_background_color_plotly(input.dark_mode()),
            title_x=0.5,
        )

        fig.update_layout(uniformtext_minsize=8, uniformtext_mode="hide")

        return fig


static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)

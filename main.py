import pandas as pd
from pandas.core.indexes.api import all_indexes_same

import DataHandling as dh
import Builder as b
from dash import Dash, dcc, html, Output, Input, State, ctx

# the amount of indexes allowed through the app:
max_displayed_indexes = 2
# the data handler
dh = dh.DataHandler()
# dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Well-being Index comparison around the world", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select up to 2 Indexes:", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="index-dropdown",
            options=[
                {"label": "Big Mac Index", "value": "BMI"},
                {"label": "Democracy Index", "value": "DIIndex"},
                {"label": "GDP", "value": "GDPValue"},
                {"label": "GDP Per Capita", "value": "GDPCapitaValue"},
                {"label": "Human Development Index", "value": "HDIValue"},
                {"label": "Life Expectancy Index", "value": "LifeExpectancy"},
            ],
            value=[],  # default empty selection
            multi=True,
            maxHeight=300,
            style={"width": "100%"}
        )
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "stretch",
        "padding": "10px",
        "width": "30% ",
        "margin": "0 auto"
    }),

    html.Div(
        dcc.Graph(id="world-map", figure=b.build_map(frames=b.build_map_info()), style={"width": "100%", "height": "100%"}),
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexDirection": "column",
            "width": "100%",
            "height": "80vh"
        }
    ),
    dcc.Dropdown(
        id="chart-selector",
        options=[
            {"label": "Line Chart", "value": "line"},
            {"label": "Bar Chart", "value": "bar"},
        ],
        value=None,
        placeholder="Select a chart to display"
    ),
    html.Div([
        dcc.Graph(id="line-chart"),
        html.Button("Reset Line Chart", id="reset-btn-line", n_clicks=0, className="plotly-btn")
    ],
    id="line-container",
    style={"display": "none"}
    ),
    html.Div(
        [
            dcc.Dropdown(
                id='year-selector-bar',
                options=[{'label': str(year), 'value': year} for year in dh.get_all_years()], #empty as well by default
                value=dh.get_all_years()[0],  # default no year values
                clearable=False,
                style={'width': '150px'}
            ),
            dcc.Graph(id="bar-chart"),
            html.Button("Reset Bar Chart", id="reset-btn-bar", n_clicks=0, className="plotly-btn")
        ],
        id="bar-container",
        style={"display": "none"}
    ),
    dcc.Store(id="selected_countries_line", data=["Denmark"]),
    dcc.Store(id="selected_countries_bar", data=["Denmark"]),
    dcc.Store(id="selected_indexes"),
    dcc.Store(id="merged_df")
])

@app.callback(
    Output("line-container", "style"),
    Output("bar-container", "style"),
    Input("chart-selector", "value")
)
def update_selected_charts(selected_chart):
    # Default hidden
    styles = [{"display": "none"}] * 2 # scale with charts

    if selected_chart == "line":
        styles[0] = {"display": "block"}
    elif selected_chart == "bar":
        styles[1] = {"display": "block"}

    return styles

@app.callback(
    Output("world-map", "figure"),
    Input("selected_indexes", "data"),
    Input("merged_df", "data"),
)
def update_map(selected_indexes, merged_df):
    merged_df = pd.read_json(merged_df, orient="split") if merged_df else pd.DataFrame()
    years = sorted(merged_df["year"].astype(int).unique()) if not merged_df.empty else []
    return b.build_map(frames=b.build_map_info(years, merged_df, selected_indexes), years=years)

@app.callback(
    Output("index-dropdown", "value"),              # updates UI display
    Output("selected_indexes", "data"),                 # updates internal selection store
    Output("merged_df", "data"),
    Input("index-dropdown", "value"),
)
def update_selected_indexes(index_dropdown):
    selected_indexes = index_dropdown[:max_displayed_indexes]
    merged_df = dh.get_merged_df(selected_indexes)
    return selected_indexes, selected_indexes, merged_df.to_json(date_format="iso", orient="split") #returns as much selected as much is allowed


# charts control callback
@app.callback(
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("selected_countries_line", "data"),
    Output("selected_countries_bar", "data"),
    Output("world-map", "clickData"),
    Output("year-selector-bar", "value"),
    Input("world-map", "clickData"),
    Input("reset-btn-line", "n_clicks"),
    Input("reset-btn-bar", "n_clicks"),
    Input("selected_indexes", "data"),
    Input("chart-selector", "value"),
    Input("year-selector-bar", "value"),
    State("merged_df", "data"),
    State("selected_countries_line", "data"),
    State("selected_countries_bar", "data"),
)
def update_charts(clickData, _, __, selected_indexes, selected_chart, selected_year_bar, merged_df, selected_countries_line, selected_countries_bar):
    # reverting JSON
    merged_df = pd.read_json(merged_df, orient="split") if merged_df else pd.DataFrame()

    # reset buttons
    if ctx.triggered_id == "reset-btn-line":
        selected_countries_line = ["Denmark"]
    if ctx.triggered_id == "reset-btn-bar":
        selected_countries_bar = ["Denmark"]
        selected_year_bar = dh.get_all_years()[0]
    # Click event
    elif clickData and "points" in clickData and len(clickData["points"]) > 0:
        country_clicked = clickData["points"][0]["customdata"][0]
        if selected_chart == "line":
            if country_clicked in selected_countries_line:
                selected_countries_line.remove(country_clicked)
            else:
                selected_countries_line.append(country_clicked)
        elif selected_chart == "bar":
            selected_countries_bar = [country_clicked]

    #updating charts
    if selected_chart == "line":
        return b.build_line_chart(selected_countries_line, selected_indexes, merged_df), None, selected_countries_line, selected_countries_bar, None, selected_year_bar
    elif selected_chart == "bar":
        return None, b.build_bar_chart(selected_countries_bar, selected_year_bar, dh.get_all_indexes(), dh.get_df_by_name("all")), selected_countries_line, selected_countries_bar, None, selected_year_bar
    else:
        return None, None, selected_countries_line, selected_countries_bar, None, selected_year_bar


if __name__ == "__main__":
    app.run(debug=False)

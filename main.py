import DataHandling as dh
import Builder as b
from dash import Dash, dcc, html, Output, Input, State, ctx

# the amount of indexes allowed through the app:
max_displayed_indexes = 2
#preload the data
merged_df = dh.get_merged_df()
#get the years
years = sorted(int(y) for y in merged_df["year"].unique())
all_indexes = ["price_adjusted", "DIIndex"]
# dash app
app = Dash(__name__)

app.layout = html.Div([
    # === HEADER ===
    html.H1("Well-being Index comparison around the world", style={"textAlign": "center"}),

    # === MIDDLE SECTION: LEFT (selector+buttons) + CENTER (map) ===
    html.Div([
        # LEFT COLUMN: Index Selector + Buttons
        html.Div([
            # Index selector
            html.Div([
                html.Label("Select up to 2 Indexes:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="index-dropdown",
                    options=[
                        {"label": "Big Mac Index", "value": "price_adjusted"},
                        {"label": "Democracy Index", "value": "DIIndex"},
                        {"label": "Test", "value": ""},
                    ],
                    value=[],
                    multi=True,
                    maxHeight=300,
                    style={"width": "100%"}
                )
            ], style={"marginBottom": "20px"}),

            # Buttons below
            html.Div([
                html.Button("▶ Play", id="play-button", n_clicks=0, className="rounded-btn"),
                html.Button("⏸ Pause", id="pause-button", n_clicks=0, className="rounded-btn"),
                html.Button("⟳ Reset", id="reset-button", n_clicks=0, className="rounded-btn"),
                dcc.Interval(id="interval", interval=1000, n_intervals=0, disabled=True)
            ], style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "flex-start",
                "justifyContent": "flex-start",
                "gap": "8px",
            })
        ], style={
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "flex-start",
            "justifyContent": "flex-start",
            "padding": "0px",
        }),

        # CENTER COLUMN: Map
        html.Div([
            dcc.Graph(
                id="world-map",
                figure=b.build_map(),
                style={"width": "100%", "height": "70vh"},
            )
        ], style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "flex-start"
        })
    ], style={
        "display": "grid",
        "gridTemplateColumns": "150px 1fr",  # left column fixed, map fills remaining space
        "gap": "10px",
        "alignItems": "start",
        "width": "100%",
        "marginBottom": "5px"
    }),

    # === YEAR SLIDER (full width below) ===
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=years[0],
            max=years[-1],
            value=years[0],
            marks={str(year): str(year) for year in years},
            step=None,
            tooltip={"placement": "bottom", "always_visible": True},
            updatemode='drag'
        )
    ], style={
        "width": "80%",
        "margin": "0 auto 30px auto"
    }),

    # === CHART SELECTOR (bottom) ===
    html.Div([
        html.Label("Select chart type:", style={"fontWeight": "bold", "marginBottom": "5px"}),
        dcc.Dropdown(
            id="chart-selector",
            options=[
                {"label": "Line Chart", "value": "line"},
                {"label": "Bar Chart", "value": "bar"},
            ],
            value=None,
            placeholder="Select a chart to display",
            style={"width": "40%", "margin": "0 auto"}
        ),
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "center",
        "marginBottom": "20px"
    }),

    # === CONDITIONAL CHART SECTIONS ===
    html.Div([
        dcc.Graph(id="line-chart"),
        html.Button("Reset Line Chart", id="reset-btn-line", n_clicks=0, className="plotly-btn")
    ], id="line-container", style={"display": "none"}),

    html.Div([
        dcc.Graph(id="bar-chart"),
        html.Button("Reset Bar Chart", id="reset-btn-bar", n_clicks=0, className="plotly-btn")
    ], id="bar-container", style={"display": "none"}),

    # === STORED DATA ===
    dcc.Store(id="selected_countries_line", data=["Denmark"]),
    dcc.Store(id="selected_countries_bar", data=["Denmark"]),
    dcc.Store(id="selected_indexes"),
])

@app.callback(
    Output("line-container", "style"),
    Output("bar-container", "style"),
    Input("chart-selector", "value")
)
def update_selected_charts(selected_chart):
    # Default hidden
    styles = [{"display": "none"}] * 2 #scale with charts

    if selected_chart == "line":
        styles[0] = {"display": "block"}
    elif selected_chart == "bar":
        styles[1] = {"display": "block"}

    return styles

@app.callback(
    Output("world-map", "figure"),
    Input("selected_indexes", "data"),
    Input('year-slider', 'value')
)
def update_map(selected_indexes, year):
    return b.build_map(frames=b.build_map_info(year, merged_df, selected_indexes))

@app.callback(
    Output("index-dropdown", "value"),              # updates UI display
    Output("selected_indexes", "data"),                 # updates internal selection store
    Input("index-dropdown", "value"),
)
def update_selected_indexes(selected_values):
    return selected_values[:max_displayed_indexes], selected_values[:max_displayed_indexes] #returns as much selected as much is allowed


# line chart callback
@app.callback(
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("selected_countries_line", "data"),
    Output("selected_countries_bar", "data"),
    Output("world-map", "clickData"),
    Input("world-map", "clickData"),
    Input("reset-btn-line", "n_clicks"),
    Input("reset-btn-bar", "n_clicks"),
    Input("selected_indexes", "data"),
    Input("chart-selector", "value"),
    Input("year-slider", "value"),
    State("selected_countries_line", "data"),
    State("selected_countries_bar", "data"),
)
def update_charts(clickData, _, __, selected_indexes, selected_chart, selected_year_bar, selected_countries_line, selected_countries_bar):
    if ctx.triggered_id == "reset-btn-line":
        selected_countries_line = ["Denmark"]
    if ctx.triggered_id == "reset-btn-bar":
        selected_countries_bar = ["Denmark"]
        selected_year_bar = years[0]
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

    if selected_chart == "line":
        return b.build_line_chart(selected_countries_line, selected_indexes, merged_df), None, selected_countries_line, selected_countries_bar, None
    elif selected_chart == "bar":
        return None, b.build_bar_chart(selected_countries_bar, selected_year_bar, all_indexes, merged_df), selected_countries_line, selected_countries_bar, None
    else:
        return None, None, selected_countries_line, selected_countries_bar, None


if __name__ == "__main__":
    app.run(debug=False)

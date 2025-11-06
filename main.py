import plotly.graph_objects as go
import DataHandling as dh
import Builder as b
import MetaData as md
from dash import Dash, dcc, html, Output, Input, State, ctx

# the amount of indexes allowed through the app:
max_displayed_indexes = 2
#preload the data
merged_df = dh.get_merged_df()
#get the years
years = sorted(int(y) for y in merged_df["year"].unique())

# dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Big Mac Index VS Democracy Ratings World Wide Comparison", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select up to 2 Indexes:", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="index-dropdown",
            options=[
                {"label": "Big Mac Index", "value": "price_adjusted"},
                {"label": "Democracy Index", "value": "DIIndex"},
                {"label": "Test", "value": ""},
            ],
            value=[],  # default selection
            multi=True,
            maxHeight=300,
            style={"width": "60%"}
        )
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "padding": "10px"
    }),

    html.Div(
        dcc.Graph(id="world-map", figure=b.build_map(years=years), style={"width": "100%", "height": "100%"}),
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexDirection": "column",
            "width": "100%",
            "height": "80vh"
        }
    ),
    dcc.Store(id="selected_countries", data=["Denmark"]),
    dcc.Store(id="selected_indices"),

    html.Div([
        dcc.Graph(id="line-chart"),
        html.Button("Reset Line Chart", id="reset-btn", n_clicks=0, className="plotly-btn")
    ])
])

@app.callback(
    Output("world-map", "figure"),
    Input("selected_indices", "data"),
)
def update_map(selected_indices):
    frames = []
    for year in years:
        dff = merged_df[merged_df["year"] == year]
        data = []

        # dynamic title text
        title_text = ''
        for i in range(len(selected_indices)):
            title_text += md.chart_names[selected_indices[i]]
            if i != len(selected_indices) - 1:
                title_text += " & "
            else:
                title_text += f' in {year}'

        # first selected index on the map
        if len(selected_indices) > 0 and selected_indices[0] in dff.columns:
            choropleth = go.Choropleth(
                locations=dff["country"],
                z=dff[selected_indices[0]],
                locationmode="country names",
                zmin=dff[selected_indices[0]].min(),
                zmax=dff[selected_indices[0]].max(),
                colorscale=md.colours[selected_indices[0]] + "s",
                marker_line_color="white",
                marker_line_width=0.5,
                hoverinfo="skip",
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=1)),
                showlegend=True,
                showscale=False,
                name = md.legend_names[selected_indices[0]],
            )
            data.append(choropleth)

        # every other index as bubis bublé
        for i in range(1, len(selected_indices)):
            if selected_indices[i] in dff.columns:
                bubbles = go.Scattergeo(
                    locations=dff["country"],
                    locationmode="country names",
                    mode="markers",
                    marker=dict(
                        size=dff[selected_indices[i]] * 5,
                        color=md.colours[selected_indices[i]],
                        opacity=0.5,
                        line=dict(width=0.7, color="white")
                    ),
                    hoverinfo="skip",
                    selected=dict(marker=dict(opacity=0.5)),
                    unselected=dict(marker=dict(opacity=0.5)),
                    name = md.legend_names[selected_indices[i]],
                    showlegend = True,
                )
                data.append(bubbles)

        #building custom data
        custom_data = ["country"]
        custom_data.extend(selected_indices)

        #building hover info
        hover_info = "Country: %{customdata[0]}<br>"
        for index in selected_indices:
            hover_info += md.chart_names[index] + " " + md.hover_data_1[index] + str(selected_indices.index(index) + 1) + md.hover_data_2[index] + "<br>"
        hover_info += "<extra></extra>"
        # an invisible marker per country so selection events are triggered reliably.
        scatter_text = go.Scattergeo(
            locations=dff["country"],
            locationmode="country names",
            mode="markers+text",
            marker=dict(size=20, opacity=0),  # invisible but selectable
            customdata=dff[custom_data].values,
            hovertemplate=hover_info, # also this invisible layer handles hoverinfo to make it consistent
            selected=dict(marker=dict(opacity=0)),
            unselected=dict(marker=dict(opacity=0)),
            showlegend=False,
        )
        data.append(scatter_text)

        frames.append(go.Frame(
            data=data,
            name=str(year),
            layout=go.Layout(
                title_text = title_text,
            )
        ))
    return b.build_map(frames=frames, years=years)

@app.callback(
    Output("index-dropdown", "value"),          # updates UI display
    Output("selected_indices", "data"),         # updates internal selection store
    Input("index-dropdown", "value"),
)
def update_selected_indexes(selected_values):
    return selected_values[:max_displayed_indexes], selected_values[:max_displayed_indexes]


# line chart callback
@app.callback(
    Output("line-chart", "figure"),
    Output("selected_countries", "data"),
    Output("world-map", "clickData"),
    Input("world-map", "clickData"),
    Input("reset-btn", "n_clicks"),
    Input("selected_indices", "data"),
    State("selected_countries", "data"),
)

def update_line_chart(clickData, _, selected_indices, selected_countries):
    if ctx.triggered_id == "reset-btn":
        selected_countries = ["Denmark"]
    # Click event
    elif clickData and "points" in clickData and len(clickData["points"]) > 0:
        country_clicked = clickData["points"][0]["customdata"][0]

        if country_clicked in selected_countries:
            selected_countries.remove(country_clicked)
        else:
            selected_countries.append(country_clicked)

    return b.build_line_chart(selected_countries, selected_indices), selected_countries, None



if __name__ == "__main__":
    app.run(debug=True)

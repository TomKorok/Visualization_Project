import plotly.graph_objects as go
import DataHandling as dh
import plotly.express as px
from dash import Dash, dcc, html, Output, Input, State, ctx

# the amount of indexes allowed through the app:
max_displayed_indexes = 2

# initial data load
DemocracyIndex = dh.LoadDemocracyIndex()
BigmacIndex = dh.LoadBigMacIndex()

# merging both datasets to have the same years and countries
MergedIndex = dh.MergeDataFrames(DemocracyIndex, BigmacIndex)

years = sorted(int(y) for y in MergedIndex["year"].unique())
# prefixed colour based on the column name in the MergedIndex
colours = {
    "price_adjusted": 'Red',
    "DIIndex" : 'Blue'
}
# prefixed legend names based on the column name in the MergedIndex
legend_names = {
    "price_adjusted": f"Big Mac Price [{MergedIndex["price_adjusted"].min():.2f} - {MergedIndex["price_adjusted"].max():.2f}]",
    "DIIndex": "Democracy Index [0 - 10]"
}
# prefixed chart names based on the column name in the MergedIndex
chart_names = {
    "price_adjusted": 'Big Mac Price',
    "DIIndex": "Democracy Index"
}
#prefixed data for hovering
hover_data_1 = {
    "price_adjusted": "%{customdata[",
    "DIIndex": "%{customdata["
}
hover_data_2 = {
    "price_adjusted": "]:.2f} USD",
    "DIIndex": "]:.2f}"
}

# initial map figure
def build_map(frames=None):
    return go.Figure(
        data= frames[0].data if frames is not None else None,
        frames=frames,
        layout=go.Layout(
            title=frames[0].layout.title.text if frames else "",
            clickmode="event+select",
            geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
            margin=dict(l=0, r=0, t=50, b=0),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                x=0.05, y=0.95,
                xanchor="left", yanchor="top",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 1000, "redraw": True},
                                     "fromcurrent": True,
                                     "transition": {"duration": 300, "easing": "linear"}}]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                       "mode": "immediate",
                                       "transition": {"duration": 0}}]
                    ),
                    dict(
                        label="Reset",
                        method="animate",
                        args=[[str(years[0])],
                              {"frame": {"duration": 500, "redraw": True},
                               "mode": "immediate",
                               "transition": {"duration": 300}}]
                    )
                ]
            )],
            sliders=[dict(
                active=0,
                x=0.5,
                xanchor="center",
                len=0.9,
                pad={"t": 50, "b": 20},  #
                steps=[dict(
                    label=str(year),
                    method="animate",
                    args=[[str(year)], {"frame": {"duration": 300, "redraw": True},
                                        "mode": "immediate",
                                        "transition": {"duration": 200}}]
                ) for year in years]
            )],
            legend=dict(
                title="Legend",
                orientation="v",
                yanchor="middle",
                y=0.92,
                xanchor="right",
                x=1.01,
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="black",
                borderwidth=0.5
            )
        )
    )

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
        dcc.Graph(id="world-map", figure=build_map(), style={"width": "100%", "height": "100%"}),
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
        dff = MergedIndex[MergedIndex["year"] == year]
        data = []

        # dynamic title text
        title_text = ''
        if len(selected_indices) > 0:
            title_text += chart_names[selected_indices[0]]
        if len(selected_indices) > 1:
            title_text += ' & ' + chart_names[selected_indices[1]]
        if selected_indices:
            title_text += f' in {year}'

        # first selected index on the map
        if len(selected_indices) > 0 and selected_indices[0] in dff.columns:
            choropleth = go.Choropleth(
                locations=dff["country"],
                z=dff[selected_indices[0]],
                locationmode="country names",
                zmin=dff[selected_indices[0]].min(),
                zmax=dff[selected_indices[0]].max(),
                colorscale=colours[selected_indices[0]] + "s",
                marker_line_color="white",
                marker_line_width=0.5,
                hoverinfo="skip",
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=1)),
                showlegend=True,
                showscale=False,
                name = legend_names[selected_indices[0]],
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
                        color=colours[selected_indices[i]],
                        opacity=0.5,
                        line=dict(width=0.7, color="white")
                    ),
                    hoverinfo="skip",
                    selected=dict(marker=dict(opacity=0.5)),
                    unselected=dict(marker=dict(opacity=0.5)),
                    name = legend_names[selected_indices[i]],
                    showlegend = True,
                )
                data.append(bubbles)

        #building custom data
        custom_data = ["country"]
        custom_data.extend(selected_indices)

        #building hover info
        hover_info = "Country: %{customdata[0]}<br>"
        for index in selected_indices:
            hover_info += chart_names[index] + " " + hover_data_1[index] + str(selected_indices.index(index) + 1) + hover_data_2[index] + "<br>"
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
    return build_map(frames)

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

    return build_line_chart(selected_countries), selected_countries, None

def build_line_chart(selected_countries):
    fig = go.Figure()
    color_map = px.colors.qualitative.Plotly
    country_colors = {country: color_map[i % len(color_map)] for i, country in enumerate(selected_countries)}
    for country in selected_countries:
        df_country = MergedIndex[MergedIndex["country"] == country].sort_values("year")
        color = country_colors[country]
        fig.add_trace(go.Scatter(
            x=df_country["year"],
            y=df_country["price_adjusted"],
            mode="lines+markers",
            name=f"{country} - Big Mac Price",
            yaxis="y1",
            line=dict(width=2, color=color)
        ))
        fig.add_trace(go.Scatter(
            x=df_country["year"],
            y=df_country["DIIndex"],
            mode="lines+markers",
            name=f"{country} - Diplomacy Index",
            yaxis="y2",
            line=dict(width=2, dash="dot", color=color)
        ))

    fig.update_layout(
        title="Big Mac Price vs Diplomacy Index Over Time",
        xaxis=dict(title="Year"),
        yaxis=dict(
            title="Big Mac Price (USD)",
            tickfont=dict(color="#E53935"),
            range=[0, 12],

        ),
        yaxis2=dict(
            title="Diplomacy Index",
            tickfont=dict(color="#1E88E5"),
            overlaying="y",
            side="right",
            range=[0, 12]

        ),
        legend=dict(
            x=1.05,  # push slightly outside the plotting area
            y=1,     # align to top
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        template="plotly_white",
        margin=dict(r=150))
    return fig

if __name__ == "__main__":
    app.run(debug=True)

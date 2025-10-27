import plotly.graph_objects as go
import DataHandling as dh
import plotly.express as px
from dash import Dash, dcc, html, Output, Input, State, ctx

# initial data load
DemocracyIndex = dh.LoadDemocracyIndex()
BigmacIndex = dh.LoadBigMacIndex()

# merging both datasets to have the same years and countries
MergedIndex = dh.MergeDataFrames(DemocracyIndex, BigmacIndex)

# set the scale
min_price = MergedIndex["price_adjusted"].min()
max_price = MergedIndex["price_adjusted"].max()


years = sorted(int(y) for y in MergedIndex["year"].unique())
frames = []
for year in years:
    dff = MergedIndex[MergedIndex["year"] == year]

    # the map with the big mac data
    choropleth = go.Choropleth(
        locations=dff["country"],
        z=dff["price_adjusted"],
        locationmode="country names",
        zmin=min_price,
        zmax=max_price,
        colorscale="Reds",
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(title="Price (USD)"),
        showscale=True,
        hoverinfo="skip",
        selected=dict(marker=dict(opacity=1)),
        unselected=dict(marker=dict(opacity=1))
    )

    # democracy index as bubis bublé
    democracy_bubbles = go.Scattergeo(
        locations=dff["country"],
        locationmode="country names",
        mode="markers",
        marker=dict(
            size=dff["DIIndex"] * 5,
            color="blue",
            opacity=0.5,
            line=dict(width=0.7, color="white")
        ),
        hoverinfo="skip",
        selected=dict(marker=dict(opacity=0.5)),
        unselected=dict(marker=dict(opacity=0.5))
    )

    # an invisible marker per country so selection events are triggered reliably.
    scatter_text = go.Scattergeo(
        locations=dff["country"],
        locationmode="country names",
        mode="markers+text",
        marker=dict(size=20, opacity=0),  # invisible but selectable
        customdata=dff[["country", "price_adjusted", "DIIndex"]].values,
        hovertemplate=(
            "Country: %{customdata[0]}<br>"
            "Big Mac Price: %{customdata[1]:.2f} USD<br>"
            "Democracy Index: %{customdata[2]:.2f}<extra></extra>"
        ),
        selected=dict(marker=dict(opacity=0)),
        unselected=dict(marker=dict(opacity=0)),
        showlegend=False,
    )

    frames.append(go.Frame(
        data=[choropleth, democracy_bubbles, scatter_text],
        name=str(year),
        layout=go.Layout(title_text=f"Big Mac Dollar Prices — {year}")
    ))

# initial map figure
map_fig = go.Figure(
    data=frames[0].data,
    frames=frames,
    layout=go.Layout(
        title=f"Big Mac Dollar Prices & Democracy Index in {years[0]}",
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
        )]
    )
)

initial_map_fig = map_fig

# dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Big Mac Index VS Democracy Ratings World Wide Comparison", style={"textAlign": "center"}),
    html.Div(
        dcc.Graph(id="world-map", figure=map_fig, style={"width": "100%", "height": "100%"}),
        style={
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "flexDirection": "column",
            "width": "100%",
            "height": "80vh"
        }
    ),
    dcc.Store(id="last-clicked", data=None),
    dcc.Store(id="selected_countries", data=["Denmark"]),
    html.Div([
        dcc.Graph(id="line-chart"),
        html.Button("Reset Line Chart", id="reset-btn", n_clicks=0, className="plotly-btn")
    ])
])

# line chart callback
@app.callback(
    Output("line-chart", "figure"),
    Output("last-clicked", "data"),
    Output("selected_countries", "data"),
    Input("world-map", "selectedData"),
    Input("reset-btn", "n_clicks"),
    State("last-clicked", "data"),
    State("selected_countries", "data"),
)

def update_line_chart(selectedData, _, last_clicked, selected_countries):
    # reset behavior
    if ctx.triggered_id == "reset-btn":
        selected_countries = ["Denmark"]
        last_clicked = None
        return build_line_chart(selected_countries), last_clicked, selected_countries

    # a country was selected -- selectedData present
    elif selectedData and "points" in selectedData and len(selectedData["points"]) > 0:
        raw = selectedData["points"][0].get("customdata") or selectedData["points"][0].get("location")

        if isinstance(raw, (list, tuple)):
            country_clicked = raw[0]
        else:
            country_clicked = raw

        if country_clicked:
            # if present remove, else add
            if country_clicked in selected_countries:
                selected_countries.remove(country_clicked)
            else:
                selected_countries.append(country_clicked)
            last_clicked = country_clicked

    # selectedData is none so a deselect happened -- use last_clicked to know which to remove
    else:
        if last_clicked:
            if last_clicked in selected_countries:
                selected_countries.remove(last_clicked)
            last_clicked = None

    return build_line_chart(selected_countries) ,last_clicked, selected_countries

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
            titlefont=dict(color="#E53935"),
            tickfont=dict(color="#E53935"),
            range=[0, 11],

        ),
        yaxis2=dict(
            title="Diplomacy Index",
            titlefont=dict(color="#1E88E5"),
            tickfont=dict(color="#1E88E5"),
            overlaying="y",
            side="right",
            range=[0, 11] 

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
    app.run(debug=False)

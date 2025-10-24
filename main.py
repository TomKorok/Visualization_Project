import pandas as pd
import plotly.graph_objects as go
import DataHandling as dh
from dash import Dash, dcc, html, Output, Input, State, ctx

DemocracyIndex = dh.LoadDemocracyIndex()
BigmacIndex = dh.LoadBigMacIndex()

MergedIndex = dh.MergeDataFrames(DemocracyIndex, BigmacIndex)

min_price = MergedIndex["price"].min()
max_price = MergedIndex["price"].max()

# --- Create frames --- (add customdata so we reliably know country in callbacks)
years = sorted(int(y) for y in MergedIndex["year"].unique())
frames = []
for year in years:
    dff = MergedIndex[MergedIndex["year"] == year]

    choropleth = go.Choropleth(
        locations=df_bm_cy["country"],
        z=df_bm_cy["price_adjusted"],
        locationmode="country names",
        zmin=min_price,
        zmax=max_price,
        colorscale="Reds",
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(title="Price (USD)"),
        showscale=True,
        customdata=df_bm_cy["country"].tolist(),  # <-- customdata with country names
        hovertemplate="%{customdata}<br>Price: %{z:.2f}$<extra></extra>",
        selected=dict(marker=dict(opacity=1)),
        unselected=dict(marker=dict(opacity=1))
    )

    # --- Democracy Index Bubis Bublé ---
    democracy_bubbles = go.Scattergeo(
        locations=df_di_cy["country"],
        locationmode="country names",
        text=df_di_cy["index"].astype(str),
        mode="markers",
        marker=dict(
            size=df_di_cy["index"] * 5,   # scale bubble size
            color="blue",
            opacity=0.5,
            line=dict(width=0.7, color="white")
        ),
        hoverinfo="text",
        name="Democracy Index"
    )

    # Make an invisible marker per country so selection events are triggered reliably.
    scatter_text = go.Scattergeo(
        locations=df_bm_cy["country"],
        locationmode="country names",
        text=df_bm_cy["price_adjusted"].round(2).astype(str),
        mode="markers+text",
        marker=dict(size=8, opacity=0),  # invisible but selectable
        textposition="top center",
        textfont=dict(size=11, color="black", family="Arial"),
        hoverinfo="skip",
        customdata=df_bm_cy["country"].tolist(),  # also attach customdata here
        selected=dict(marker=dict(opacity=0), textfont=dict(color="black")),
        unselected=dict(marker=dict(opacity=0), textfont=dict(color="black"))
    )

    frames.append(go.Frame(
        data=[choropleth, scatter_text, democracy_bubbles],
        name=str(year),
        layout=go.Layout(title_text=f"Big Mac Dollar Prices — {year}")
    ))

# --- Initial map figure --- (add clickmode to enable select events)
map_fig = go.Figure(
    data=frames[0].data,
    frames=frames,
    layout=go.Layout(
        title=f"Big Mac Dollar Prices — {years[0]}",
        clickmode="event+select",  # important: enable selection events
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
                    args=[[str(years[0])],   # reset to first year
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

# --- Dash app ---
app = Dash(__name__)

# store selected countries (server-side simple list) and a store to remember last-clicked country
selected_countries = ["Denmark"]

app.layout = html.Div([
    html.H3("Big Mac Index World Wide Comparison"),
    html.Div(
        dcc.Graph(id="world-map", figure=map_fig, style={"width": "100%", "height": "100%"}),
        style={
            "display": "flex",
            "justifyContent": "center",  # centers horizontally
            "alignItems": "center",  # centers vertically if container has height
            "flexDirection": "column",
            "width": "100%",
            "height": "80vh"
        }
    ),
    dcc.Store(id="last-clicked", data=None),  # stores last clicked country so we can handle deselects
    html.Div([
        dcc.Graph(id="line-chart"),
        html.Button("Reset Line Chart", id="reset-btn", n_clicks=0, className="plotly-btn")
    ])
])


# --- Line chart callback (multi-country + highlight current year) ---
@app.callback(
    Output("line-chart", "figure"),
    Output("last-clicked", "data"),
    Input("world-map", "selectedData"),
    Input("reset-btn", "n_clicks"),
    State("last-clicked", "data"),
    State("world-map", "figure")
)
def update_line_chart(selectedData, n_clicks, last_clicked, world_map_fig_state):
    triggered_input = ctx.triggered_id

    global selected_countries

    # reset behavior
    if triggered_input == "reset-btn":
        selected_countries = ["Denmark"]
        last_clicked = None

    # a country was selected (selectedData present)
    elif selectedData and "points" in selectedData and len(selectedData["points"]) > 0:
        raw = selectedData["points"][0].get("customdata") or selectedData["points"][0].get("location")
        # customdata might be a list or a single string
        if isinstance(raw, (list, tuple)):
            country_clicked = raw[0]
        else:
            country_clicked = raw

        if country_clicked:
            # toggle: if present remove, else add
            if country_clicked in selected_countries:
                selected_countries.remove(country_clicked)
            else:
                selected_countries.append(country_clicked)
            last_clicked = country_clicked

    # selectedData is None -> a deselect happened. Use last_clicked to know which to remove.
    else:
        if last_clicked:
            if last_clicked in selected_countries:
                selected_countries.remove(last_clicked)
            last_clicked = None

    # --- Build the line chart ---
    fig = go.Figure()
    for country in selected_countries:
        df_country = MergedIndex[MergedIndex["country"] == country].sort_values("year")
        fig.add_trace(go.Scatter(
            x=df_country["year"],
            y=df_country["price_adjusted"],
            mode="lines+markers",
            name=country
        ))

    fig.update_layout(
        title="Big Mac Prices Over Time -- Click a country to compare",
        xaxis_title="Year",
        yaxis_title="Price (USD)",
        showlegend=True
    )

    return fig, last_clicked

if __name__ == "__main__":
    app.run(debug=False)

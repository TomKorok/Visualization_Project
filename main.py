import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input, State, ctx
import plotly.express as px

# --- Load data ---
df = pd.read_csv("BigmacPrice.csv")
df = df.rename(columns={"name": "country", "dollar_price": "price"})
df["year"] = pd.to_datetime(df["date"]).dt.year
df = df.groupby(["country", "year"], as_index=False)["price"].mean()

years = sorted(int(y) for y in df["year"].unique())
min_price = df["price"].min()
max_price = df["price"].max()

# --- Create frames ---
frames = []
for year in years:
    dff = df[df["year"] == year]

    choropleth = go.Choropleth(
        locations=dff["country"],
        z=dff["price"],
        locationmode="country names",
        zmin=min_price,
        zmax=max_price,
        colorscale="Reds",
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(title="Price (USD)"),
        showscale=True
    )

    scatter_text = go.Scattergeo(
        locations=dff["country"],
        locationmode="country names",
        text=dff["price"].round(2).astype(str),
        mode="text",
        textfont=dict(size=12, color="black", family="Arial Bold"),
        hoverinfo="text"
    )

    frames.append(go.Frame(
        data=[choropleth, scatter_text],
        name=str(year),
        layout=go.Layout(title_text=f"Big Mac Dollar Prices — {year}")
    ))

# --- Initial map figure ---
map_fig = go.Figure(
    data=frames[0].data,
    frames=frames,
    layout=go.Layout(
        title=f"Big Mac Dollar Prices — {years[0]}",
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        width=1400,
        height=800,
        margin=dict(l=0, r=0, t=50, b=0),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.05, y=0.05,
            xanchor="left", yanchor="bottom",
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
                )
            ]
        )],
        sliders=[dict(
            active=0,
            pad={"t": 50},
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

# store selected countries
selected_countries = ["Denmark"]

app.layout = html.Div([
    html.H3("Big Mac Index — Click a Country to Compare"),
    html.Button("Reset", id="reset-btn", n_clicks=0),
    dcc.Graph(id="world-map", figure=map_fig),
    dcc.Graph(id="line-chart")
])

# --- Line chart callback (multi-country + highlight current year) ---
@app.callback(
    Output("line-chart", "figure"),
    Input("world-map", "clickData"),
    Input("reset-btn", "n_clicks"),
    State("line-chart", "figure")
)
def update_line_chart(clickData, n_clicks, current_fig):
    triggered_input = ctx.triggered_id

    global selected_countries
    if triggered_input == "reset-btn":
        selected_countries = ["Denmark"]
    elif clickData:
        country_clicked = clickData["points"][0]["location"]
        if country_clicked in selected_countries:
            selected_countries.remove(country_clicked)
        else:
            selected_countries.append(country_clicked)

    fig = go.Figure()
    for country in selected_countries:
        df_country = df[df["country"] == country].sort_values("year")
        fig.add_trace(go.Scatter(
            x=df_country["year"],
            y=df_country["price"],
            mode="lines+markers",
            name=country
        ))

    fig.update_layout(
        title="Big Mac Prices Over Time",
        xaxis_title="Year",
        yaxis_title="Price (USD)",
        showlegend=True  # make sure legend is visible
    )

    # Highlight current year from map (if figure has a title like "… — YEAR")
    if current_fig and "layout" in current_fig and "title" in current_fig["layout"]:
        title_text = current_fig["layout"]["title"]["text"]
        try:
            current_year = int(title_text.split("—")[-1].strip())
            fig.add_vline(x=current_year, line_width=2, line_dash="dash", line_color="gray")
        except:
            pass

    fig.update_layout(
        title="Big Mac Prices Over Time",
        xaxis_title="Year",
        yaxis_title="Price (USD)"
    )
    return fig

# --- Reset map callback ---
@app.callback(
    Output("world-map", "figure"),
    Input("reset-btn", "n_clicks")
)
def reset_map(n_clicks):
    if n_clicks == 0:
        return initial_map_fig
    return initial_map_fig

if __name__ == "__main__":
    app.run(debug=False)

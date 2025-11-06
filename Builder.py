import plotly.graph_objects as go
import plotly.express as px

import MetaData as md
import DataHandling as dh


def build_line_chart(selected_countries, selected_indices):
    fig = go.Figure()
    color_map = px.colors.qualitative.Plotly
    country_colors = {country: color_map[i % len(color_map)] for i, country in enumerate(selected_countries)}
    for country in selected_countries:
        merged_df = dh.get_merged_df()
        df_country = merged_df[merged_df["country"] == country].sort_values("year")
        color = country_colors[country]
        if len(selected_indices) > 0:
            fig.add_trace(go.Scatter(
                x=df_country["year"],
                y=df_country[selected_indices[0]],
                mode="lines+markers",
                name=f"{country} - {md.chart_names[selected_indices[0]]}",
                yaxis="y1",
                line=dict(width=2, color=color),
                showlegend=True
            ))
        if len(selected_indices) > 1:
            fig.add_trace(go.Scatter(
                x=df_country["year"],
                y=df_country[selected_indices[1]],
                mode="lines+markers",
                name=f"{country} - {md.chart_names[selected_indices[1]]}",
                yaxis="y2",
                line=dict(width=2, dash="dot", color=color),
                showlegend=True
            ))

    # dynamic title text
    title_text = ''
    if len(selected_indices) > 0:
        title_text += md.chart_names[selected_indices[0]]
    if len(selected_indices) > 1:
        title_text += " & " + md.chart_names[selected_indices[1]]
    if len(selected_indices) > 0:
        title_text += " Over Time"

    if len(selected_indices) > 0:
        layout_kwargs = dict(
            title=title_text,
            xaxis=dict(title="Year"),
            yaxis=dict(
                title=md.chart_names[selected_indices[0]],
                tickfont=dict(color="black"),
                range=[0, 12],
            ),
            legend=dict(
                x=1.05,
                y=1,
                xanchor="left",
                yanchor="top",
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1
            ),
            template="plotly_white",
            margin=dict(r=150)
        )

        # Only add yaxis2 if there's a second selected index
        if len(selected_indices) > 1:
            layout_kwargs['yaxis2'] = dict(
                title=md.chart_names[selected_indices[1]],
                tickfont=dict(color="black"),
                overlaying="y",
                side="right",
                range=[0, 12]
            )

        # Apply layout
        fig.update_layout(**layout_kwargs)
    else:
        # Fallback if no selected indices
        fig.update_layout(
            title=title_text,
            xaxis=dict(title="Year"),
            template="plotly_white",
            margin=dict(r=150)
        )
    return fig

# initial map figure
def build_map(frames=None, years=[]):
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
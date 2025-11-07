import plotly.graph_objects as go
import plotly.express as px

import chart_config as cc
import DataHandling as dh


def build_line_chart(selected_countries, selected_indexes, merged_df):
    fig = go.Figure()
    color_map = px.colors.qualitative.Plotly
    country_colors = {country: color_map[i % len(color_map)] for i, country in enumerate(selected_countries)}
    for country in selected_countries:
        df_country = merged_df[merged_df["country"] == country].sort_values("year")
        color = country_colors[country]
        if len(selected_indexes) > 0:
            fig.add_trace(go.Scatter(
                x=df_country["year"],
                y=df_country[selected_indexes[0]],
                mode="lines+markers",
                name=f"{country} - {cc.chart_config[selected_indexes[0]]["chart_name"]}",
                yaxis="y1",
                line=dict(width=2, color=color),
                showlegend=True
            ))
        if len(selected_indexes) > 1:
            fig.add_trace(go.Scatter(
                x=df_country["year"],
                y=df_country[selected_indexes[1]],
                mode="lines+markers",
                name=f"{country} - {cc.chart_config[selected_indexes[1]]["chart_name"]}",
                yaxis="y2",
                line=dict(width=2, dash="dot", color=color),
                showlegend=True
            ))

    # dynamic title text
    title_text = ''
    if len(selected_indexes) > 0:
        title_text += cc.chart_config[selected_indexes[0]]["chart_name"]
    if len(selected_indexes) > 1:
        title_text += " & " + cc.chart_config[selected_indexes[1]]["chart_name"]
    if len(selected_indexes) > 0:
        title_text += " Over Time"

    if len(selected_indexes) > 0:
        layout_kwargs = dict(
            title=title_text,
            xaxis=dict(title="Year"),
            yaxis=dict(
                title=cc.chart_config[selected_indexes[0]]["chart_name"],
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
        if len(selected_indexes) > 1:
            layout_kwargs['yaxis2'] = dict(
                title=cc.chart_config[selected_indexes[1]]["chart_name"],
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

def build_map_info(years, merged_df, selected_indexes):
    frames = []
    for year in years:
        dff = merged_df[merged_df["year"] == year]
        data = []

        # dynamic title text
        title_text = ''
        for i in range(len(selected_indexes)):
            title_text += cc.chart_config[selected_indexes[i]]["chart_name"]
            if i != len(selected_indexes) - 1:
                title_text += " & "
            else:
                title_text += f' in {year}'

        # first selected index on the map
        if len(selected_indexes) > 0 and selected_indexes[0] in dff.columns:
            choropleth = go.Choropleth(
                locations=dff["country"],
                z=dff[selected_indexes[0]],
                locationmode="country names",
                zmin=dff[selected_indexes[0]].min(),
                zmax=dff[selected_indexes[0]].max(),
                colorscale=cc.chart_config[selected_indexes[0]]["color"] + "s",
                marker_line_color="white",
                marker_line_width=0.5,
                hoverinfo="skip",
                selected=dict(marker=dict(opacity=1)),
                unselected=dict(marker=dict(opacity=1)),
                showlegend=True,
                showscale=False,
                name = cc.chart_config[selected_indexes[0]]["legend_name"],
            )
            data.append(choropleth)

        # every other index as bubis bublé
        for i in range(1, len(selected_indexes)):
            if selected_indexes[i] in dff.columns:
                bubbles = go.Scattergeo(
                    locations=dff["country"],
                    locationmode="country names",
                    mode="markers",
                    marker=dict(
                        size=dff[selected_indexes[i]] * 5,
                        color=cc.chart_config[selected_indexes[i]]["color"],
                        opacity=0.5,
                        line=dict(width=0.7, color="white")
                    ),
                    hoverinfo="skip",
                    selected=dict(marker=dict(opacity=0.5)),
                    unselected=dict(marker=dict(opacity=0.5)),
                    name = cc.chart_config[selected_indexes[i]]["legend_name"],
                    showlegend = True,
                )
                data.append(bubbles)

        #building custom data
        custom_data = ["country"]
        custom_data.extend(selected_indexes)

        #building hover info
        hover_info = "Country: %{customdata[0]}<br>"
        for index in selected_indexes:
            hover_info += cc.chart_config[index]["chart_name"] + " " + cc.chart_config[index]["hover_prefix"] + str(selected_indexes.index(index) + 1) + cc.chart_config[index]["hover_suffix"] + "<br>"
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
    return frames

# initial map figure
def build_map(frames=None, years=[]):
    return go.Figure(
        data= frames[0].data if frames is not None else None,
        frames=frames,
        layout=go.Layout(
            title=frames[0].layout.title.text if frames else "",
            clickmode="event+select",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type="natural earth",
                bgcolor = 'rgba(0,0,0,0)' #transparent
            ),
            margin=dict(l=0, r=0, t=50, b=0),
            paper_bgcolor='rgba(0,0,0,0)',  # transparent
            plot_bgcolor='rgba(0,0,0,0)',  # transparent
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

def build_bar_chart(selected_countries, year, all_indexes, merged_df):
    fig = go.Figure()

    #selected_countries here is always 1 long
    data = merged_df[
        (merged_df["country"] == selected_countries[0]) &
        (merged_df["year"] == year) ]

    # Build bars for all indexes
    y_values = [data[idx].values[0] if idx in data else None for idx in all_indexes]
    x_labels = [cc.chart_config[idx]["chart_name"] for idx in all_indexes]

    fig.add_trace(go.Bar(
        x=x_labels,
        y=y_values,
        marker_color="Darkorange",
        text=[f"{y:.2f}" if y is not None else "" for y in y_values],
        textposition="auto"
    ))

    # Build dynamic title
    title_text = "Comparison for " + selected_countries[0] + " Across All Available Indexes"

    # Transparent, clean layout
    fig.update_layout(
        title=title_text,
        xaxis=dict(title="Indexes"),
        yaxis=dict(title="Value", range=[0, 12]),
        barmode="group",
        legend=dict(
            x=1.02,
            y=1,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        margin=dict(r=150, t=50, b=80),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    return fig
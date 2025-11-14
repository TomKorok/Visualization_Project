# metadata for displaying the correct text everywhere

chart_config = {
    "BMI": {
        "color": "Red",
        "legend_name": "Big Mac Price [0 - 10] Log Scaled",
        "chart_name": "Big Mac Price",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]:.2f} US$"
    },
    "DIIndex": {
        "color": "Blue",
        "legend_name": "Democracy Index [0 - 10]",
        "chart_name": "Democracy Index",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]:.2f}"
    },
    "GDPValue": {
        "color": "Green",
        "legend_name": "GDP [0 - 10] Log Scaled",
        "chart_name": "GDP",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]} US$B"
    },
    "GDPCapitaValue": {
        "color": "Orange",
        "legend_name": "GDP Per Capita [0 - 10] Log Scaled",
        "chart_name": "GDP Per Capita",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]:.2f} US$"
    }
}
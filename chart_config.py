# metadata for displaying the correct text everywhere

chart_config = {
    "price_adjusted": {
        "color": "Red",
        "legend_name": "Big Mac Price [0 - 12.16] US$",
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
        "legend_name": "GDP [0 - 30507217] US$B",
        "chart_name": "GDP",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]} US$B"
    },
    "GDPCapitaValue": {
        "color": "Orange",
        "legend_name": "GDP Per Capita [0 - 138934.96] US$",
        "chart_name": "GDP Per Capita",
        "hover_prefix": "%{customdata[",
        "hover_suffix": "]:.2f} US$"
    }
}
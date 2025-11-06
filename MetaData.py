# prefixed colour based on the column name in the MergedIndex
colours = {
    "price_adjusted": 'Red',
    "DIIndex" : 'Blue'
}
# prefixed legend names based on the column name in the MergedIndex
legend_names = {
    "price_adjusted": f"Big Mac Price [0 - 12.16]",
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
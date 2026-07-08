# 2.1 Install necessary Python libraries: Plotly, Dash, Streamlit, Pandas, GeoPandas, etc.
# (Installation happens outside this script; this section is informational.)

from dash import Dash, dcc, html, dash_table
import plotly.express as px
import pandas as pd

# Initializing the Dash app
app = Dash(__name__)

# Using a built-in dataset so the map displays real points (no placeholder square)
carshare = px.data.carshare()

# Creating placeholder data for charts and table
data_table = pd.DataFrame({
    "Region": ["Region A", "Region B", "Region C"],
    "Unemployment Rate": [7.5, 6.2, 8.1],
    "Population": [50000, 42000, 61000],
    "Median Income": [65000, 58000, 72000]
})

# 2.2 Plan the user interface and user experience. Decide on the placement of maps, charts, filters, and other interactive elements.
# (Implemented through the layout structure below.)

# 2.3 Allow users to select specific data layers, time periods, or demographic groups.
# (Filters added in the layout.)

# 2.4 Incorporate geospatial visualizations with panning and zooming capabilities.
# 2.5 Provide detailed information when users hover over data points or map regions.

# Building a geospatial map with panning, zooming, and hover information
fig = px.scatter_mapbox(
    carshare,
    lat="centroid_lat",
    lon="centroid_lon",
    size="car_hours",
    color="peak_hour",
    hover_name="peak_hour",
    hover_data={
        "Car Hours": carshare["car_hours"],
        "Peak Hour": carshare["peak_hour"]
    },
    zoom=10,
    height=500
)

fig.update_layout(mapbox_style="carto-positron")

# 2.7 Use Plotly or Folium to create interactive maps. Make sure to include bar charts, line graphs, or other relevant visualizations.

# Placeholder bar chart
bar_chart = px.bar(
    data_table,
    x="Region",
    y="Unemployment Rate",
    title="Unemployment Rate by Region"
)

# Placeholder line chart
line_chart = px.line(
    data_table,
    x="Region",
    y="Median Income",
    title="Median Income Trend"
)

# 2.8 Provide options for users to view the underlying data.
# 2.9 Add annotations and guidance tools.

# Building the full dashboard layout
app.layout = html.Div([

    # Dashboard Title
    html.H2("Honolulu County Dashboard"),

    # Filters section
    html.Div([
        html.H4("Filters"),

        # Data layer selection
        dcc.Checklist(
            id='layer-select',
            options=[
                {'label': 'Unemployment Rates', 'value': 'unemp'},
                {'label': 'Community Resources', 'value': 'resources'},
                {'label': 'Transit Access', 'value': 'transit'},
                {'label': 'Income Levels', 'value': 'income'},
                {'label': 'Population Density', 'value': 'popdensity'}
            ],
            value=['unemp']
        ),

        # Time period selection
        dcc.Dropdown(
            id='time-period',
            options=[
                {'label': '2020', 'value': '2020'},
                {'label': '2021', 'value': '2021'},
                {'label': '2022', 'value': '2022'},
                {'label': '2023', 'value': '2023'}
            ],
            placeholder="Select time period"
        ),

        # Demographic group selection
        dcc.Dropdown(
            id='demographic-group',
            options=[
                {'label': 'All Residents', 'value': 'all'},
                {'label': 'Youth (18–24)', 'value': 'youth'},
                {'label': 'Adults (25–64)', 'value': 'adults'},
                {'label': 'Seniors (65+)', 'value': 'seniors'},
                {'label': 'Native Hawaiian / Pacific Islander', 'value': 'nhpi'},
                {'label': 'Asian', 'value': 'asian'},
                {'label': 'White', 'value': 'white'},
                {'label': 'Hispanic / Latino', 'value': 'latino'}
            ],
            placeholder="Select demographic group"
        ),

        # Unemployment range filter
        dcc.Dropdown(
            id='unemp-range',
            options=[
                {'label': 'Low Unemployment', 'value': 'low'},
                {'label': 'Medium Unemployment', 'value': 'medium'},
                {'label': 'High Unemployment', 'value': 'high'}
            ],
            placeholder="Select unemployment range"
        ),

        # Guidance annotation
        html.Div("Use the filters above to explore different layers and demographic groups.",
                 style={'marginTop': '20px', 'fontStyle': 'italic'})

    ], style={'width': '25%', 'float': 'left', 'padding': '10px'}),

    # Map + charts section
    html.Div([
        html.H4("Interactive Map (Panning, Zooming, Hover Enabled)"),
        dcc.Graph(id='main-map', figure=fig),

        html.H4("Bar Chart"),
        dcc.Graph(id='bar-chart', figure=bar_chart),

        html.H4("Line Chart"),
        dcc.Graph(id='line-chart', figure=line_chart),

        html.H4("View Underlying Data"),
        dash_table.DataTable(
            id='data-table',
            data=data_table.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_table.columns],
            page_size=10
        )

    ], style={'width': '70%', 'float': 'right', 'padding': '10px'})
])

# Running the app
if __name__ == '__main__':
    app.run(debug=True)


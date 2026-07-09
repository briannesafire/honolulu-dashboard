import streamlit as st
import pandas as pd
import plotly.express as px
from shapely.geometry import mapping

# Load data
merged = pd.read_pickle("merged.pkl")
osm_points = pd.read_pickle("osm_points.pkl")

# Convert Shapely geometry to JSON-safe dicts
merged["geometry"] = merged["geometry"].apply(lambda g: mapping(g))

st.set_page_config(
    layout="wide",
    page_title="Honolulu Community Development Dashboard"
)

st.title("Honolulu Community Development Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

demo = st.sidebar.selectbox(
    "Demographic Group",
    ["population", "nhpi", "asian", "white"]
)

indicator = st.sidebar.selectbox(
    "Indicator",
    ["unemployment_rate", "need_score"]
)

layers = st.sidebar.multiselect(
    "OSM Layers",
    ["School", "Health", "Church", "Community", "Bus Stop", "Rail Station"]
)

# Map
fig_map = px.choropleth_mapbox(
    merged,
    geojson=merged.set_index("tract_id")["geometry"].__geo_interface__,
    locations="tract_id",
    color=indicator,
    mapbox_style="carto-positron",
    center={"lat": 21.4389, "lon": -157.9993},
    zoom=10,
    opacity=0.9,
    hover_name="tract_id",
    hover_data={
        "population": True,
        "nhpi": True,
        "asian": True,
        "white": True,
        "resource_count": True,
        "transit_count": True,
        "unemployment_rate": True,
        "need_score": True
    }
)

fig_map.update_traces(marker_line_width=0.5, marker_line_color="black")

# Add OSM layers (multiple layers with different colors)
if layers:
    layer_colors = {
        "School": "red",
        "Health": "blue",
        "Church": "purple",
        "Community": "green",
        "Bus Stop": "orange",
        "Rail Station": "yellow"
    }

    for layer in layers:
        subset = osm_points[osm_points["type"] == layer]
        fig_map.add_scattermapbox(
            lat=subset.geometry.y,
            lon=subset.geometry.x,
            mode="markers",
            marker=dict(size=6, color=layer_colors.get(layer, "black")),
            text=subset["type"],
            name=layer
        )


st.plotly_chart(fig_map, width="stretch")

# Bar chart
fig_bar = px.bar(
    merged.sort_values(indicator, ascending=False).head(10),
    x="tract_id",
    y=indicator,
    title=f"Top 10 Tracts by {indicator.replace('_', ' ').title()}"
)

st.plotly_chart(fig_bar, width="stretch")

# Underlying data viewer
st.subheader("Underlying Data")
st.dataframe(merged.drop(columns=["geometry"]))


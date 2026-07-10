import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
merged = pd.read_pickle("merged.pkl")
osm_points = pd.read_pickle("osm_points.pkl")

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

# Compute centroids for dot placement
merged["centroid_x"] = merged["geometry"].centroid.x
merged["centroid_y"] = merged["geometry"].centroid.y

# Base map with unemployment dots
fig_map = px.scatter_mapbox(
    merged,
    lat="centroid_y",
    lon="centroid_x",
    color=indicator,
    color_continuous_scale="YlOrRd",
    size=[12] * len(merged),
    opacity=0.85,
    zoom=10,
    center={"lat": 21.4389, "lon": -157.9993},
    mapbox_style="carto-positron",
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

# Push unemployment dots BELOW all other layers
fig_map.update_traces(below="")

# Add OSM layers (these will naturally sit on top)
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

st.plotly_chart(fig_map, use_container_width=True)

# Bar chart
fig_bar = px.bar(
    merged.sort_values(indicator, ascending=False).head(10),
    x="tract_id",
    y=indicator,
    title=f"Top 10 Tracts by {indicator.replace('_', ' ').title()}"
)

st.plotly_chart(fig_bar, use_container_width=True)

# Underlying data viewer
st.subheader("Underlying Data")
st.dataframe(merged.drop(columns=["geometry"]))

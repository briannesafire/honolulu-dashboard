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

# Build GeoJSON
geojson = {
    "type": "FeatureCollection",
    "features": []
}

for _, row in merged.iterrows():
    geojson["features"].append({
        "type": "Feature",
        "geometry": row["geometry"],
        "properties": {
            "tract_id": row["tract_id"],
            "population": row["population"],
            "nhpi": row["nhpi"],
            "asian": row["asian"],
            "white": row["white"],
            "resource_count": row["resource_count"],
            "transit_count": row["transit_count"],
            "unemployment_rate": row["unemployment_rate"],
            "need_score": row["need_score"]
        }
    })

# Map
fig_map = px.choropleth_map(
    merged,
    geojson=geojson,
    locations="tract_id",
    featureidkey="properties.tract_id",
    color=indicator,
    center={"lat": 21.4389, "lon": -157.9993},
    zoom=10,
    opacity=0.7,
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

# REQUIRED for scattermapbox layers to appear
fig_map.update_layout(mapbox_style="carto-positron")

# Add OSM layers
if layers:
    filtered_osm = osm_points[osm_points["type"].isin(layers)]
    fig_map.add_scattermapbox(
        lat=filtered_osm.geometry.y,
        lon=filtered_osm.geometry.x,
        mode="markers",
        marker=dict(size=6, color="red"),
        text=filtered_osm["type"],
        name="OSM Layers"
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


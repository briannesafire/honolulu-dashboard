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

# Add readable neighborhood names
merged["neighborhood"] = merged["NAMELSAD"]

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

# Push unemployment dots below OSM layers
fig_map.update_traces(below="")

# Legend fix so it doesn't overlap
fig_map.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=0.01,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255,255,255,0.7)"
    )
)

# OSM layers (these stay on top)
if layers:
    layer_colors = {
        "School": "red",
        "Health": "blue",
        "Church": "purple",
        "Community": "green",
        "Bus Stop": "cyan",        # changed to avoid clashing with unemployment orange
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

# Better bar chart (neighborhood names instead of tract IDs)
fig_bar = px.bar(
    merged.sort_values(indicator, ascending=False).head(10),
    x="neighborhood",
    y=indicator,
    title=f"Top 10 Neighborhoods by {indicator.replace('_', ' ').title()}",
    text=indicator
)

fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig_bar.update_layout(yaxis_title=indicator.replace('_', ' ').title())

st.plotly_chart(fig_bar, use_container_width=True)

# Chart 1: Unemployment vs resource access
fig_scatter_resources = px.scatter(
    merged,
    x="resource_count",
    y="unemployment_rate",
    trendline="ols",
    title="Unemployment vs Community Resource Access",
    labels={"resource_count": "Nearby Services"}
)
st.plotly_chart(fig_scatter_resources, use_container_width=True)

# Chart 2: Unemployment vs transit access
fig_scatter_transit = px.scatter(
    merged,
    x="transit_count",
    y="unemployment_rate",
    trendline="ols",
    title="Unemployment vs Transit Access",
    labels={"transit_count": "Transit Stops (Bus + Rail)"}
)
st.plotly_chart(fig_scatter_transit, use_container_width=True)

# Chart 3: Line graph of unemployment by neighborhood
fig_line = px.line(
    merged.sort_values("unemployment_rate"),
    x="neighborhood",
    y="unemployment_rate",
    title="Unemployment Rate by Neighborhood"
)
fig_line.update_layout(xaxis_tickangle=45)
st.plotly_chart(fig_line, use_container_width=True)

# Underlying data (cleaned to only show relevant fields)
st.subheader("Underlying Data")
st.dataframe(
    merged[[
        "neighborhood",
        "population",
        "unemployment_rate",
        "median_income",
        "resource_count",
        "transit_count",
        "need_score"
    ]]
)

# -*- coding: utf-8 -*-
"""REgional data tab."""

from datetime import datetime
from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from src.get_industry_data import transform_data_to_industry_types

DATA_DIR = Path(__file__).parent.parent.resolve() / "data"


@st.cache_data
def get_region_geometry_from_csv():
    # Path to the CSV file containing the geometry data
    file_path = DATA_DIR / "data_regions_KRS_2022-01-01.csv"

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, dtype={"id": str})

    # Convert the 'geometry_epsg3035_500m' column to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.GeoSeries.from_wkt(df["geometry_epsg3035_500m"])
    )

    # Set the CRS for the GeoDataFrame
    gdf.crs = "EPSG:3035"
    return gdf


@st.cache_data
def get_synthetic_load_profiles(list_ind):
    list_df = []
    for ind in list_ind:
        filename = f"data/profiles/load_profiles_2019_{ind}.csv"
        tmp = pd.read_csv(filename, usecols=[1, 2, 3, 4])
        list_df.append(tmp)
    df_all = pd.concat(list_df)
    # Convert the timestamp column to datetime objects
    df_all["time"] = pd.to_datetime(df_all["time"])
    # aggregate:
    df_all = df_all.groupby(["time", "industry_id"])["value"].sum().reset_index()

    # Filter rows for a specific date
    target_date = datetime(2019, 1, 4).date()
    df_all = df_all[df_all["time"].dt.date == target_date]
    return df_all


def create_map(gdf, df_select, par_select):
    # Create a blank folium map centered at Germany
    # remove the tiles=None parameter to show  OSM street map
    m = folium.Map(
        location=[51.1657, 10.4515],
        zoom_start=6,
        control_scale=True,
        background_color="white",
    )

    # Create a choropleth layer to fill areas with colors based on 'area_m2'
    folium.Choropleth(
        geo_data=gdf,
        data=df_select,
        columns=["id", par_select],
        key_on="feature.properties.id",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=par_select,
        nan_fill_color="white",
    ).add_to(m)
    # Display the choropleth map using folium_static
    clickdata = st_folium(m, width=600, height=800)
    return clickdata


tab1, tab2, tab3 = st.tabs(["Map", "Data", "Regional profiles"])

if "cat_select" not in st.session_state.keys():
    st.session_state["cat_select"] = "WZ2008"

if "par_select" not in st.session_state.keys():
    st.session_state["par_select"] = "n_cap"

if "id_clicked" not in st.session_state.keys():
    st.session_state["id_clicked"] = None

if "name_clicked" not in st.session_state.keys():
    st.session_state["name_clicked"] = None

if "clickdata" not in st.session_state.keys():
    st.session_state["clickdata"] = None

# load cap and site data from database:
cap_and_site_data = pd.read_csv(DATA_DIR / "cap_and_site_data.csv", dtype={"id": str})

# load weights for transforming to industry types:
shares = pd.read_csv(DATA_DIR / "industry_type_2_wz2008_shares.csv")

# transform data from wz2008 categories to industry types:
industry_types = transform_data_to_industry_types(cap_and_site_data, shares)

# load geometry:
gdf = get_region_geometry_from_csv()

# wz or industry types?
st.session_state["cat_select"] = st.sidebar.radio(
    "Which categories to display on map?", ["WZ2008", "Industry types"]
)

# select wz category:
if st.session_state["cat_select"] == "WZ2008":
    list_wz = cap_and_site_data.wz2008_abteilung_name.unique().tolist()
if st.session_state["cat_select"] == "Industry types":
    list_wz = industry_types.sector_agg.unique().tolist()

list_wz.sort()
wz_select = st.sidebar.selectbox("Select category:", list_wz)
# which parameter to display?
st.session_state["par_select"] = st.sidebar.radio(
    "Select parameter:", ["n_sites", "n_cap"]
)

with tab1:
    if st.session_state["cat_select"] == "WZ2008":
        df_select = cap_and_site_data.loc[
            cap_and_site_data.wz2008_abteilung == int(wz_select[0:2])
        ].drop(["wz2008_abteilung", "wz2008_abteilung_name"], axis=1)
    if st.session_state["cat_select"] == "Industry types":
        df_select = industry_types.loc[industry_types.sector_agg == wz_select]
    c1, c2 = st.columns(2)
    with c2:
        # create map:
        st.session_state["clickdata"] = create_map(
            gdf, df_select, st.session_state["par_select"]
        )
        if st.session_state["clickdata"]["last_clicked"] is not None:
            st.session_state["id_clicked"] = st.session_state["clickdata"][
                "last_active_drawing"
            ]["properties"]["id"]
            st.session_state["name_clicked"] = st.session_state["clickdata"][
                "last_active_drawing"
            ]["properties"]["name"]

    with c1:
        if st.session_state["name_clicked"] is None:
            st.write("Click on an area for more details.")
        else:
            st.write(f"Data for {st.session_state['name_clicked']}:")
            if st.session_state["cat_select"] == "WZ2008":
                df_show = cap_and_site_data.loc[
                    cap_and_site_data.id == st.session_state["id_clicked"]
                ].sort_values(by="wz2008_abteilung_name", ascending=False)

                fig = px.bar(
                    df_show,
                    y="wz2008_abteilung_name",
                    x=st.session_state["par_select"],
                    orientation="h",
                    height=800,
                )
            if st.session_state["cat_select"] == "Industry types":
                df_show = industry_types.loc[
                    industry_types.id == st.session_state["id_clicked"]
                ].sort_values(by="sector_agg", ascending=False)

                fig = px.bar(
                    df_show,
                    y="sector_agg",
                    x=st.session_state["par_select"],
                    orientation="h",
                    height=800,
                )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.write("Data for all areas:")
    st.dataframe(df_select.set_index("name").sort_index(), use_container_width=True)

with tab3:
    st.write("Regional profiles")

    # Import regional synthetic profiles from csv:
    list_ind = shares.sector_agg_id.unique().tolist()
    df_profiles = get_synthetic_load_profiles(list_ind)
    st.dataframe(df_profiles)
    fig = px.area(
        df_profiles,
        x="time",
        y="value",
        facet_col="industry_id",
        facet_col_wrap=5,
    )
    st.plotly_chart(fig, use_container_width=True)

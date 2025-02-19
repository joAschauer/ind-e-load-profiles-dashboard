# -*- coding: utf-8 -*-
"""REgional data tab."""

from datetime import datetime
from pathlib import Path
from typing import Literal

import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from page_contents.components import download_excel_file
from src.get_industry_data import get_industry_type_regional_distribution

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
def get_synthetic_load_profiles():
    list_df = []
    for ind in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
        filename = f"data/profiles/load_profiles_2019_{ind}.csv"
        tmp = pd.read_csv(filename, usecols=[1, 2, 3, 4])
        list_df.append(tmp)
    df_all = pd.concat(list_df)
    # Convert the timestamp column to datetime objects
    df_all["time"] = pd.to_datetime(df_all["time"])
    # aggregate end use types:
    df_all = df_all.groupby(["time", "industry_id"])["value"].sum().reset_index()

    return df_all


@st.cache_data()
def get_regional_synthetic_load_profiles(
    region_id,
    split_by: Literal["n_cap", "n_sites"],
    dates: tuple[str, str] | None = None,
):
    load_profiles = get_synthetic_load_profiles().set_index("time")
    if dates is not None:
        load_profiles = load_profiles.loc[dates[0] : dates[1], :]

    industry_data = get_industry_type_regional_distribution()

    industry_type_id_mapping = (
        industry_data[["sector_agg_id", "sector_agg"]]
        .drop_duplicates()
        .set_index("sector_agg_id")
        .squeeze()
        .to_dict()
    )

    scaled_load_profiles = []
    for industry_number in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
        sector_data = industry_data.loc[
            industry_data["sector_agg_id"] == industry_number
        ]
        if (sector_data["id"] == region_id).any():
            quantity_in_region = sector_data.loc[
                (sector_data["id"] == region_id),
                split_by,
            ].iloc[0]
            quantity_over_all_regions = sector_data[split_by].sum()
            scaling_factor = quantity_in_region / quantity_over_all_regions
            scaled_profile = load_profiles.loc[
                (load_profiles["industry_id"] == industry_number), :
            ].assign(value=lambda x: x["value"] * scaling_factor)

            scaled_load_profiles.append(scaled_profile)

    out = pd.concat(scaled_load_profiles).reset_index()
    out["industry_id"] = out["industry_id"].map(industry_type_id_mapping)
    return out


def create_map(gdf, df_select, split_by):
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
        columns=["id", split_by],
        key_on="feature.properties.id",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=split_by,
        nan_fill_color="white",
        highlight=True,
    ).add_to(m)
    # Display the choropleth map using folium_static
    clickdata = st_folium(m, width=600, height=800)
    return clickdata


@st.fragment()
def map_and_widget(gdf, industry_data):
    list_wz = industry_data.sector_agg.unique().tolist()
    list_wz.sort()
    wz_select = st.selectbox("Select industry type for map", list_wz)
    df_select = industry_data.loc[industry_data.sector_agg == wz_select]
    # create map:
    create_map(gdf, df_select, st.session_state["split_by"])
    with st.expander("Data"):
        st.dataframe(
            df_select.set_index("name")
            .sort_index()[[st.session_state["split_by"]]]
            .rename(
                columns={
                    "n_cap": "Number of employees",
                    "n_sites": "Number of production sites",
                }
            ),
            use_container_width=True,
        )


@st.fragment()
def regional_profile_with_date_range_widget():
    date_range = st.slider(
        "select time range for data",
        value=(datetime(2019, 1, 1, 0, 0), datetime(2019, 1, 14, 0, 0)),
        min_value=datetime(2019, 1, 1, 0, 0),
        max_value=datetime(2019, 12, 31, 23, 45),
        format="YYYY/MM/DD - HH:mm",
        label_visibility="hidden",
        key="slider-regional-data",
    )

    regional_profiles = get_regional_synthetic_load_profiles(
        st.session_state["region_id"],
        st.session_state["split_by"],
        dates=date_range,
    )
    # transfrom unit to [MW]
    regional_profiles["value"] = regional_profiles["value"] * 1e-3
    fig = px.area(
        regional_profiles,
        x="time",
        y="value",
        color="industry_id",
        labels={"value": "MW", "time": "Time", "industry_id": "Industry type"},
    )
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Data"):
        regional_profiles_wide = regional_profiles.pivot(
            index="time", columns="industry_id", values="value"
        )
        st.dataframe(regional_profiles_wide, use_container_width=True)
        download_excel_file(
            f"synthetic-load-profiles-{st.session_state['region_id']}-{st.session_state['split_by']}.xlsx",
            regional_profiles_wide,
            "Download table as .xlsx",
        )


st.title("Regional synthetic load data")

st.write(
    "On this page, synthetic load data is disaggregated to a specific region based on the number of employees or number of production sites in the respective region."
)

# load cap and site data from database:
cap_and_site_data = pd.read_csv(DATA_DIR / "cap_and_site_data.csv", dtype={"id": str})

# load weights for transforming to industry types:
shares = pd.read_csv(DATA_DIR / "industry_type_2_wz2008_shares.csv")

# load geometry:
gdf = get_region_geometry_from_csv()
industry_data = get_industry_type_regional_distribution()
region_names = {k: v for k, v in zip(industry_data["id"], industry_data["name"])}

st.sidebar.header("Settings")
region_id = st.sidebar.selectbox(
    "Region",
    options=industry_data.sort_values("name")["id"].unique(),
    index=0,
    placeholder="Select region...",
    format_func=lambda x: region_names.get(x, x),
    key="region_id",
)

split_by = st.sidebar.selectbox(
    "Disaggregation parameter",
    options=("n_cap", "n_sites"),
    index=0,
    format_func=lambda x: {
        "n_cap": "Number of employees",
        "n_sites": "Number of production sites",
    }.get(x, x),
    key="split_by",
)


with st.container(border=True):
    st.header("Industry types in selected region")
    st.write(f"Data for {region_names.get(st.session_state['region_id'])}:")

    df_show = industry_data.loc[
        industry_data.id == st.session_state["region_id"]
    ].sort_values(by="sector_agg", ascending=False)

    fig = px.bar(
        df_show,
        y="sector_agg",
        x=st.session_state["split_by"],
        orientation="h",
        height=800,
        labels={
            "n_cap": "Number of employees",
            "n_sites": "Number of production sites",
            "sector_agg": "Industry type",
        },
    )
    st.plotly_chart(fig, use_container_width=True)


with st.container(border=True):
    st.header("Regional distribution of selected disaggregation parameter")
    map_and_widget(gdf, industry_data)


with st.container(border=True):
    st.header("Load profile in selected region")
    regional_profile_with_date_range_widget()


# this placeholder is needed at the bottom of the page to prevent scroll-jumping
# during widget interaction in the interactive figure
st.container(height=1000, border=False)

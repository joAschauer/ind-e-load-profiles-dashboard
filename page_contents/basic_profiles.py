# -*- coding: utf-8 -*-
"""Content of basic profiles page."""

import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache_data()
def load_profiles_from_csv(aggregate_end_use_types):
    if aggregate_end_use_types:
        return pd.read_csv(
            "data/profile_data_aggregate_end_use_types.csv", parse_dates=["time"]
        )
    else:
        return pd.read_csv("data/profile_data.csv", parse_dates=["time"])


@st.cache_data()
def load_end_use_shares_from_csv(aggregate_end_use_types):
    if aggregate_end_use_types:
        return pd.read_csv("data/end_use_shares_aggregate_end_use_types.csv")
    else:
        return pd.read_csv("data/end_use_shares.csv")


st.header("Basic end use profiles")

if "aggregate_end_use_types" not in st.session_state.keys():
    st.session_state["aggregate_end_use_types"] = False

st.session_state["aggregate_end_use_types"] = st.checkbox("Aggregate end user types?")


df_profiles = load_profiles_from_csv(st.session_state["aggregate_end_use_types"])

fig = px.area(
    df_profiles,
    x="time",
    y="value",
    facet_row="day",
    facet_col="end_use_type",
    facet_row_spacing=0.1,
    height=700,
)

st.plotly_chart(fig, use_container_width=True)

df_shares = load_end_use_shares_from_csv(st.session_state["aggregate_end_use_types"])

fig = px.bar(
    df_shares,
    y="industry_type",
    x="share_fraction",
    color="end_use_type",
    orientation="h",
)
st.plotly_chart(fig, use_container_width=True)

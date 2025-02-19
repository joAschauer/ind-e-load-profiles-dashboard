# -*- coding: utf-8 -*-
"""Content of Synthetic profiles tab."""

from datetime import datetime

import plotly.express as px
import streamlit as st

from page_contents.components import download_excel_file
from src.load_generator import (
    modul_1_IND_E,
    modul_2_IND_E,
    modul_3_IND_E,
    modul_4_IND_E,
)

st.title("Generate synthetic load data")


# """Lege Pfad fest, wo Ergebnisse abgelegt werden"""
PROFILES_DATA_PATH = "data/profiles"

all_info_wz = modul_1_IND_E.get_industry_type_data(PROFILES_DATA_PATH)


with st.expander("Characteristics of all industry types"):
    st.dataframe(all_info_wz, column_config={"WZ_ID": st.column_config.TextColumn()})


st.header("Settings")
settings_container = st.container(border=True)
year = 2019  # we do not have data for 2017 and 2018, so we fix it to 2019

with settings_container:
    industry_name = st.selectbox("Industry type", all_info_wz["Name"], index=0)

industry_number = int(
    all_info_wz.set_index("Name").at[industry_name, "industry_number"]
)


# """Ausführen von Modul 1:
# Normierte Lastprofile pro Typtag"""
(
    weekday_1,
    saturday_1,
    sunday_1,
    holiday_1,
    constant_1,
    data_industry_type,
) = modul_1_IND_E.modul_1_el(industry_number, PROFILES_DATA_PATH)

with settings_container:
    cols = st.columns(4)
    with cols[0]:
        data_industry_type["Fluktuation"] = st.select_slider(
            "Fluctuation",
            range(0, 100),
            value=data_industry_type["Fluktuation"].values[0],
        )
    with cols[1]:
        data_industry_type["Energieverbrauch 2019"] = st.number_input(
            "Energy consumption",
            value=data_industry_type["Energieverbrauch 2019"].values[0],
        )
    with cols[2]:
        data_industry_type["Peak_faktor"] = st.number_input(
            "Peak factor",
            value=data_industry_type["Peak_faktor"].values[0],
        )
    with cols[3]:
        data_industry_type["Base_faktor"] = st.number_input(
            "Base factor:",
            value=data_industry_type["Base_faktor"].values[0],
        )

industry_type = data_industry_type["WZ_ID"][industry_number]

# """Ausführen von Modul 2:
# Anpassung in vertikaler Richtung, Strecken und Stauchen
# anhand base_ und peak_faktoren"""
weekday_2, saturday_2, sunday_2, holiday_2, constant_2 = modul_2_IND_E.modul_2(
    year,
    industry_number,
    data_industry_type,
    weekday_1,
    saturday_1,
    sunday_1,
    holiday_1,
    constant_1,
)

# """Ausführen von Modul 3:
# Zusammensetzen der Tageslastgänge zu Lastgang 1 Jahr, Normierung
# auf Verbrauch von 1000 MWh/a"""
year_list, array_load_type = modul_3_IND_E.modul_3(year)
df = modul_3_IND_E.seasonality(
    year,
    year_list,
    array_load_type,
    weekday_2,
    saturday_2,
    sunday_2,
    holiday_2,
    constant_2,
    PROFILES_DATA_PATH,
)

df_year_3 = modul_3_IND_E.normalising_1000(df)

# """Ausführen von Modul 4:
# Skalieren auf Jahresverbrauch und Aufprägung der Fluktuationen"""
df_year_4 = modul_4_IND_E.modul_4(year, industry_number, df_year_3, data_industry_type)
df_year_4 = modul_4_IND_E.modul_4_fluct(industry_number, df_year_4, data_industry_type)

st.header("Germany wide load profile")
with st.container(border=True):
    date_range = st.slider(
        "select range for plot",
        value=(datetime(2019, 1, 1, 0, 0), datetime(2019, 1, 14, 0, 0)),
        min_value=datetime(2019, 1, 1, 0, 0),
        max_value=datetime(2019, 12, 31, 23, 45),
        format="YYYY/MM/DD - HH:mm",
        label_visibility="hidden",
    )

    fig = px.area(
        df_year_4.drop("Total", axis=1)
        .multiply(1e-3)
        .loc[date_range[0] : date_range[1], :],
        title=f"{industry_name} (WZ {industry_type})",
        labels={"value": "MW", "index": "Time", "variable": "End use type"},
    )
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("Data"):
        st.dataframe(df_year_4 * 1e-3, use_container_width=True)
        download_excel_file(
            f"synthetic-load-profiles-germany-{industry_name.lower().replace(' ', '')}.xlsx",
            df_year_4,
            "Download table as .xlsx",
        )

# this placeholder is needed at the bottom of the page to prevent scroll-jumping
# during widget interaction in the interactive figure
st.container(height=1000, border=False)

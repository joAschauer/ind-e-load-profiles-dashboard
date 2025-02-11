# -*- coding: utf-8 -*-
"""Content of Synthetic profiles tab."""

from datetime import datetime

import plotly.express as px
import streamlit as st

from src.load_generator import (
    modul_1_IND_E,
    modul_2_IND_E,
    modul_3_IND_E,
    modul_4_IND_E,
)

st.title("Synthetic load data")


# """Lege Pfad fest, wo Ergebnisse abgelegt werden"""
PROFILES_DATA_PATH = "data/profiles"

all_info_wz = modul_1_IND_E.get_industry_type_data(PROFILES_DATA_PATH)

st.subheader("Eigenschaften aller Industrietypen:")

st.dataframe(all_info_wz, column_config={"WZ_ID": st.column_config.TextColumn()})


st.sidebar.subheader("Einstellungen:")
year = st.sidebar.selectbox("Jahr:", [2018, 2019, 2020], index=1)

industry_name = st.sidebar.selectbox("Industry type:", all_info_wz["Name"], index=0)
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

st.write(data_industry_type)
st.sidebar.subheader("Parameter zu ausgewähltem Industrietyp:")
data_industry_type["Fluktuation"] = st.sidebar.select_slider(
    "Fluktuation:", range(0, 100), value=data_industry_type["Fluktuation"].values[0]
)

data_industry_type["Energieverbrauch 2019"] = st.sidebar.number_input(
    "Energieverbrauch 2019:",
    value=data_industry_type["Energieverbrauch 2019"].values[0],
)

data_industry_type["Peak_faktor"] = st.sidebar.number_input(
    "Peak_faktor:",
    value=data_industry_type["Peak_faktor"].values[0],
)

data_industry_type["Base_faktor"] = st.sidebar.number_input(
    "Base_faktor:",
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

st.subheader("Final Profile")

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
    labels={"value": "MW", "index": "Zeit"},
)
st.plotly_chart(fig, use_container_width=True)
with st.expander("Data"):
    st.dataframe(df_year_4 * 1e-3, use_container_width=True)

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 15:52:10 2021.

@author: asandhaa
"""

from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def get_industry_type_data(data_path):
    """Input 2: Tabelle mit allen Informationen zu Industrietypen."""
    all_info_wz = pd.read_excel(
        Path(data_path) / "Electrical" / "All_info_industry_types_electrical.xlsx",
        skipfooter=1,
    ).drop(0)
    all_info_wz.dropna(how="all", axis=0, inplace=True)
    all_info_wz.dropna(how="all", axis=1, inplace=True)
    all_info_wz.fillna(0, inplace=True)
    all_info_wz["WZ_ID"] = all_info_wz["WZ_ID"].astype("str")
    return all_info_wz


@st.cache_data
def modul_1_el(industry_number, data_path):
    """Input 1: Normierte Tageslastprofile Load_profiles_enduser.xlsx."""
    load_prof_enduser = pd.read_excel(
        Path(data_path) / "Electrical" / "Load_profiles_enduser.xlsx",
        usecols=("B:J"),
        sheet_name="Week_day",
    )
    load_prof_enduser.drop("unstetige mech. Antriebe", axis=1, inplace=True)
    load_prof_enduser.dropna(axis=0, inplace=True)
    profiles_weekday = load_prof_enduser.rename(
        columns={"stetige mech. Antriebe": "Mechanische Antriebe"}
    )

    load_prof_enduser = pd.read_excel(
        Path(data_path) / "Electrical" / "Load_profiles_enduser.xlsx",
        usecols=("B:J"),
        sheet_name="Saturday",
    )
    load_prof_enduser.drop("unstetige mech. Antriebe", axis=1, inplace=True)
    load_prof_enduser.dropna(axis=0, inplace=True)
    profiles_saturday = load_prof_enduser.rename(
        columns={"stetige mech. Antriebe": "Mechanische Antriebe"}
    )

    load_prof_enduser = pd.read_excel(
        Path(data_path) / "Electrical" / "Load_profiles_enduser.xlsx",
        usecols=("B:J"),
        sheet_name="Sunday",
    )
    load_prof_enduser.drop("unstetige mech. Antriebe", axis=1, inplace=True)
    load_prof_enduser.dropna(axis=0, inplace=True)
    profiles_sunday = load_prof_enduser.rename(
        columns={"stetige mech. Antriebe": "Mechanische Antriebe"}
    )

    load_prof_enduser = pd.read_excel(
        Path(data_path) / "Electrical" / "Load_profiles_enduser.xlsx",
        usecols=("B:J"),
        sheet_name="Holiday",
    )
    load_prof_enduser.drop("unstetige mech. Antriebe", axis=1, inplace=True)
    load_prof_enduser.dropna(axis=0, inplace=True)
    profiles_holiday = load_prof_enduser.rename(
        columns={"stetige mech. Antriebe": "Mechanische Antriebe"}
    )

    profiles_constant = profiles_weekday.copy()
    profiles_constant.loc[:, :] = 1

    """Input 2: Tabelle mit allen Informationen zu Industrietypen"""

    all_info_wz = get_industry_type_data(data_path)

    """Filtern der Infos für ausgewählten Industrietyp"""

    data_industry_type = all_info_wz[
        all_info_wz.industry_number.eq(industry_number)
    ]  # filters the row with specific industry_wz
    energy_enduser_industry_type = data_industry_type[
        [
            "Raumwärme",
            "Warmwasser",
            "Prozesswärme",
            "Klimakälte",
            "Prozesskälte",
            "Beleuchtung",
            "IKT",
            "Mechanische Antriebe",
        ]
    ].values  # extracts enduser values
    energy_enduser_industry_type = energy_enduser_industry_type.astype(float)

    """ERSTELLUNG normierter Tageslastprofile"""

    """WEEK DAY"""
    y = profiles_weekday.mul(
        energy_enduser_industry_type, axis=1
    )  # Anwendungsprofile * Anteile der Anwendungen
    y["Total"] = y.sum(axis=1)
    weekday_1 = y

    """SATURDAY"""
    y = profiles_saturday.mul(
        energy_enduser_industry_type, axis=1
    )  # Anwendungsprofile * Anteile der Anwendungen
    y["Total"] = y.sum(axis=1)
    saturday_1 = y

    """SUNDAY"""
    y = profiles_sunday.mul(
        energy_enduser_industry_type, axis=1
    )  # Anwendungsprofile * Anteile der Anwendungen
    y["Total"] = y.sum(axis=1)
    sunday_1 = y

    """HOLIDAY"""
    y = profiles_holiday.mul(
        energy_enduser_industry_type, axis=1
    )  # Anwendungsprofile * Anteile der Anwendungen
    y["Total"] = y.sum(axis=1)
    holiday_1 = y

    """Constant"""
    y = profiles_constant.mul(
        energy_enduser_industry_type, axis=1
    )  # Anwendungsprofile * Anteile der Anwendungen
    y["Total"] = y.sum(axis=1)
    constant_1 = y

    return (weekday_1, saturday_1, sunday_1, holiday_1, constant_1, data_industry_type)


def modul_1_th(industry_number, data_path):
    """Input 1: Normierte Tageslastprofile Load_profiles_enduser.xlsx."""
    profiles_weekday = pd.read_excel(
        Path(data_path) / "Thermal" / "Load_profiles_daytypes.xlsx",
        sheet_name="Week_day",
        index_col=0,
    )
    profiles_saturday = pd.read_excel(
        Path(data_path) / "Thermal" / "Load_profiles_daytypes.xlsx",
        sheet_name="Saturday",
        index_col=0,
    )
    profiles_sunday = pd.read_excel(
        Path(data_path) / "Thermal" / "Load_profiles_daytypes.xlsx",
        sheet_name="Sunday",
        index_col=0,
    )
    profiles_holiday = pd.read_excel(
        Path(data_path) / "Thermal" / "Load_profiles_daytypes.xlsx",
        sheet_name="Holiday",
        index_col=0,
    )

    profiles_constant = profiles_weekday.copy()
    profiles_constant.loc[:, :] = 1

    """Input 2: Tabelle mit allen Informationen zu Industrietypen"""

    all_info_wz = pd.read_excel(
        Path(data_path) / "Thermal" / "All_info_industry_types_thermal.xlsx".format()
    )
    all_info_wz.dropna(how="all", axis=0, inplace=True)
    all_info_wz.dropna(how="all", axis=1, inplace=True)
    all_info_wz.fillna(0, inplace=True)

    """Filtern der Infos für ausgewählten Industrietyp"""

    data_industry_type = all_info_wz[
        all_info_wz.industry_number.eq(industry_number)
    ]  # filters the row with specific industry_wz
    energy_enduser_industry_type = data_industry_type.iloc[
        :, 3:9
    ]  # extracts temp range values
    energy_enduser_industry_type = energy_enduser_industry_type.astype(float)

    """ERSTELLUNG normierter Tageslastprofile"""

    """WEEK DAY"""
    y = pd.DataFrame(
        index=profiles_weekday.index, columns=energy_enduser_industry_type.columns
    )
    for i in range(len(y.columns)):
        y.iloc[:, i] = profiles_weekday * float(energy_enduser_industry_type.iloc[:, i])
    y["Total"] = y.sum(axis=1)
    weekday_1 = y

    """SATURDAY"""
    y = pd.DataFrame(
        index=profiles_saturday.index, columns=energy_enduser_industry_type.columns
    )
    for i in range(len(y.columns)):
        y.iloc[:, i] = profiles_saturday * float(
            energy_enduser_industry_type.iloc[:, i]
        )
    y["Total"] = y.sum(axis=1)
    saturday_1 = y

    """SUNDAY"""
    y = pd.DataFrame(
        index=profiles_sunday.index, columns=energy_enduser_industry_type.columns
    )
    for i in range(len(y.columns)):
        y.iloc[:, i] = profiles_sunday * float(energy_enduser_industry_type.iloc[:, i])
    y["Total"] = y.sum(axis=1)
    sunday_1 = y

    """HOLIDAY"""
    y = pd.DataFrame(
        index=profiles_holiday.index, columns=energy_enduser_industry_type.columns
    )
    for i in range(len(y.columns)):
        y.iloc[:, i] = profiles_holiday * float(energy_enduser_industry_type.iloc[:, i])
    y["Total"] = y.sum(axis=1)
    holiday_1 = y

    """CONSTANT"""
    y = pd.DataFrame(
        index=profiles_constant.index, columns=energy_enduser_industry_type.columns
    )
    for i in range(len(y.columns)):
        y.iloc[:, i] = profiles_constant * float(
            energy_enduser_industry_type.iloc[:, i]
        )
    y["Total"] = y.sum(axis=1)
    constant_1 = y

    return weekday_1, saturday_1, sunday_1, holiday_1, constant_1, data_industry_type

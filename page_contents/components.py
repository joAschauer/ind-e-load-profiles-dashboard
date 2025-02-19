# download button for excel file:
import io

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def create_excel_file(df: pd.DataFrame) -> io.BytesIO:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, merge_cells=False)
    return buffer


def download_excel_file(
    filename: str,
    df: pd.DataFrame,
    label: str = "Tabelle als .xlsx herunterladen",
    key: str = "excel-download",
):
    if st.button("Prepare data for Excel download", key=f"btn-{key}"):
        buffer = create_excel_file(df)
        st.download_button(
            label=label,
            icon=":material/download:",
            data=buffer,
            file_name=filename,
            mime="application/vnd.ms-excel",
        )

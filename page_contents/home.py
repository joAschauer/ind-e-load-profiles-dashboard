from pathlib import Path

import streamlit as st

st.title("IND-E industry load profiles")

st.markdown(
    """This dashboard lets you view and download synthetic load profiles for different industry sectors.
    It was developed as part of the IND-E project.
    """
)
st.image(Path("assets/BMWK_Fz_2017_Web2x_en.gif"))

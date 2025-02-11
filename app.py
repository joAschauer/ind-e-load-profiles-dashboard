import streamlit as st

st.set_page_config(layout="wide")

page = st.navigation(
    [
        st.Page("page_contents/home.py", title="Home", default=True),
        st.Page(
            "page_contents/basic_profiles.py",
            title="View basic profiles",
            url_path="basic_profiles",
        ),
        st.Page(
            "page_contents/synthetic_profiles.py",
            title="Generate synthetic profiles",
            url_path="synthetic_profiles",
        ),
        st.Page(
            "page_contents/regional_data.py",
            title="View regional data",
            url_path="regionl_data",
        ),
    ],
    position="sidebar",
)
page.run()

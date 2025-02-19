import streamlit as st

st.set_page_config(layout="wide")


# https://discuss.streamlit.io/t/keep-menu-without-header/46558/2
st.markdown(
    """
<style>
	[data-testid="stDecoration"] {
        background: #FFFFFF;
    }

</style>""",
    unsafe_allow_html=True,
)


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
            url_path="regional_data",
        ),
    ],
    position="sidebar",
)
page.run()

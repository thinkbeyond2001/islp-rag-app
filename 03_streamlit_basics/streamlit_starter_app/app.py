import streamlit as st
from pages.home import show_home
from pages.upload_and_explore import show_upload_and_explore
from pages.custom_logic import show_custom_logic
from pages.about import show_about

st.set_page_config(
    page_title="Streamlit Starter App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Shared frame / layout
st.sidebar.title("🚀 Streamlit Starter App")
st.sidebar.caption("A practical starter project for learning Streamlit.")

pages = [
    st.Page(show_home, title="Home", icon="🏠", default=True),
    st.Page(show_upload_and_explore, title="Upload + Charts", icon="📊"),
    st.Page(show_custom_logic, title="Custom Logic", icon="🧠"),
    st.Page(show_about, title="About / Next Steps", icon="📚"),
]

pg = st.navigation(pages, position="sidebar", expanded=True)
pg.run()
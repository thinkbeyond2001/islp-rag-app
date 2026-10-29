import streamlit as st
import pandas as pd

def show_home():
    st.title("Build Fast with Streamlit")
    st.write(
        """
        This app demonstrates the core pieces most people need to get started:

        - **Navigation** across multiple pages
        - **File upload** for CSV data
        - **Interactive charts**
        - **Session state**
        - **Custom business logic**
        - **Clean app structure** you can extend later
        """
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Pages", 4)
    col2.metric("Upload Support", "CSV")
    col3.metric("Starter Pattern", "Multipage")

    st.subheader("How Streamlit works")
    st.code(
        """
# 1) Write Python
import streamlit as st

# 2) Use Streamlit commands
st.title("Hello Streamlit")
name = st.text_input("Your name")

# 3) React to widget state automatically
if name:
    st.success(f"Welcome, {name}!")
        """.strip(),
        language="python"
    )

    st.subheader("Tiny demo dataset")
    demo = pd.DataFrame(
        {
            "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "sales": [120, 155, 143, 180, 210, 195],
            "profit": [30, 42, 38, 55, 67, 61],
        }
    )
    st.dataframe(demo, use_container_width=True)
    st.line_chart(demo.set_index("month")[["sales", "profit"]])

    st.info(
        "Use the sidebar to move through the app. The Upload + Charts page is the most practical place to start."
    )
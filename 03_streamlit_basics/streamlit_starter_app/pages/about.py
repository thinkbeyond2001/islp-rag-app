import streamlit as st

def show_about():
    st.title("What to Learn Next")

    st.markdown(
        """
        **The big idea:** Streamlit is best when you want to turn Python workflows
        into interactive internal tools quickly.

        **What you now have in this starter app:**
        - a modern multipage structure
        - widgets and layout primitives
        - data upload
        - charts
        - session state
        - custom transformation logic
        - downloadable outputs

        **What to learn after this:**
        1. `st.session_state` for persistent user interactions
        2. caching with `st.cache_data`
        3. forms with `st.form`
        4. sidebar filters
        5. deployment to Streamlit Community Cloud or your own server
        6. authentication and database connections
        7. agent/chat workflows if you want AI features
        """
    )

    st.subheader("Run locally")
    st.code(
        """
pip install -r requirements.txt
streamlit run app.py
        """.strip(),
        language="bash"
    )

    st.subheader("A few practical tips")
    st.write(
        """
        - Keep app code small and modular.
        - Put expensive data loads behind caching.
        - Start with CSVs and pandas before connecting databases.
        - Build around one core workflow, not ten half-features.
        - Use Streamlit for internal tools first. That is where it shines fastest.
        """
    )
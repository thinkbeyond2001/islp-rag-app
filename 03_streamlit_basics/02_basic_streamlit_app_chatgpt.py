# USING CHATGPT TO CREATE A STREAMLIT APP

# * ChatGPT Prompt: 
# Make a streamlit app in python that showcases the main features of streamlit including navigation, home page, data upload, charts, and custom logic. Anything you think I need to know to get started. 

import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# -----------------------------
# App setup
# -----------------------------
st.set_page_config(
    page_title="Streamlit Feature Showcase",
    page_icon="🧭",
    layout="wide",
)

# -----------------------------
# Sidebar: Navigation + globals
# -----------------------------
PAGES = ["Home", "Upload Data", "Charts", "Custom Logic Playground", "About"]

with st.sidebar:
    st.title("🧭 Navigation")
    page = st.radio("Go to", PAGES, index=0)

    st.divider()
    st.subheader("Global Controls")
    theme = st.selectbox("Chart theme", ["default", "dark"], index=0)
    st.caption("These controls are shared across pages.")

# -----------------------------
# Helpers + session state
# -----------------------------
def init_state():
    if "df" not in st.session_state:
        st.session_state.df = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

init_state()


@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def load_excel(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_excel(io.BytesIO(file_bytes))


def apply_theme(chart: alt.Chart) -> alt.Chart:
    if theme == "dark":
        return chart.configure(background="#111111").configure_axis(
            labelColor="#FFFFFF",
            titleColor="#FFFFFF",
            gridColor="#333333",
        ).configure_legend(labelColor="#FFFFFF", titleColor="#FFFFFF")
    return chart


def make_synthetic_data(n=200, seed=7):
    rng = np.random.default_rng(seed)
    x = np.arange(n)
    y = np.cumsum(rng.normal(0, 1, size=n)) + 50
    cat = rng.choice(["A", "B", "C"], size=n, p=[0.4, 0.35, 0.25])
    df = pd.DataFrame({"t": x, "value": y, "category": cat})
    return df


# -----------------------------
# Page: Home
# -----------------------------
if page == "Home":
    st.title("Streamlit Feature Showcase")
    st.write(
        "This app demonstrates **navigation**, **file upload**, **tables**, **charts**, "
        "and **custom logic** with session state + caching."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Pages", len(PAGES))
    col2.metric("Data Loaded", "Yes ✅" if st.session_state.df is not None else "No ❌")
    col3.metric("Notes Saved", len(st.session_state.messages))

    st.divider()
    st.subheader("Quick Start")
    st.code("streamlit run app.py", language="bash")

    with st.expander("Generate sample data (optional)", expanded=True):
        n = st.slider("Rows", 50, 2000, 300, step=50)
        seed = st.number_input("Seed", value=7, step=1)
        if st.button("Create sample dataset"):
            st.session_state.df = make_synthetic_data(n=n, seed=seed)
            st.success("Sample data created and stored in session_state.df")

    st.subheader("Current dataset preview")
    if st.session_state.df is None:
        st.info("No data yet. Go to **Upload Data** or generate sample data above.")
    else:
        st.dataframe(st.session_state.df.head(50), use_container_width=True)

# -----------------------------
# Page: Upload Data
# -----------------------------
elif page == "Upload Data":
    st.title("📤 Upload Data")
    st.write("Upload a CSV or Excel file. The parsed DataFrame is stored in **session_state**.")

    uploaded = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

    colA, colB = st.columns([2, 1])

    with colA:
        if uploaded is not None:
            try:
                file_bytes = uploaded.getvalue()
                if uploaded.name.lower().endswith(".csv"):
                    df = load_csv(file_bytes)
                else:
                    df = load_excel(file_bytes)

                st.session_state.df = df
                st.success(f"Loaded {uploaded.name} — shape: {df.shape[0]} rows × {df.shape[1]} cols")
                st.dataframe(df.head(200), use_container_width=True)
            except Exception as e:
                st.error(f"Could not load file: {e}")

        st.divider()
        st.subheader("Optional: data cleaning helpers")
        if st.session_state.df is not None:
            df = st.session_state.df

            with st.form("cleaning_form"):
                drop_na = st.checkbox("Drop rows with NA", value=False)
                dedupe = st.checkbox("Remove duplicate rows", value=False)
                max_rows = st.number_input("Limit rows (0 = no limit)", min_value=0, value=0, step=100)
                submitted = st.form_submit_button("Apply cleaning")

            if submitted:
                df2 = df.copy()
                if drop_na:
                    df2 = df2.dropna()
                if dedupe:
                    df2 = df2.drop_duplicates()
                if max_rows and max_rows > 0:
                    df2 = df2.head(int(max_rows))

                st.session_state.df = df2
                st.success(f"Updated dataset — shape: {df2.shape}")
                st.dataframe(df2.head(200), use_container_width=True)
        else:
            st.info("Load or generate a dataset first.")

    with colB:
        st.subheader("Tips")
        st.markdown(
            """
- **CSV** is easiest.
- Excel requires `openpyxl` (usually installed automatically with pandas).
- Use `st.cache_data` for expensive parsing.
- Store shared data in `st.session_state`.
            """
        )

# -----------------------------
# Page: Charts
# -----------------------------
elif page == "Charts":
    st.title("📊 Charts")
    st.write("Interactive charting with filters. Works best if your dataset has numeric columns.")

    if st.session_state.df is None:
        st.info("No data loaded. Go to **Upload Data** or create sample data on **Home**.")
    else:
        df = st.session_state.df

        # Detect numeric + categorical columns
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

        if not numeric_cols:
            st.warning("No numeric columns found. Upload a dataset with at least one numeric column.")
        else:
            left, right = st.columns([1, 2])

            with left:
                st.subheader("Controls")
                y_col = st.selectbox("Y (numeric)", numeric_cols, index=0)
                x_col = st.selectbox("X (optional)", ["(row index)"] + numeric_cols + cat_cols, index=0)

                color_by = None
                if cat_cols:
                    color_by = st.selectbox("Color by (optional)", ["(none)"] + cat_cols, index=0)
                    if color_by == "(none)":
                        color_by = None

                chart_type = st.selectbox("Chart type", ["Line", "Bar", "Scatter"], index=0)

                # Optional filtering by category
                filter_col = None
                filter_values = None
                if cat_cols:
                    filter_col = st.selectbox("Filter column (optional)", ["(none)"] + cat_cols, index=0)
                    if filter_col != "(none)":
                        filter_values = st.multiselect(
                            f"Keep values of {filter_col}",
                            sorted(df[filter_col].dropna().astype(str).unique().tolist())
                        )

            # Prepare data
            plot_df = df.copy()
            if filter_col and filter_col != "(none)" and filter_values:
                plot_df = plot_df[plot_df[filter_col].astype(str).isin(filter_values)]

            if x_col == "(row index)":
                plot_df = plot_df.reset_index(drop=False).rename(columns={"index": "__row_index__"})
                x_field = "__row_index__"
                x_type = "quantitative"
            else:
                x_field = x_col
                x_type = "quantitative" if x_field in numeric_cols else "nominal"

            with right:
                st.subheader("Chart")
                base = alt.Chart(plot_df)

                enc = {
                    "x": alt.X(x_field, type=x_type),
                    "y": alt.Y(y_col, type="quantitative"),
                    "tooltip": list(plot_df.columns[:20]),
                }

                if color_by:
                    enc["color"] = alt.Color(color_by, type="nominal")

                if chart_type == "Line":
                    chart = base.mark_line().encode(**enc)
                elif chart_type == "Bar":
                    chart = base.mark_bar().encode(**enc)
                else:
                    chart = base.mark_circle(size=60, opacity=0.7).encode(**enc)

                chart = apply_theme(chart).interactive()
                st.altair_chart(chart, use_container_width=True)

                st.caption(f"Rows shown: {len(plot_df):,}")

# -----------------------------
# Page: Custom Logic Playground
# -----------------------------
elif page == "Custom Logic Playground":
    st.title("🧪 Custom Logic Playground")
    st.write(
        "This page demonstrates **session state**, **forms**, **callbacks**, and basic app logic."
    )

    tabs = st.tabs(["Notes (session state)", "Simple KPI Engine", "Reset"])

    with tabs[0]:
        st.subheader("Save notes (persists while app is running)")
        with st.form("note_form"):
            note = st.text_input("Add a note")
            submitted = st.form_submit_button("Save")
        if submitted and note.strip():
            st.session_state.messages.append(note.strip())
            st.success("Saved!")

        if st.session_state.messages:
            st.write("Saved notes:")
            for i, msg in enumerate(st.session_state.messages[::-1], start=1):
                st.write(f"{i}. {msg}")
        else:
            st.info("No notes yet.")

    with tabs[1]:
        st.subheader("Simple KPI Engine (custom logic)")
        st.write("Pick a numeric column and compute metrics with configurable thresholds.")

        if st.session_state.df is None:
            st.info("Load data first to use KPI Engine.")
        else:
            df = st.session_state.df
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

            if not numeric_cols:
                st.warning("No numeric columns found.")
            else:
                col = st.selectbox("Metric column", numeric_cols, index=0)
                threshold = st.slider("Threshold", float(df[col].min()), float(df[col].max()), float(df[col].mean()))

                series = df[col].dropna()
                above = (series > threshold).mean() if len(series) else 0.0

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Mean", f"{series.mean():.3f}")
                c2.metric("Median", f"{series.median():.3f}")
                c3.metric("Std", f"{series.std():.3f}")
                c4.metric("% > Threshold", f"{above*100:.1f}%")

                # Small histogram
                hist_df = pd.DataFrame({col: series})
                chart = alt.Chart(hist_df).mark_bar().encode(
                    x=alt.X(f"{col}:Q", bin=True),
                    y="count()",
                    tooltip=["count()"],
                )
                st.altair_chart(apply_theme(chart), use_container_width=True)

    with tabs[2]:
        st.subheader("Reset state")
        if st.button("Clear loaded dataset"):
            st.session_state.df = None
            st.success("Cleared dataset.")
        if st.button("Clear saved notes"):
            st.session_state.messages = []
            st.success("Cleared notes.")

# -----------------------------
# Page: About
# -----------------------------
else:
    st.title("ℹ️ About")
    st.markdown(
        """
**What this app demonstrates**
- **Navigation** via sidebar `st.radio`
- **Home page** with metrics, expanders, and dataset preview
- **Upload page** with `st.file_uploader` + caching
- **Charts** using Altair + interactive filters
- **Custom logic** with `st.session_state`, tabs, and forms

**Next steps**
- Add authentication (Streamlit Community Cloud secrets or external auth)
- Persist data (S3, Postgres, DuckDB)
- Deploy (Streamlit Community Cloud, Docker, or a VM)
        """
    )

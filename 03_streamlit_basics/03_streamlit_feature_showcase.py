import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from typing import Optional

st.set_page_config(
    page_title="Streamlit Feature Showcase",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

REQUIRED_KPI_COLUMNS = {"spend", "revenue"}


@st.cache_data
def make_sample_data(rows: int = 365) -> pd.DataFrame:
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=rows)
    channels = ["Search", "Social", "Email", "Affiliate", "Display"]
    rng = np.random.default_rng(42)
    data = {
        "date": dates,
        "channel": rng.choice(channels, size=rows),
        "spend": np.clip(rng.normal(500, 120, size=rows), a_min=50, a_max=None).round(2),
        "clicks": rng.integers(50, 1200, size=rows),
    }
    df = pd.DataFrame(data)
    df["conversions"] = (df["clicks"] * rng.uniform(0.02, 0.08, size=rows)).round(0)
    df["revenue"] = np.clip(
        df["conversions"] * rng.normal(45, 12, size=rows),
        a_min=0,
        a_max=None,
    ).round(2)
    df["ctr"] = (df["clicks"] / df["spend"]).round(3)
    return df


@st.cache_data
def load_uploaded_data(uploaded_file) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(uploaded_file)
    return None


if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

if "notes" not in st.session_state:
    st.session_state.notes = ""


st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Upload Data", "Charts", "Custom Logic", "About"],
)


def get_active_data() -> pd.DataFrame:
    if st.session_state.uploaded_df is not None:
        return st.session_state.uploaded_df
    return make_sample_data()


def show_data_health(df: pd.DataFrame) -> None:
    st.subheader("Data health")
    cols = df.columns
    st.write(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")
    missing = df.isna().mean().sort_values(ascending=False)
    if missing.max() > 0:
        st.write("Missing values by column")
        st.dataframe(missing.to_frame("missing_rate").head(10), use_container_width=True)
    else:
        st.success("No missing values detected.")


if page == "Home":
    st.title("Streamlit Feature Showcase")
    st.write(
        "This app demonstrates common Streamlit features: navigation, data upload, "
        "interactive charts, and custom logic. Use the sidebar to explore."
    )

    st.subheader("Quick start")
    st.code("streamlit run 03_streamlit_basics/03_streamlit_feature_showcase.py", language="bash")

    st.subheader("What you'll see")
    st.markdown(
        "- **Navigation**: Sidebar radio to move between pages.\n"
        "- **Data upload**: CSV or Excel.\n"
        "- **Charts**: Choose chart type and columns.\n"
        "- **Custom logic**: KPI calculations, filters, and notes."
    )

    st.subheader("Sample data preview")
    st.dataframe(make_sample_data().head(10), use_container_width=True)

elif page == "Upload Data":
    st.title("Upload Data")
    st.write("Upload a CSV or Excel file to use in the charts and custom logic pages.")

    with st.form("upload_form"):
        uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])
        use_sample = st.checkbox("Keep sample data instead", value=False)
        submitted = st.form_submit_button("Load data")

    if submitted:
        if use_sample:
            st.session_state.uploaded_df = None
            st.success("Using sample data.")
        else:
            df = load_uploaded_data(uploaded_file)
            if df is None:
                st.error("Unsupported file type. Please upload CSV or Excel.")
            else:
                st.session_state.uploaded_df = df
                st.success(f"Loaded {df.shape[0]:,} rows and {df.shape[1]} columns.")

    active_df = get_active_data()
    st.subheader("Current data")
    st.dataframe(active_df.head(20), use_container_width=True)
    show_data_health(active_df)

elif page == "Charts":
    st.title("Charts")
    df = get_active_data()

    st.write("Pick columns to visualize your data.")
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    all_cols = df.columns.tolist()

    if not all_cols:
        st.warning("No columns available for charting.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            chart_type = st.selectbox("Chart type", ["Line", "Bar", "Scatter"])
        with col2:
            x_col = st.selectbox("X-axis", all_cols, index=0)
        with col3:
            y_col = st.selectbox("Y-axis", numeric_cols if numeric_cols else all_cols)

        color_col = st.selectbox("Color", ["None"] + all_cols)
        color = None if color_col == "None" else color_col

        if chart_type == "Line":
            fig = px.line(df, x=x_col, y=y_col, color=color, markers=True)
        elif chart_type == "Bar":
            fig = px.bar(df, x=x_col, y=y_col, color=color)
        else:
            fig = px.scatter(df, x=x_col, y=y_col, color=color)

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Quick stats")
        st.dataframe(df.describe(include="all").T, use_container_width=True)

elif page == "Custom Logic":
    st.title("Custom Logic")
    df = get_active_data().copy()

    st.write("Apply business logic with filters, KPIs, and notes.")

    if REQUIRED_KPI_COLUMNS.issubset(df.columns):
        df["profit"] = df["revenue"] - df["spend"]
        df["roi"] = (df["profit"] / df["spend"]).replace([np.inf, -np.inf], np.nan)

        min_roi = st.slider("Minimum ROI", min_value=-1.0, max_value=3.0, value=0.2, step=0.05)
        filtered = df[df["roi"].fillna(-999) >= min_roi]

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Spend", f"${filtered['spend'].sum():,.0f}")
        kpi2.metric("Total Revenue", f"${filtered['revenue'].sum():,.0f}")
        kpi3.metric("ROI", f"{filtered['roi'].mean():.2f}")

        st.subheader("Filtered results")
        st.dataframe(filtered.head(25), use_container_width=True)
    else:
        missing = REQUIRED_KPI_COLUMNS.difference(df.columns)
        st.warning(
            "To run the KPI logic, your data needs these columns: "
            f"{', '.join(sorted(missing))}."
        )

    st.subheader("Analyst notes")
    st.session_state.notes = st.text_area("Capture insights or assumptions", value=st.session_state.notes)
    if st.session_state.notes:
        st.info("Notes saved in the session. Reloading the page will reset them.")

else:
    st.title("About")
    st.write(
        "Streamlit is a fast way to build data apps in pure Python. "
        "This demo app keeps everything in a single file for easy learning."
    )
    st.subheader("Tips to get started")
    st.markdown(
        "- Start simple: run the app and edit labels, widgets, and charts.\n"
        "- Use `st.cache_data` for expensive data loading.\n"
        "- Keep state with `st.session_state`.\n"
        "- Use layout helpers like `st.columns` and `st.container`.\n"
        "- Add authentication or secrets in `.streamlit/secrets.toml`."
    )

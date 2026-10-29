import streamlit as st
import pandas as pd

def show_upload_and_explore():
    st.title("Upload Data and Explore It")

    uploaded_file = st.file_uploader(
        "Upload a CSV file",
        type=["csv"],
        help="Try any CSV with headers. Example: sales, transactions, stock prices, survey data, etc.",
    )

    if uploaded_file is None:
        st.warning("Upload a CSV to unlock the explorer.")
        st.markdown(
            """
            **Good starter CSV shapes:**
            - time series data with a date column
            - category + numeric columns
            - any small business or analytics dataset
            """
        )
        return

    df = pd.read_csv(uploaded_file)
    st.session_state["uploaded_df"] = df

    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", len(df))
    c2.metric("Columns", len(df.columns))
    c3.metric("Numeric Columns", df.select_dtypes(include="number").shape[1])

    st.subheader("Column types")
    dtypes_df = pd.DataFrame({
        "column": df.columns,
        "dtype": [str(x) for x in df.dtypes]
    })
    st.dataframe(dtypes_df, use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = df.columns.tolist()

    if len(numeric_cols) == 0:
        st.error("No numeric columns found. Upload a CSV with at least one numeric column for charts.")
        return

    st.subheader("Quick chart builder")
    chart_type = st.selectbox("Chart type", ["Line", "Bar", "Area", "Scatter"])
    x_col = st.selectbox("X-axis", all_cols, index=0)
    y_col = st.selectbox("Y-axis", numeric_cols, index=0)

    chart_df = df[[x_col, y_col]].copy()

    if chart_type == "Line":
        st.line_chart(chart_df, x=x_col, y=y_col)
    elif chart_type == "Bar":
        st.bar_chart(chart_df, x=x_col, y=y_col)
    elif chart_type == "Area":
        st.area_chart(chart_df, x=x_col, y=y_col)
    else:
        st.scatter_chart(chart_df, x=x_col, y=y_col)

    with st.expander("Summary statistics"):
        st.dataframe(df.describe(include="all").T, use_container_width=True)
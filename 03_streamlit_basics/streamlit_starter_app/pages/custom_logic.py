import streamlit as st
import pandas as pd

def show_custom_logic():
    st.title("Custom Logic Example")

    st.write(
        """
        This page shows where your own app logic goes.
        Instead of just displaying data, you can compute signals, scores, flags,
        decisions, recommendations, or automation-ready outputs.
        """
    )

    source = st.radio(
        "Choose a data source",
        ["Use uploaded CSV", "Use built-in example data"],
        horizontal=True,
    )

    if source == "Use uploaded CSV" and "uploaded_df" in st.session_state:
        df = st.session_state["uploaded_df"].copy()
    else:
        df = pd.DataFrame(
            {
                "item": ["A", "B", "C", "D", "E"],
                "value": [120, 85, 160, 70, 210],
                "cost": [75, 60, 100, 55, 130],
            }
        )

    st.dataframe(df, use_container_width=True)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        st.error("Your data needs numeric columns for this example.")
        return

    value_col = st.selectbox("Primary metric column", numeric_cols, index=0)
    threshold = st.slider("High-value threshold", 0.0, float(df[value_col].max()), float(df[value_col].mean()))

    result = df.copy()
    result["is_high_value"] = result[value_col] >= threshold

    if len(numeric_cols) >= 2:
        secondary = st.selectbox("Optional denominator / comparison column", ["None"] + numeric_cols, index=1)
        if secondary != "None":
            denom = result[secondary].replace(0, pd.NA)
            result["ratio"] = (result[value_col] / denom).round(2)

    st.subheader("Processed output")
    st.dataframe(result, use_container_width=True)

    high_count = int(result["is_high_value"].sum())
    st.metric("High-value rows", high_count)

    only_high = st.checkbox("Show only high-value rows")
    display_df = result[result["is_high_value"]] if only_high else result

    st.subheader("Filtered result")
    st.dataframe(display_df, use_container_width=True)

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download processed CSV",
        data=csv_bytes,
        file_name="processed_results.csv",
        mime="text/csv",
    )
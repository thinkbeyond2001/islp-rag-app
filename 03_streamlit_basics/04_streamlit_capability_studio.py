import io
import json
import math
import random
import time
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Streamlit Capability Studio",
    page_icon="🧰",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = [
    "Overview",
    "Widgets",
    "Data Lab",
    "Files",
    "Chat",
    "Status",
]


def init_session_state() -> None:
    if "data_mode" not in st.session_state:
        st.session_state.data_mode = "sample"
    if "working_df" not in st.session_state:
        st.session_state.working_df = None
    if "uploaded_name" not in st.session_state:
        st.session_state.uploaded_name = None
    if "notes" not in st.session_state:
        st.session_state.notes = []
    if "counter" not in st.session_state:
        st.session_state.counter = 0
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "Analyst",
            "role": "Marketing Lead",
            "goals": ["Build dashboard", "Explore data"],
            "confidence": 72,
            "budget": 2500,
            "launch_date": date.today() + timedelta(days=14),
            "standup_time": datetime.now().replace(second=0, microsecond=0).time(),
            "layout": "Wide",
            "accent": "#0f766e",
            "notes": "Use this app as a teaching template.",
            "alerts": True,
            "power_user": False,
        }
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": (
                    "I can explain the demo. Ask about widgets, caching, data uploads, "
                    "charts, session state, or status elements."
                ),
            }
        ]


def reset_demo_state() -> None:
    profile = {
        "name": "Analyst",
        "role": "Marketing Lead",
        "goals": ["Build dashboard", "Explore data"],
        "confidence": 72,
        "budget": 2500,
        "launch_date": date.today() + timedelta(days=14),
        "standup_time": datetime.now().replace(second=0, microsecond=0).time(),
        "layout": "Wide",
        "accent": "#0f766e",
        "notes": "Use this app as a teaching template.",
        "alerts": True,
        "power_user": False,
    }
    st.session_state.data_mode = "sample"
    st.session_state.working_df = None
    st.session_state.uploaded_name = None
    st.session_state.notes = []
    st.session_state.counter = 0
    st.session_state.profile = profile
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "The demo has been reset. Ask about widgets, caching, charts, "
                "uploads, or session state."
            ),
        }
    ]


def set_working_dataframe(df: pd.DataFrame, name: str) -> None:
    st.session_state.working_df = df.copy()
    st.session_state.data_mode = "custom"
    st.session_state.uploaded_name = name


@st.cache_data(show_spinner=False)
def build_demo_data(rows: int = 180, seed: int = 42) -> pd.DataFrame:
    rng = random.Random(seed)
    start_date = date.today() - timedelta(days=rows - 1)
    region_centers = {
        "New York": (40.7128, -74.0060),
        "Chicago": (41.8781, -87.6298),
        "Austin": (30.2672, -97.7431),
        "San Francisco": (37.7749, -122.4194),
    }
    channels = ["Search", "Email", "Social", "Partner", "Events"]
    segments = ["Starter", "Growth", "Enterprise"]
    records = []

    for idx in range(rows):
        current_date = start_date + timedelta(days=idx)
        region = rng.choice(list(region_centers))
        channel = rng.choice(channels)
        segment = rng.choice(segments)

        base_visits = 120 + idx * 0.45 + 18 * math.sin(idx / 9)
        visits = max(40, int(base_visits + rng.randint(0, 180)))
        signups = max(5, int(visits * (0.07 + rng.random() * 0.11)))
        customers = max(1, int(signups * (0.18 + rng.random() * 0.22)))
        avg_order_value = 95 + rng.randint(15, 180)
        revenue = round(customers * avg_order_value, 2)
        cost = round(visits * (0.6 + rng.random() * 0.9) + customers * (12 + rng.random() * 18), 2)
        margin = round(revenue - cost, 2)
        satisfaction = round(3.2 + rng.random() * 1.6, 2)
        lat, lon = region_centers[region]

        records.append(
            {
                "date": pd.to_datetime(current_date),
                "region": region,
                "channel": channel,
                "segment": segment,
                "visits": visits,
                "signups": signups,
                "customers": customers,
                "revenue": revenue,
                "cost": cost,
                "margin": margin,
                "conversion_rate": round(customers / visits, 4),
                "signup_rate": round(signups / visits, 4),
                "satisfaction": satisfaction,
                "lat": round(lat + rng.uniform(-0.35, 0.35), 5),
                "lon": round(lon + rng.uniform(-0.35, 0.35), 5),
            }
        )

    return pd.DataFrame(records)


@st.cache_data(show_spinner=False)
def parse_uploaded_file(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    lower_name = file_name.lower()
    if lower_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError("Please upload a CSV or Excel file.")

    df = df.copy()
    df.columns = [str(column).strip() for column in df.columns]

    for column in df.columns:
        lower_column = column.lower()
        if "date" in lower_column or "time" in lower_column:
            try:
                df[column] = pd.to_datetime(df[column])
            except (ValueError, TypeError):
                continue

    return df


@st.cache_data(show_spinner=False)
def dataframe_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def build_badge_svg(title: str, accent: str, subtitle: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; padding: 0.5rem;">
      <svg width="100%" height="170" viewBox="0 0 700 170" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="hero" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{accent}" stop-opacity="1" />
            <stop offset="100%" stop-color="#111827" stop-opacity="1" />
          </linearGradient>
        </defs>
        <rect width="700" height="170" rx="26" fill="url(#hero)" />
        <circle cx="84" cy="86" r="42" fill="white" fill-opacity="0.12" />
        <text x="84" y="95" text-anchor="middle" font-size="22" fill="white">st</text>
        <text x="160" y="74" font-size="34" fill="white" font-weight="700">{title}</text>
        <text x="160" y="108" font-size="18" fill="white" opacity="0.88">{subtitle}</text>
      </svg>
    </div>
    """


def current_data(sample_rows: int, sample_seed: int) -> pd.DataFrame:
    if st.session_state.data_mode == "custom" and st.session_state.working_df is not None:
        return st.session_state.working_df.copy()
    return build_demo_data(rows=sample_rows, seed=sample_seed)


def current_source_label(sample_rows: int, sample_seed: int) -> str:
    if st.session_state.data_mode == "custom" and st.session_state.uploaded_name:
        return st.session_state.uploaded_name
    return f"Sample dataset ({sample_rows} rows, seed {sample_seed})"


def make_summary_payload(df: pd.DataFrame, sample_rows: int, sample_seed: int) -> dict:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return {
        "current_source": current_source_label(sample_rows, sample_seed),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "numeric_columns": numeric_cols,
        "session_keys": sorted(list(st.session_state.keys())),
        "notes_saved": len(st.session_state.notes),
        "chat_messages": len(st.session_state.chat_history),
        "profile": st.session_state.profile,
    }


class DemoAssistant:
    def __init__(self) -> None:
        self.topic_map = {
            "cache": "Use `st.cache_data` for data loading and `st.cache_resource` for long-lived helpers.",
            "widget": "Widgets rerun the script top-to-bottom, which is why `st.session_state` matters.",
            "upload": "The Files page uses `st.file_uploader`, parses the file, and stores it as the active dataset.",
            "chart": "The Data Lab page combines filters, `st.data_editor`, tables, charts, and a map from one dataframe.",
            "state": "Session state keeps counters, notes, profile settings, chat history, and the current dataset alive across reruns.",
            "status": "The Status page demonstrates alerts, progress bars, spinners, exception blocks, and celebratory UI.",
        }

    def reply(self, prompt: str, df: pd.DataFrame, profile: dict) -> str:
        lower_prompt = prompt.lower()
        for keyword, answer in self.topic_map.items():
            if keyword in lower_prompt:
                return answer

        if "summary" in lower_prompt or "dataset" in lower_prompt:
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            preview = ", ".join(numeric_cols[:5]) if numeric_cols else "none"
            return (
                f"{profile['name']}, the active dataset has {df.shape[0]:,} rows and "
                f"{df.shape[1]} columns. Example numeric fields: {preview}."
            )

        return (
            "This app is a single-file teaching demo. Navigate with the sidebar, try the form, "
            "edit the dataset, upload a file, and then run the status workflow."
        )


@st.cache_resource(show_spinner=False)
def get_demo_assistant() -> DemoAssistant:
    return DemoAssistant()


def add_note() -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.notes.append(f"Manual note added at {timestamp}")


def clear_notes() -> None:
    st.session_state.notes = []


def send_demo_prompt(prompt: str, df: pd.DataFrame) -> None:
    assistant = get_demo_assistant()
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    response = assistant.reply(prompt, df, st.session_state.profile)
    st.session_state.chat_history.append({"role": "assistant", "content": response})


def safe_default_index(options: list[str], preferred: str) -> int:
    return options.index(preferred) if preferred in options else 0


def render_status_demo(df: pd.DataFrame) -> None:
    if hasattr(st, "status"):
        with st.status("Running demo workflow", expanded=True) as status:
            st.write("Inspecting the active dataset.")
            time.sleep(0.15)
            st.write(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]}")
            progress = st.progress(0, text="Preparing output")
            for pct in [15, 35, 60, 85, 100]:
                time.sleep(0.12)
                progress.progress(pct, text=f"Progress {pct}%")
            progress.empty()
            st.write("Status elements can narrate a multi-step process.")
            status.update(label="Workflow complete", state="complete")
    else:
        with st.spinner("Running demo workflow"):
            time.sleep(0.8)
        st.success("Workflow complete")

    if hasattr(st, "toast"):
        st.toast("Demo workflow finished")


init_session_state()

with st.sidebar:
    st.title("Capability Studio")
    page = st.radio("Go to", PAGES, index=0)
    st.divider()
    sample_rows = st.slider("Sample rows", min_value=90, max_value=365, value=180, step=15)
    sample_seed = st.number_input("Sample seed", min_value=0, max_value=9999, value=42, step=1)

    if st.button("Use sample dataset", use_container_width=True):
        st.session_state.data_mode = "sample"
        st.session_state.working_df = None
        st.session_state.uploaded_name = None

    if st.button("Reset session state", use_container_width=True):
        reset_demo_state()

active_df = current_data(sample_rows, sample_seed)
source_label = current_source_label(sample_rows, sample_seed)

with st.sidebar:
    st.caption(f"Current source: {source_label}")
    st.caption(f"Rows: {active_df.shape[0]:,} | Columns: {active_df.shape[1]}")


if page == "Overview":
    st.title("Streamlit Capability Studio")
    st.write(
        "One file that demonstrates most of what people reach for in Streamlit: "
        "layout, widgets, forms, state, caching, data editing, uploads, downloads, chat UI, and status elements."
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Pages", len(PAGES))
    metric_2.metric("Rows", f"{active_df.shape[0]:,}")
    metric_3.metric("Notes", len(st.session_state.notes))
    metric_4.metric("Messages", len(st.session_state.chat_history))

    tab_1, tab_2, tab_3 = st.tabs(["What It Covers", "Run It", "Session Snapshot"])

    with tab_1:
        left, right = st.columns([1.1, 1])
        with left:
            st.subheader("Included in the demo")
            st.markdown(
                """
                - Sidebar navigation and page configuration
                - Inputs: buttons, sliders, forms, text boxes, pickers, toggles, and selectors
                - Layout: columns, tabs, expanders, chat containers, and custom HTML components
                - Data tooling: dataframe, data editor, filtering, charts, map, and downloads
                - App behavior: session state, cache helpers, upload parsing, and status feedback
                """
            )
            st.dataframe(active_df.head(8), use_container_width=True, hide_index=True)

        with right:
            st.subheader("Minimal run command")
            st.code(
                "streamlit run 03_streamlit_basics/04_streamlit_capability_studio.py",
                language="bash",
            )
            with st.expander("Show the Streamlit rerun pattern"):
                with st.echo():
                    sample_total = active_df["revenue"].head(5).sum() if "revenue" in active_df else 0
                    st.write(f"Top 5 revenue total: ${sample_total:,.0f}")

    with tab_2:
        st.subheader("How to use the app")
        st.markdown(
            """
            1. Start on `Overview` to inspect the current sample dataset.
            2. Open `Widgets` to see forms, inputs, and session state.
            3. Move to `Data Lab` to filter, edit, chart, and map the data.
            4. Use `Files` to upload your own CSV or Excel file and download outputs.
            5. Finish with `Chat` and `Status` to see app state and status elements.
            """
        )

    with tab_3:
        st.json(make_summary_payload(active_df, sample_rows, sample_seed))

elif page == "Widgets":
    st.title("Widgets and Forms")
    st.write("This page shows common input widgets, form submission, callbacks, metrics, and live state.")

    widget_col, state_col = st.columns([1.15, 1])

    with widget_col:
        power_user_widget = st.toggle if hasattr(st, "toggle") else st.checkbox
        profile = st.session_state.profile

        with st.form("profile_form"):
            name = st.text_input("Name", value=profile["name"])
            role = st.selectbox(
                "Role",
                ["Marketing Lead", "Data Analyst", "Product Manager", "Founder"],
                index=safe_default_index(
                    ["Marketing Lead", "Data Analyst", "Product Manager", "Founder"],
                    profile["role"],
                ),
            )
            goals = st.multiselect(
                "Goals",
                ["Build dashboard", "Explore data", "Share app", "Track KPIs", "Prototype logic"],
                default=profile["goals"],
            )
            confidence = st.slider("Confidence", min_value=0, max_value=100, value=profile["confidence"])
            budget = st.number_input("Monthly budget", min_value=0, value=profile["budget"], step=250)
            launch_date = st.date_input("Launch date", value=profile["launch_date"])
            standup_time = st.time_input("Standup time", value=profile["standup_time"])
            layout = st.radio(
                "Preferred layout",
                ["Wide", "Centered"],
                index=safe_default_index(["Wide", "Centered"], profile["layout"]),
                horizontal=True,
            )
            accent = st.color_picker("Accent color", value=profile["accent"])
            notes = st.text_area("Analyst notes", value=profile["notes"], height=110)
            alerts = st.checkbox("Enable alerts", value=profile["alerts"])
            power_user = power_user_widget("Power user mode", value=profile["power_user"])
            submit_profile = st.form_submit_button("Save profile")

        if submit_profile:
            st.session_state.profile = {
                "name": name,
                "role": role,
                "goals": goals,
                "confidence": confidence,
                "budget": budget,
                "launch_date": launch_date,
                "standup_time": standup_time,
                "layout": layout,
                "accent": accent,
                "notes": notes,
                "alerts": alerts,
                "power_user": power_user,
            }
            st.success("Profile saved to session state.")

        action_1, action_2, action_3 = st.columns(3)
        action_1.button("Increment counter", on_click=lambda: st.session_state.__setitem__("counter", st.session_state.counter + 1))
        action_2.button("Add note", on_click=add_note)
        action_3.button("Clear notes", on_click=clear_notes)

        st.metric("Counter", st.session_state.counter, delta="Callbacks in action")

    with state_col:
        st.subheader("Live session state")
        st.json(st.session_state.profile)

        badge_html = build_badge_svg(
            st.session_state.profile["name"],
            st.session_state.profile["accent"],
            f"{st.session_state.profile['role']} | {source_label}",
        )
        components.html(badge_html, height=190)

        with st.expander("Saved notes"):
            if st.session_state.notes:
                for item in st.session_state.notes:
                    st.write(f"- {item}")
            else:
                st.caption("No notes saved yet.")

elif page == "Data Lab":
    st.title("Data Lab")
    st.write("This page demonstrates tables, data editing, filters, charts, statistics, geospatial display, and downloads.")

    working_df = active_df.copy()
    numeric_cols = working_df.select_dtypes(include="number").columns.tolist()
    category_cols = working_df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = working_df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

    control_1, control_2, control_3, control_4 = st.columns(4)
    filter_col = control_1.selectbox("Categorical filter", ["None"] + category_cols)
    selected_values = []
    if filter_col != "None":
        filter_options = sorted(working_df[filter_col].dropna().astype(str).unique().tolist())
        selected_values = control_2.multiselect("Keep values", filter_options)
    else:
        control_2.caption("Select a categorical filter to enable values.")

    range_col = None
    range_values = None
    if numeric_cols:
        preferred_metric = "revenue" if "revenue" in numeric_cols else numeric_cols[0]
        range_col = control_3.selectbox("Range filter", numeric_cols, index=safe_default_index(numeric_cols, preferred_metric))
        min_value = float(working_df[range_col].min())
        max_value = float(working_df[range_col].max())
        if min_value < max_value:
            range_values = control_4.slider(
                "Keep values between",
                min_value=min_value,
                max_value=max_value,
                value=(min_value, max_value),
            )
    else:
        control_3.caption("No numeric columns found.")
        control_4.caption("Numeric range filters are unavailable.")

    filtered_df = working_df.copy()
    if filter_col != "None" and selected_values:
        filtered_df = filtered_df[filtered_df[filter_col].astype(str).isin(selected_values)]
    if range_col and range_values:
        filtered_df = filtered_df[filtered_df[range_col].between(range_values[0], range_values[1])]
    if "margin" in filtered_df.columns and st.checkbox("Show only profitable rows", value=False):
        filtered_df = filtered_df[filtered_df["margin"] > 0]

    preview_tab, edit_tab, chart_tab, map_tab = st.tabs(["Preview", "Edit", "Charts", "Map"])

    with preview_tab:
        stats_1, stats_2, stats_3, stats_4 = st.columns(4)
        stats_1.metric("Filtered rows", f"{filtered_df.shape[0]:,}")
        if "revenue" in filtered_df.columns:
            stats_2.metric("Revenue", f"${filtered_df['revenue'].sum():,.0f}")
        if "cost" in filtered_df.columns:
            stats_3.metric("Cost", f"${filtered_df['cost'].sum():,.0f}")
        if "margin" in filtered_df.columns:
            stats_4.metric("Margin", f"${filtered_df['margin'].sum():,.0f}")

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        if numeric_cols:
            st.subheader("Quick numeric summary")
            summary_table = filtered_df[numeric_cols].agg(["mean", "median", "max"]).T.round(2)
            st.table(summary_table.head(8))

        with st.expander("Data schema"):
            schema_payload = {
                "columns": {column: str(dtype) for column, dtype in filtered_df.dtypes.items()},
                "rows": int(filtered_df.shape[0]),
            }
            st.json(schema_payload)

        st.download_button(
            "Download filtered CSV",
            data=dataframe_to_csv(filtered_df),
            file_name="filtered_streamlit_demo_data.csv",
            mime="text/csv",
        )

    with edit_tab:
        st.caption("`st.data_editor` returns a dataframe, so you can feed edits directly back into your app.")
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
        )
        edit_left, edit_right = st.columns([1, 1])
        if edit_left.button("Use edited data in app"):
            set_working_dataframe(edited_df, "Edited dataset")
            if hasattr(st, "rerun"):
                st.rerun()
        edit_right.download_button(
            "Download edited CSV",
            data=dataframe_to_csv(edited_df),
            file_name="edited_streamlit_demo_data.csv",
            mime="text/csv",
        )

    with chart_tab:
        if not numeric_cols:
            st.warning("Upload or generate a dataset with numeric columns to show charts.")
        else:
            chart_controls = st.columns(4)
            metric_col = chart_controls[0].selectbox(
                "Metric",
                numeric_cols,
                index=safe_default_index(numeric_cols, "revenue" if "revenue" in numeric_cols else numeric_cols[0]),
            )
            aggregation = chart_controls[1].selectbox("Aggregation", ["sum", "mean", "median", "max"])
            group_col = chart_controls[2].selectbox("Group by", ["None"] + category_cols)
            time_col = chart_controls[3].selectbox("Time axis", ["None"] + date_cols)

            trend_placeholder = st.container()
            if time_col != "None":
                trend_df = filtered_df.groupby(time_col)[metric_col].agg(aggregation).sort_index()
                trend_placeholder.subheader("Trend")
                trend_placeholder.line_chart(trend_df, use_container_width=True)

            if group_col != "None":
                grouped_df = filtered_df.groupby(group_col)[metric_col].agg(aggregation).sort_values(ascending=False)
                st.subheader("Category comparison")
                st.bar_chart(grouped_df, use_container_width=True)

            if len(numeric_cols) >= 2:
                scatter_left, scatter_right = st.columns(2)
                x_metric = scatter_left.selectbox("Scatter X", numeric_cols, index=0)
                y_metric = scatter_right.selectbox(
                    "Scatter Y",
                    numeric_cols,
                    index=1 if len(numeric_cols) > 1 else 0,
                )
                scatter_df = filtered_df[[x_metric, y_metric]].dropna()
                if not scatter_df.empty:
                    st.subheader("Scatter view")
                    st.scatter_chart(scatter_df, x=x_metric, y=y_metric, use_container_width=True)

    with map_tab:
        if {"lat", "lon"}.issubset(filtered_df.columns):
            st.map(filtered_df[["lat", "lon"]].dropna(), use_container_width=True)
            st.caption("`st.map` expects latitude and longitude columns.")
        else:
            fallback_map = build_demo_data(rows=sample_rows, seed=sample_seed)
            st.info("The active dataset does not include `lat`/`lon`, so the sample geospatial dataset is shown instead.")
            st.map(fallback_map[["lat", "lon"]], use_container_width=True)

elif page == "Files":
    st.title("Files, Downloads, and Custom Components")
    st.write("Use this page to upload data, export app outputs, and render a small HTML component inside Streamlit.")

    file_tab, export_tab, component_tab = st.tabs(["Upload", "Downloads", "Component"])

    with file_tab:
        with st.form("upload_form"):
            uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
            load_file = st.form_submit_button("Load file into app")

        if load_file:
            if uploaded_file is None:
                st.warning("Choose a file before loading.")
            else:
                try:
                    parsed_df = parse_uploaded_file(uploaded_file.name, uploaded_file.getvalue())
                    set_working_dataframe(parsed_df, uploaded_file.name)
                    st.success(f"Loaded `{uploaded_file.name}` with {parsed_df.shape[0]:,} rows.")
                    if hasattr(st, "rerun"):
                        st.rerun()
                except Exception as error:
                    st.error(f"Upload failed: {error}")

        st.info(f"Current source: {source_label}")
        st.dataframe(active_df.head(15), use_container_width=True, hide_index=True)

    with export_tab:
        sample_df = build_demo_data(rows=sample_rows, seed=sample_seed)
        summary_json = json.dumps(make_summary_payload(active_df, sample_rows, sample_seed), indent=2, default=str)

        export_left, export_right = st.columns(2)
        export_left.download_button(
            "Download sample CSV",
            data=dataframe_to_csv(sample_df),
            file_name="streamlit_demo_template.csv",
            mime="text/csv",
        )
        export_right.download_button(
            "Download app state JSON",
            data=summary_json,
            file_name="streamlit_demo_state.json",
            mime="application/json",
        )

        with st.expander("State JSON preview"):
            st.code(summary_json, language="json")

    with component_tab:
        component_title = st.text_input("Badge title", value=st.session_state.profile["name"])
        component_subtitle = st.text_input("Badge subtitle", value=source_label)
        badge_svg = build_badge_svg(
            component_title,
            st.session_state.profile["accent"],
            component_subtitle,
        )
        components.html(badge_svg, height=190)
        st.download_button(
            "Download badge SVG",
            data=badge_svg,
            file_name="streamlit_demo_badge.html",
            mime="text/html",
        )
        with st.expander("Rendered component markup"):
            st.code(badge_svg, language="html")

elif page == "Chat":
    st.title("Chat UI and Session State")
    st.write("This is a rule-based assistant cached with `st.cache_resource`, wired into `st.chat_message` and `st.chat_input`.")

    chat_action_1, chat_action_2, chat_action_3 = st.columns(3)
    if chat_action_1.button("Summarize dataset"):
        send_demo_prompt("Give me a dataset summary.", active_df)
        if hasattr(st, "rerun"):
            st.rerun()
    if chat_action_2.button("Explain session state"):
        send_demo_prompt("How does session state work?", active_df)
        if hasattr(st, "rerun"):
            st.rerun()
    if chat_action_3.button("Clear chat"):
        st.session_state.chat_history = st.session_state.chat_history[:1]
        if hasattr(st, "rerun"):
            st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask about widgets, uploads, caching, charts, status, or the active dataset")
    if prompt:
        send_demo_prompt(prompt, active_df)
        if hasattr(st, "rerun"):
            st.rerun()

    st.caption(f"Messages in session: {len(st.session_state.chat_history)}")

elif page == "Status":
    st.title("Status Elements")
    st.write("This page demonstrates alerts, progress indicators, spinners, exception blocks, and celebratory actions.")

    alert_col, workflow_col = st.columns([0.9, 1.1])

    with alert_col:
        st.info("Use info boxes for helpful context.")
        st.warning("Warnings are useful when data is missing or assumptions are weak.")
        st.error("Errors should explain what failed and what the user can do next.")
        if st.button("Celebrate with balloons"):
            st.balloons()

    with workflow_col:
        if st.button("Run staged workflow"):
            render_status_demo(active_df)
        placeholder = st.empty()
        placeholder.metric("Current time", datetime.now().strftime("%H:%M:%S"))

        with st.expander("Show an exception block"):
            try:
                raise ValueError("Example exception to demonstrate `st.exception`.")
            except ValueError as error:
                st.exception(error)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="U.S. State Highlighter",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)


US_STATES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def make_state_dataframe(selected_states: list[str]) -> pd.DataFrame:
    """Return one row per state with the fields needed by the map."""
    selected = set(selected_states)
    return pd.DataFrame(
        {
            "state": list(US_STATES),
            "abbreviation": list(US_STATES.values()),
            "is_selected": [int(state in selected) for state in US_STATES],
            "status": [
                "Highlighted" if state in selected else "Not selected"
                for state in US_STATES
            ],
        }
    )


def make_us_map(
    state_data: pd.DataFrame,
    highlight_color: str,
    unselected_color: str,
) -> go.Figure:
    """Build a two-color U.S. choropleth from the state selection data."""
    colorscale = [
        [0.0, unselected_color],
        [0.4999, unselected_color],
        [0.5, highlight_color],
        [1.0, highlight_color],
    ]

    figure = go.Figure(
        go.Choropleth(
            locations=state_data["abbreviation"],
            locationmode="USA-states",
            z=state_data["is_selected"],
            zmin=0,
            zmax=1,
            text=state_data["state"],
            customdata=state_data[["status", "abbreviation"]],
            colorscale=colorscale,
            showscale=False,
            marker_line_color="#ffffff",
            marker_line_width=1.2,
            hovertemplate=(
                "<b>%{text} (%{customdata[1]})</b><br>"
                "%{customdata[0]}<extra></extra>"
            ),
        )
    )

    figure.update_geos(
        scope="usa",
        projection_type="albers usa",
        bgcolor="rgba(0,0,0,0)",
        showlakes=True,
        lakecolor="#dbeafe",
    )
    figure.update_layout(
        height=610,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        uirevision="state-highlighter",
    )
    return figure


st.markdown(
    """
    <style>
        .block-container {padding-top: 2.5rem; padding-bottom: 2rem;}
        [data-testid="stMetric"] {
            background: rgba(148, 163, 184, 0.10);
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 0.8rem;
            padding: 0.85rem 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "map_selected_states" not in st.session_state:
    st.session_state.map_selected_states = ["California", "New York", "Texas"]


with st.sidebar:
    st.header("Map controls")
    st.caption("Choose one or more states. The map updates automatically.")

    button_col_1, button_col_2 = st.columns(2)
    if button_col_1.button("Select all", use_container_width=True):
        st.session_state.map_selected_states = list(US_STATES)
    if button_col_2.button("Clear", use_container_width=True):
        st.session_state.map_selected_states = []

    selected_states = st.multiselect(
        "States to highlight",
        options=list(US_STATES),
        key="map_selected_states",
        placeholder="Select one or more states",
    )

    st.divider()
    st.subheader("Colors")
    highlight_color = st.color_picker("Highlighted states", "#2563EB")
    unselected_color = st.color_picker("Other states", "#CBD5E1")


st.title("🗺️ U.S. State Highlighter")
st.write(
    "Select states from the sidebar to highlight them on the map. "
    "Hover over any state to see its name, abbreviation, and selection status."
)

state_data = make_state_dataframe(selected_states)

metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
metric_col_1.metric("States highlighted", len(selected_states))
metric_col_2.metric("States not selected", len(US_STATES) - len(selected_states))
metric_col_3.metric("Coverage", f"{len(selected_states) / len(US_STATES):.0%}")

st.plotly_chart(
    make_us_map(state_data, highlight_color, unselected_color),
    use_container_width=True,
    config={"displayModeBar": False, "responsive": True},
)

if selected_states:
    selected_labels = [f"{state} ({US_STATES[state]})" for state in selected_states]
    st.success("Highlighted: " + ", ".join(selected_labels))
else:
    st.info("No states are highlighted. Choose states from the sidebar to begin.")

with st.expander("View state selection data"):
    st.dataframe(
        state_data.rename(
            columns={
                "state": "State",
                "abbreviation": "Abbreviation",
                "status": "Status",
            }
        )[["State", "Abbreviation", "Status"]],
        hide_index=True,
        use_container_width=True,
    )

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.loader import open_excel

MAPS_FILE = "Maps.xlsx"
MAPS_SHEET = "Map List"

RESOURCE_COLUMNS = [
    "Boar Food",
    "Deer Food",
    "Berry Food",
    "Total Food",
    "Large Gold Sum",
    "Small Gold Sum",
    "Total Gold",
    "Large Stone Sum",
    "Small Stone Sum",
    "Total Stone"
]

CATEGORY_COLUMNS = {
    "All": RESOURCE_COLUMNS,
    "Food": ["Boar Food", "Deer Food", "Berry Food", "Total Food"],
    "Gold": ["Large Gold Sum", "Small Gold Sum", "Total Gold"],
    "Stone": ["Large Stone Sum", "Small Stone Sum", "Total Stone"],
}

def load_data() -> pd.DataFrame:
    return open_excel(MAPS_FILE, MAPS_SHEET, "Name")


def render_sidebar(maps_frame) -> tuple[str, str]:
    maps = st.sidebar.selectbox("Select a map", maps_frame["Name"].tolist())
    category = st.sidebar.selectbox("Select a resource", list(CATEGORY_COLUMNS.keys()))

    return str(maps), str(category)


def render_comparison_chart(maps_frame, selected_map, selected_category):

    columns_to_show = CATEGORY_COLUMNS[selected_category]

    row = maps_frame[maps_frame["Name"] == selected_map].iloc[0]
    median = maps_frame.median(numeric_only=True)

    fig = go.Figure([
        go.Bar(name=selected_map, x=columns_to_show, y=row[columns_to_show]),
        go.Bar(name="Median",     x=columns_to_show, y=median[columns_to_show]),
    ])

    fig.update_layout(barmode="group", title="Resource comparison vs. median")
    st.plotly_chart(fig, use_container_width=True)


def render_rankings_table(maps_frame, selected_map, selected_category):

    if selected_category == "All":
        st.info("Select a specific resource to see rankings.")
        return

    total_columns_mapping = {
        "Food": "Total Food",
        "Gold": "Total Gold",
        "Stone": "Total Stone",
    }

    total_col = total_columns_mapping[selected_category]
    median_val = maps_frame[total_col].median()

    df = maps_frame[["Name", total_col]].copy()
    df["Median"] = int(median_val)
    df["Flat diff from Median"] = (df[total_col] - median_val).astype(int)
    df["% diff from Median"] = ((df[total_col] - median_val) / median_val * 100).astype(int)
    df = df.sort_values(total_col, ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", range(1, len(df) + 1))

    selected_row = df[df["Name"] == selected_map]
    full_format = {total_col: "{:,}", "Median": "{:,}", "Flat diff from Median": "{:,}"}
    rank_col_config = {"Rank": st.column_config.NumberColumn(width="small")}

    def highlight_row(row):
        if row["Name"] == selected_map:
            return ["background-color: #6C3483; color: white"] * len(row)
        return [""] * len(row)

    st.markdown("**Selected map**")

    st.dataframe(
        selected_row.style
        .apply(lambda x: ["background-color: #6C3483; color: white"] * len(x), axis=1)
        .format(full_format),
        use_container_width=True,
        hide_index=True,
        column_config=rank_col_config,
    )

    st.markdown("**All maps**")

    st.dataframe(
        df.style.apply(highlight_row, axis=1).format(full_format),
        use_container_width=True,
        hide_index=True,
        column_config=rank_col_config,
    )


def render_map_info(maps_frame, selected_map):

    """Style
    Topographically Defensible Spawn

    Sacred Sites (+ median)
    Trade Posts (+ median)
    Relics (+ median)

    Water
    Shoreline Fish
    Deep Water Fish

    """

    current_map_row = maps_frame[maps_frame["Name"] == selected_map].iloc[0]
    map_type = current_map_row["Style"]
    median = maps_frame.median(numeric_only=True)

    sacred_sites = current_map_row["Sacred Sites"]
    ss_median = median["Sacred Sites"]

    relics = current_map_row["Relics"]
    r_median = median["Relics"]

    trade_posts = current_map_row["Trade Posts"]
    tp_median = median["Trade Posts"]

    tds = "Yes" if current_map_row["Topographically Defensible Spawn"] else "No"
    water_line = "<p style='margin: 4px 0;'>Water: Yes</p>" if current_map_row["Water"] else ""
    shoreline_line = "<p style='margin: 4px 0;'>Shoreline Fish: Yes</p>" if current_map_row["Shoreline Fish"] else ""
    deep_water_line = "<p style='margin: 4px 0;'>Deep Water Fish: Yes</p>" if current_map_row["Deep Water Fish"] else ""

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
        <div style="padding: 12px 16px; background-color: #14141A; border: 1px solid #3A3A4A; border-radius: 8px;">
            <p style="margin: 4px 0;">Map Archetype: {map_type}</p>
            <p style="margin: 4px 0;">Sacred Sites: {sacred_sites} (μ = {ss_median})</p>
            <p style="margin: 4px 0;">Relics: {relics} (μ = {r_median})</p>
            <p style="margin: 4px 0;">Trade Posts: {trade_posts} (μ = {tp_median})</p>
            <p style="margin: 4px 0;">Topographically Defensible Spawn: {tds}</p>
            {water_line}
            {shoreline_line}
            {deep_water_line}
        </div>
    """, unsafe_allow_html=True)


def render_map_description(maps_frame, selected_map):

    current_map_row = maps_frame[maps_frame["Name"] == selected_map].iloc[0]
    current_map_description = current_map_row["Comments"]

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
            <div style="padding: 12px 16px; background-color: #14141A; border: 1px solid #3A3A4A; border-radius: 8px;">
                <p style="margin: 4px 0;">Description: {current_map_description}</p>
            </div>
        """, unsafe_allow_html=True)


def main():

    st.set_page_config(layout="wide")

    maps_frame = load_data()
    selected_map, selected_category = render_sidebar(maps_frame)
    render_comparison_chart(maps_frame, selected_map, selected_category)
    render_rankings_table(maps_frame, selected_map, selected_category)
    render_map_info(maps_frame, selected_map)
    render_map_description(maps_frame, selected_map)

    # streamlit run map_dashboard.py


if __name__ == "__main__":
    main()

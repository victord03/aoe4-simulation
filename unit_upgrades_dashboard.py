import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.loader import open_excel


UNITS_FILE = "2026-05-22_AoeIV-Excel-Data-Masterfile.xlsx"
UNIT_UPGRADES_SHEET = "Unit Upgrades"

VETERAN_PCT_COLS = ["Veteran HP % increase", "Veteran Damage % increase"]
ELITE_PCT_COLS = ["Elite HP % increase",   "Elite Damage % increase"]
PCT_LABELS = ["HP %", "Damage %"]

VETERAN_FLAT_COLS = ["Veteran Melee Armor increase", "Veteran Ranged Armor increase"]
ELITE_FLAT_COLS = ["Elite Melee Armor increase",   "Elite Ranged Armor increase"]
FLAT_LABELS = ["Melee Armor", "Ranged Armor"]


def load_data() -> pd.DataFrame:
    """Load the Unit Upgrades sheet and return it as a DataFrame keyed by unit name."""
    return open_excel(UNITS_FILE, UNIT_UPGRADES_SHEET, "Unit")


def render_sidebar(units_frame: pd.DataFrame) -> str:
    """Render the unit selector in the sidebar and return the selected unit name."""
    units = st.sidebar.selectbox("Select a unit", units_frame["Unit"].tolist())
    return str(units)


def render_histogram(units_frame: pd.DataFrame, selected_unit: str) -> None:
    """Render two side-by-side grouped bar charts for the selected unit.

    Left chart: HP % and Damage % increase per tier (Veteran / Elite) vs median.
    Right chart: flat Melee and Ranged Armor increase per tier vs median, or a
    placeholder message when all armor values are zero.
    """
    current_unit_row = units_frame[units_frame["Unit"] == selected_unit].iloc[0]

    veteran = pd.notna(current_unit_row["Veteran HP % increase"])
    elite = pd.notna(current_unit_row["Elite HP % increase"])
    median = units_frame.median(numeric_only=True)

    if not veteran and not elite:
        st.info("This unit gets no regular tier upgrades.")
        return

    bars_pct: list[go.Bar] = []
    bars_flat: list[go.Bar] = []
    all_pct_vals: list[float] = []
    all_flat_vals: list[float] = []

    if veteran:
        vet_pct_y = current_unit_row[VETERAN_PCT_COLS].values * 100
        vet_flat_y = current_unit_row[VETERAN_FLAT_COLS].values
        all_pct_vals.extend(vet_pct_y)
        all_flat_vals.extend(vet_flat_y)
        bars_pct.append(go.Bar(
            name="Veteran", x=PCT_LABELS, y=vet_pct_y,
            text=[f"{v:.1f}%" if pd.notna(v) and v != 0 else "" for v in vet_pct_y],
            textposition="outside",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        ))
        bars_flat.append(go.Bar(
            name="Veteran", x=FLAT_LABELS, y=vet_flat_y,
            text=[f"{v:.0f}" if pd.notna(v) and v != 0 else "" for v in vet_flat_y],
            textposition="outside",
            hovertemplate="%{x}: %{y:.0f}<extra></extra>",
        ))

    if elite:
        elite_pct_y = current_unit_row[ELITE_PCT_COLS].values * 100
        elite_flat_y = current_unit_row[ELITE_FLAT_COLS].values
        all_pct_vals.extend(elite_pct_y)
        all_flat_vals.extend(elite_flat_y)
        bars_pct.append(go.Bar(
            name="Elite", x=PCT_LABELS, y=elite_pct_y,
            text=[f"{v:.1f}%" if pd.notna(v) and v != 0 else "" for v in elite_pct_y],
            textposition="outside",
            hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
        ))
        bars_flat.append(go.Bar(
            name="Elite", x=FLAT_LABELS, y=elite_flat_y,
            text=[f"{v:.0f}" if pd.notna(v) and v != 0 else "" for v in elite_flat_y],
            textposition="outside",
            hovertemplate="%{x}: %{y:.0f}<extra></extra>",
        ))

    bars_pct.append(go.Bar(
        name="Median (Veteran)", x=PCT_LABELS, y=median[VETERAN_PCT_COLS].values * 100
    ))
    bars_pct.append(go.Bar(
        name="Median (Elite)", x=PCT_LABELS, y=median[ELITE_PCT_COLS].values * 100
    ))

    bars_flat.append(go.Bar(
        name="Median (Veteran)", x=FLAT_LABELS, y=median[VETERAN_FLAT_COLS].values
    ))
    bars_flat.append(go.Bar(
        name="Median (Elite)", x=FLAT_LABELS, y=median[ELITE_FLAT_COLS].values
    ))

    max_pct = pd.Series(all_pct_vals).dropna().max()
    max_flat = pd.Series(all_flat_vals).dropna().max()
    no_armor = max_flat == 0 or pd.isna(max_flat)

    fig = go.Figure(bars_pct)
    fig.update_layout(barmode="group", title="Unit tier upgrade stat increase comparison (% to previous)", yaxis=dict(range=[0, max_pct * 1.2]))

    if no_armor:
        fig2 = go.Figure()
        fig2.add_annotation(
            text="No armor increase via unit tier upgrades",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14),
        )
        fig2.update_layout(
            title="Armor upgrades (flat)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
    else:
        fig2 = go.Figure(bars_flat)
        fig2.update_layout(barmode="group", title="Unit tier upgrade stat increase comparison (flat to previous)", yaxis=dict(range=[0, max_flat * 1.2]))

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)


def _normalize_col(units_frame: pd.DataFrame, row: pd.Series, col: str) -> float:
    """Return a value normalized 0–100 relative to the column maximum across all units."""
    val = row[col]
    col_max = units_frame[col].max()
    if pd.isna(val) or col_max == 0:
        return 0.0
    return float(val / col_max * 100)


def _get_radar_values(units_frame: pd.DataFrame, row: pd.Series, pct_cols: list[str], flat_cols: list[str]) -> list[float]:
    """Return normalized radar values for one tier across all four stat axes."""
    return [_normalize_col(units_frame, row, col) for col in pct_cols + flat_cols]


def _build_radar_trace(name: str, values: list[float]) -> go.Scatterpolar:
    """Build a single filled radar polygon trace for one upgrade tier."""
    return go.Scatterpolar(
        name=name,
        r=values,
        theta=PCT_LABELS + FLAT_LABELS,
        fill="toself",
    )


def render_radar_chart(units_frame: pd.DataFrame, selected_unit: str) -> None:
    """Render a radar chart showing the normalized upgrade stat profile for the selected unit.

    Each axis (HP %, Damage %, Melee Armor, Ranged Armor) is normalized 0–100
    relative to the maximum value for that stat across all units. One polygon
    per available tier (Veteran / Elite).
    """
    row = units_frame[units_frame["Unit"] == selected_unit].iloc[0]
    veteran = pd.notna(row["Veteran HP % increase"])
    elite = pd.notna(row["Elite HP % increase"])

    if not veteran and not elite:
        return

    traces = []
    if veteran:
        traces.append(_build_radar_trace("Veteran", _get_radar_values(units_frame, row, VETERAN_PCT_COLS, VETERAN_FLAT_COLS)))
    if elite:
        traces.append(_build_radar_trace("Elite", _get_radar_values(units_frame, row, ELITE_PCT_COLS, ELITE_FLAT_COLS)))

    fig = go.Figure(traces)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Upgrade stat profile (normalized per stat across all units)",
    )
    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    """Entry point — configures the page and orchestrates all render calls."""
    st.set_page_config(layout="wide")

    units_frame = load_data()
    selected_unit = render_sidebar(units_frame)
    render_histogram(units_frame, selected_unit)
    render_radar_chart(units_frame, selected_unit)


if __name__ == "__main__":
    main()

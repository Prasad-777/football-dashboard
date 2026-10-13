"""
Football Player Performance Analytics Dashboard
================================================
DISCLAIMER: All player and team data in this application is SYNTHETIC.
It was generated programmatically for demonstration purposes only.
It does NOT represent real football players, clubs, or match results.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season",
    "age", "matches_played", "minutes_played",
    "goals", "assists", "shots", "shots_on_target", "key_passes",
    "dribbles", "tackles", "yellow_cards", "red_cards",
    "clean_sheets", "saves", "rating",
]

POSITIONS = ["GK", "DEF", "MID", "FWD"]

SEASONS = ["2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]

TEAMS = [
    "Ironclad FC", "Blue Wave SC", "Red Storm United", "Golden Eagles CF",
    "Silver Fox Athletic", "Thunder Valley FC", "Coastline City SC",
    "Mountain Peak United", "Riverside Rovers", "Northgate City FC",
]

PLOT_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3", family="Segoe UI, sans-serif", size=13),
    title_font=dict(color="#58a6ff", size=16),
    legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=["#3fb950", "#58a6ff", "#f78166", "#d2a8ff",
               "#ffa657", "#79c0ff", "#56d364", "#ff7b72"],
)

CSV_PATH = "football_players.csv"

# ---------------------------------------------------------------------------
# SUB-TASK 1 — GENERATE SYNTHETIC DATASET
# ---------------------------------------------------------------------------

def generate_dataset() -> None:
    """
    Create a reproducible synthetic football player dataset and save it to
    football_players.csv.  All values are randomly generated — not real data.
    """
    rng = np.random.default_rng(42)

    rows = []
    player_id = 1

    # Distribution of players per position per team per season
    pos_counts = {"GK": 3, "DEF": 8, "MID": 8, "FWD": 6}

    for season in SEASONS:
        for team in TEAMS:
            for position, count in pos_counts.items():
                for _ in range(count):
                    age = int(rng.integers(18, 38))
                    matches = int(rng.integers(5, 38))
                    minutes = int(matches * rng.integers(60, 95))

                    # Position-weighted stats
                    if position == "GK":
                        goals     = int(rng.integers(0, 1))
                        assists   = int(rng.integers(0, 2))
                        shots     = int(rng.integers(0, 3))
                        tackles   = int(rng.integers(5, 20))
                        dribbles  = int(rng.integers(0, 5))
                        clean_sh  = int(rng.integers(0, matches // 2 + 1))
                        saves     = int(rng.integers(20, 120))
                    elif position == "DEF":
                        goals     = int(rng.integers(0, 6))
                        assists   = int(rng.integers(0, 8))
                        shots     = goals + int(rng.integers(0, 10))
                        tackles   = int(rng.integers(20, 80))
                        dribbles  = int(rng.integers(5, 40))
                        clean_sh  = 0
                        saves     = 0
                    elif position == "MID":
                        goals     = int(rng.integers(0, 14))
                        assists   = int(rng.integers(2, 18))
                        shots     = goals + int(rng.integers(2, 20))
                        tackles   = int(rng.integers(10, 60))
                        dribbles  = int(rng.integers(10, 70))
                        clean_sh  = 0
                        saves     = 0
                    else:  # FWD
                        goals     = int(rng.integers(0, 30))
                        assists   = int(rng.integers(0, 14))
                        shots     = goals + int(rng.integers(2, 30))
                        tackles   = int(rng.integers(2, 25))
                        dribbles  = int(rng.integers(10, 80))
                        clean_sh  = 0
                        saves     = 0

                    shots_on_target = int(min(shots, max(0, goals + int(rng.integers(0, max(1, shots - goals + 1))))))
                    key_passes      = assists + int(rng.integers(0, 10))
                    yellow_cards    = int(rng.integers(0, 10))
                    red_cards       = int(rng.integers(0, 3))

                    # Synthetic rating: weighted composite (5.0 – 9.5)
                    raw = (
                        goals   * 0.30 +
                        assists * 0.20 +
                        (shots_on_target / max(shots, 1)) * 10 * 0.15 +
                        tackles * 0.005 +
                        saves   * 0.002 +
                        clean_sh * 0.10 -
                        yellow_cards * 0.05 -
                        red_cards    * 0.15
                    )
                    rating = round(float(np.clip(raw / 3 + 5.5 + rng.uniform(-0.5, 0.5), 5.0, 9.5)), 2)

                    # Synthetic name: FirstName_PlayerID
                    first_names = ["James", "Carlos", "Luca", "Ahmed", "Yuki",
                                   "Kwame", "Ivan", "Pedro", "Oluwaseun", "Henri",
                                   "Marco", "David", "Emil", "Seun", "Takeshi",
                                   "Rui", "Matteo", "Jorge", "Kenji", "Ade"]
                    last_names  = ["Silva", "Mueller", "Rossi", "Johnson", "Park",
                                   "Mensah", "Petrov", "Santos", "Okafor", "Dubois",
                                   "Costa", "Kim", "Andersen", "Walker", "Nakamura",
                                   "Ferreira", "Bianchi", "Martinez", "Tanaka", "Osei"]
                    fname = first_names[player_id % len(first_names)]
                    lname = last_names[(player_id * 7) % len(last_names)]
                    name  = f"{fname} {lname}"

                    rows.append({
                        "player_id":       player_id,
                        "player_name":     name,
                        "team":            team,
                        "position":        position,
                        "season":          season,
                        "age":             age,
                        "matches_played":  matches,
                        "minutes_played":  minutes,
                        "goals":           goals,
                        "assists":         assists,
                        "shots":           shots,
                        "shots_on_target": shots_on_target,
                        "key_passes":      key_passes,
                        "dribbles":        dribbles,
                        "tackles":         tackles,
                        "yellow_cards":    yellow_cards,
                        "red_cards":       red_cards,
                        "clean_sheets":    clean_sh,
                        "saves":           saves,
                        "rating":          rating,
                    })
                    player_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(CSV_PATH, index=False)
    print("[OK] Synthetic dataset generated - NOT real player data.")


# ---------------------------------------------------------------------------
# SUB-TASK 2 — DATA LOADING AND VALIDATION
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load football_players.csv, validate schema, coerce types, fill NaNs."""
    if not os.path.exists(CSV_PATH):
        generate_dataset()

    df = pd.read_csv(CSV_PATH)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"❌ Dataset is missing columns: {missing}. Re-generating…")
        generate_dataset()
        df = pd.read_csv(CSV_PATH)

    # Coerce numeric columns
    numeric_cols = [c for c in EXPECTED_COLUMNS if c not in ("player_name", "team", "position", "season")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill remaining NaNs
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(0)

    return df


# ---------------------------------------------------------------------------
# SUB-TASK 3 — SIDEBAR FILTERS
# ---------------------------------------------------------------------------

def apply_sidebar_filters(df: pd.DataFrame):
    """
    Render sidebar filters and return (filtered_df, filter_summary).
    Empty selection for any filter means 'all values'.
    """
    st.sidebar.markdown("## ⚽ Filters")

    # Season
    all_seasons = sorted(df["season"].unique().tolist())
    sel_seasons = st.sidebar.multiselect("Season", all_seasons, default=[])

    # Team
    all_teams = sorted(df["team"].unique().tolist())
    sel_teams = st.sidebar.multiselect("Team", all_teams, default=[])

    # Position
    all_positions = [p for p in POSITIONS if p in df["position"].unique()]
    sel_positions = st.sidebar.multiselect("Position", all_positions, default=[])

    # Player (only when ≤ 2 positions selected)
    sel_players = []
    if len(sel_positions) <= 2:
        filtered_for_player = df.copy()
        if sel_seasons:
            filtered_for_player = filtered_for_player[filtered_for_player["season"].isin(sel_seasons)]
        if sel_teams:
            filtered_for_player = filtered_for_player[filtered_for_player["team"].isin(sel_teams)]
        if sel_positions:
            filtered_for_player = filtered_for_player[filtered_for_player["position"].isin(sel_positions)]
        all_players = sorted(filtered_for_player["player_name"].unique().tolist())
        sel_players = st.sidebar.multiselect("Player", all_players, default=[])

    # Apply filters
    filtered = df.copy()
    if sel_seasons:
        filtered = filtered[filtered["season"].isin(sel_seasons)]
    if sel_teams:
        filtered = filtered[filtered["team"].isin(sel_teams)]
    if sel_positions:
        filtered = filtered[filtered["position"].isin(sel_positions)]
    if sel_players:
        filtered = filtered[filtered["player_name"].isin(sel_players)]

    if filtered.empty:
        st.sidebar.warning("⚠️ No data matches these filters. Showing all data.")
        filtered = df.copy()

    # Summary string
    parts = []
    if sel_seasons:
        parts.append(f"Seasons: {', '.join(sel_seasons)}")
    if sel_teams:
        parts.append(f"Teams: {', '.join(sel_teams)}")
    if sel_positions:
        parts.append(f"Positions: {', '.join(sel_positions)}")
    if sel_players:
        parts.append(f"Players: {', '.join(sel_players)}")
    summary = " | ".join(parts) if parts else "All data"

    return filtered, summary


# ---------------------------------------------------------------------------
# SUB-TASK 9 — THEME HELPER
# ---------------------------------------------------------------------------

def apply_layout(fig, title: str = "") -> go.Figure:
    """Apply the global dark-green football theme to any Plotly figure."""
    fig.update_layout(title=title, **PLOT_LAYOUT)
    return fig


def section_header(title: str, subtitle: str = "") -> None:
    """Render a styled section header."""
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.markdown('<hr style="border:1px solid #30363d;margin:4px 0 16px 0">', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SUB-TASK 4 — OVERVIEW PAGE
# ---------------------------------------------------------------------------

def page_overview(df: pd.DataFrame, summary: str) -> None:
    section_header("📊 Overview", f"Filter: {summary}")

    # KPI cards
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(float(df["rating"].mean()), 2)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👤 Players",        f"{total_players:,}")
    c2.metric("⚽ Goals",          f"{total_goals:,}")
    c3.metric("🎯 Assists",        f"{total_assists:,}")
    c4.metric("⏱️ Minutes Played", f"{total_minutes:,}")
    c5.metric("⭐ Avg Rating",     f"{avg_rating}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    # Top 10 Scorers
    with col_a:
        top10 = (
            df.groupby("player_name", as_index=False)["goals"]
            .sum()
            .nlargest(10, "goals")
            .sort_values("goals")
        )
        fig = px.bar(
            top10, x="goals", y="player_name", orientation="h",
            labels={"goals": "Goals", "player_name": "Player"},
            color="goals", color_continuous_scale=["#1a7f37", "#3fb950"],
        )
        fig = apply_layout(fig, "🏆 Top 10 Scorers")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # Goals distribution histogram
    with col_b:
        fig2 = px.histogram(
            df, x="goals", nbins=20,
            labels={"goals": "Goals Scored", "count": "Players"},
            color_discrete_sequence=["#3fb950"],
        )
        fig2 = apply_layout(fig2, "📈 Goals Distribution")
        fig2.update_traces(marker_line_color="#0d1117", marker_line_width=1)
        st.plotly_chart(fig2, use_container_width=True)

    # Top 10 by Rating
    section_header("⭐ Top 10 Rated Players")
    top_rated = (
        df.sort_values("rating", ascending=False)
        .drop_duplicates("player_name")
        .head(10)[["player_name", "team", "position", "season", "goals", "assists", "rating"]]
        .reset_index(drop=True)
    )
    st.dataframe(top_rated, use_container_width=True)


# ---------------------------------------------------------------------------
# SUB-TASK 5 — PLAYER ANALYSIS PAGE
# ---------------------------------------------------------------------------

def page_player_analysis(df: pd.DataFrame, summary: str) -> None:
    section_header("🔍 Player Analysis", f"Filter: {summary}")

    if df.empty:
        st.warning("No player data available for the current filters.")
        return

    # Shot accuracy (guard div-by-zero)
    df = df.copy()
    df["shot_accuracy"] = np.where(df["shots"] > 0, df["shots_on_target"] / df["shots"] * 100, 0)
    df["shot_accuracy"] = df["shot_accuracy"].round(1)

    col_a, col_b = st.columns(2)

    # Goals vs Assists scatter
    with col_a:
        fig = px.scatter(
            df, x="goals", y="assists", color="position",
            hover_data={"player_name": True, "team": True, "rating": True,
                        "goals": True, "assists": True},
            labels={"goals": "Goals", "assists": "Assists", "position": "Position"},
            size="minutes_played", size_max=18,
            category_orders={"position": POSITIONS},
        )
        fig = apply_layout(fig, "⚽ Goals vs Assists")
        st.plotly_chart(fig, use_container_width=True)

    # Shots vs Goals scatter
    with col_b:
        fig2 = px.scatter(
            df, x="shots", y="goals", color="position",
            hover_data={"player_name": True, "team": True,
                        "shot_accuracy": True, "shots": True, "goals": True},
            labels={"shots": "Shots", "goals": "Goals", "position": "Position",
                    "shot_accuracy": "Shot Acc %"},
            size="minutes_played", size_max=18,
            category_orders={"position": POSITIONS},
        )
        fig2 = apply_layout(fig2, "🎯 Shots vs Goals")
        st.plotly_chart(fig2, use_container_width=True)

    # ---- Player Comparison ------------------------------------------------
    section_header("🆚 Player Comparison")
    default_players = (
        df.nlargest(2, "goals")["player_name"].tolist()
        if len(df) >= 2 else df["player_name"].tolist()
    )
    player_names = sorted(df["player_name"].unique().tolist())
    selected = st.multiselect(
        "Select 2–5 players to compare",
        player_names,
        default=default_players[:2],
        max_selections=5,
    )

    if len(selected) < 2:
        st.info("Please select at least 2 players.")
        return

    comp_df = df[df["player_name"].isin(selected)].copy()
    # Aggregate in case a player appears across multiple seasons
    comp_agg = (
        comp_df.groupby("player_name", as_index=False)
        .agg(goals=("goals","sum"), assists=("assists","sum"),
             rating=("rating","mean"), tackles=("tackles","sum"),
             key_passes=("key_passes","sum"))
    )
    comp_agg["rating"] = comp_agg["rating"].round(2)

    COMPARE_STATS = ["goals", "assists", "rating", "tackles", "key_passes"]

    col_bar, col_radar = st.columns(2)

    # Grouped Bar Chart
    with col_bar:
        fig_bar = go.Figure()
        for _, row in comp_agg.iterrows():
            fig_bar.add_trace(go.Bar(
                name=row["player_name"],
                x=[s.replace("_", " ").title() for s in COMPARE_STATS],
                y=[row[s] for s in COMPARE_STATS],
            ))
        fig_bar.update_layout(barmode="group", **PLOT_LAYOUT, title="📊 Stat Comparison")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Radar Chart (normalise to 0–100)
    with col_radar:
        fig_radar = go.Figure()
        maxima = {s: comp_agg[s].max() for s in COMPARE_STATS}
        categories = [s.replace("_", " ").title() for s in COMPARE_STATS]
        for _, row in comp_agg.iterrows():
            vals = [
                round(row[s] / maxima[s] * 100, 1) if maxima[s] > 0 else 0
                for s in COMPARE_STATS
            ]
            vals_closed = vals + [vals[0]]
            cats_closed = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_closed,
                theta=cats_closed,
                fill="toself",
                name=row["player_name"],
                opacity=0.75,
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#161b22",
                radialaxis=dict(visible=True, range=[0, 100],
                                gridcolor="#30363d", tickfont=dict(color="#e6edf3")),
                angularaxis=dict(gridcolor="#30363d", tickfont=dict(color="#e6edf3")),
            ),
            **PLOT_LAYOUT,
            title="🕸️ Radar Comparison (Normalised 0–100)",
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ---- SUB-TASK 8: Searchable Stats Table + CSV Download ----------------
    section_header("📋 Player Statistics Table")
    search_term = st.text_input("🔍 Search by player name or team", "")
    display_df = df.copy()
    if search_term.strip():
        mask = (
            display_df["player_name"].str.contains(search_term, case=False, na=False) |
            display_df["team"].str.contains(search_term, case=False, na=False)
        )
        display_df = display_df[mask]

    st.dataframe(
        display_df.sort_values("goals", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_bytes,
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------------------------
# SUB-TASK 6 — TEAM ANALYSIS PAGE
# ---------------------------------------------------------------------------

def page_team_analysis(df: pd.DataFrame, summary: str) -> None:
    section_header("🏟️ Team Analysis", f"Filter: {summary}")

    if df.empty:
        st.warning("No team data available for the current filters.")
        return

    team_agg = (
        df.groupby("team", as_index=False)
        .agg(
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            player_count=("player_id", "nunique"),
            avg_rating=("rating", "mean"),
        )
        .sort_values("total_goals", ascending=False)
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)

    col_a, col_b = st.columns(2)

    # Grouped bar: goals + assists per team
    with col_a:
        fig = px.bar(
            team_agg.melt(id_vars="team", value_vars=["total_goals", "total_assists"],
                          var_name="Metric", value_name="Value"),
            x="team", y="Value", color="Metric", barmode="group",
            labels={"team": "Team", "Value": "Count", "Metric": ""},
            color_discrete_map={"total_goals": "#3fb950", "total_assists": "#58a6ff"},
        )
        fig = apply_layout(fig, "⚽ Goals & Assists per Team")
        fig.update_xaxes(tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

    # Pie: player count per team
    with col_b:
        fig2 = px.pie(
            team_agg, names="team", values="player_count",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2 = apply_layout(fig2, "👥 Player Count per Team")
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    # Avg rating bar
    section_header("⭐ Average Rating per Team")
    fig3 = px.bar(
        team_agg.sort_values("avg_rating", ascending=True),
        x="avg_rating", y="team", orientation="h",
        labels={"avg_rating": "Avg Rating", "team": "Team"},
        color="avg_rating", color_continuous_scale=["#1a7f37", "#3fb950"],
        range_x=[5, 10],
    )
    fig3 = apply_layout(fig3, "")
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)

    section_header("📋 Team Summary Table")
    st.dataframe(team_agg.reset_index(drop=True), use_container_width=True)


# ---------------------------------------------------------------------------
# SUB-TASK 7 — POSITION ANALYSIS PAGE
# ---------------------------------------------------------------------------

def page_position_analysis(df: pd.DataFrame, summary: str) -> None:
    section_header("📐 Position Analysis", f"Filter: {summary}")

    if df.empty:
        st.warning("No data available for the current filters.")
        return

    col_a, col_b = st.columns(2)

    # Box plot: goals by position
    with col_a:
        fig = px.box(
            df, x="position", y="goals",
            category_orders={"position": POSITIONS},
            labels={"position": "Position", "goals": "Goals"},
            color="position",
            color_discrete_sequence=PLOT_LAYOUT["colorway"],
        )
        fig = apply_layout(fig, "⚽ Goals Distribution by Position")
        st.plotly_chart(fig, use_container_width=True)

    # Avg rating by position
    with col_b:
        pos_rating = (
            df.groupby("position", as_index=False)["rating"]
            .mean()
            .rename(columns={"rating": "avg_rating"})
        )
        pos_rating["avg_rating"] = pos_rating["avg_rating"].round(2)
        pos_rating["position"] = pd.Categorical(pos_rating["position"], categories=POSITIONS, ordered=True)
        pos_rating = pos_rating.sort_values("position")

        fig2 = px.bar(
            pos_rating, x="position", y="avg_rating",
            labels={"position": "Position", "avg_rating": "Avg Rating"},
            color="position",
            color_discrete_sequence=PLOT_LAYOUT["colorway"],
            range_y=[5, 10],
        )
        fig2 = apply_layout(fig2, "⭐ Average Rating by Position")
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Position count pie
    section_header("👥 Squad Composition by Position")
    pos_count = df.groupby("position", as_index=False)["player_id"].nunique()
    pos_count.columns = ["position", "player_count"]

    col_pie, col_stats = st.columns(2)
    with col_pie:
        fig3 = px.pie(
            pos_count, names="position", values="player_count",
            category_orders={"position": POSITIONS},
            color_discrete_sequence=PLOT_LAYOUT["colorway"],
        )
        fig3 = apply_layout(fig3, "")
        fig3.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig3, use_container_width=True)

    with col_stats:
        pos_agg = (
            df.groupby("position", as_index=False)
            .agg(
                players=("player_id", "nunique"),
                total_goals=("goals", "sum"),
                total_assists=("assists", "sum"),
                avg_rating=("rating", "mean"),
            )
        )
        pos_agg["avg_rating"] = pos_agg["avg_rating"].round(2)
        pos_agg["position"] = pd.Categorical(pos_agg["position"], categories=POSITIONS, ordered=True)
        pos_agg = pos_agg.sort_values("position")
        st.dataframe(pos_agg.reset_index(drop=True), use_container_width=True)

    # GK-specific section (shown only when GK data is present)
    gk_df = df[df["position"] == "GK"]
    if not gk_df.empty:
        section_header("🧤 Goalkeeper Metrics")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_saves = px.histogram(
                gk_df, x="saves", nbins=15,
                labels={"saves": "Saves", "count": "GKs"},
                color_discrete_sequence=["#58a6ff"],
            )
            fig_saves = apply_layout(fig_saves, "🧤 Saves Distribution")
            st.plotly_chart(fig_saves, use_container_width=True)

        with col_g2:
            fig_cs = px.histogram(
                gk_df, x="clean_sheets", nbins=10,
                labels={"clean_sheets": "Clean Sheets", "count": "GKs"},
                color_discrete_sequence=["#3fb950"],
            )
            fig_cs = apply_layout(fig_cs, "🚫 Clean Sheets Distribution")
            st.plotly_chart(fig_cs, use_container_width=True)


# ---------------------------------------------------------------------------
# MAIN — PAGE ROUTER + SIDEBAR HEADER
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Football Analytics Dashboard",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Sidebar header
    st.sidebar.markdown(
        """
        <div style='text-align:center; padding: 8px 0 16px 0'>
            <span style='font-size:2.5rem'>⚽</span><br>
            <span style='font-size:1.1rem; font-weight:700; color:#3fb950'>
                Football Analytics
            </span><br>
            <span style='font-size:0.75rem; color:#57606a'>
                ⚠️ Synthetic data — not real player statistics
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Page navigation
    page = st.sidebar.radio(
        "Navigate",
        ["📊 Overview", "🔍 Player Analysis", "🏟️ Team Analysis", "📐 Position Analysis"],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")

    # Load data
    df = load_data()

    # Apply filters
    filtered_df, summary = apply_sidebar_filters(df)

    # Route to selected page
    if page == "📊 Overview":
        page_overview(filtered_df, summary)
    elif page == "🔍 Player Analysis":
        page_player_analysis(filtered_df, summary)
    elif page == "🏟️ Team Analysis":
        page_team_analysis(filtered_df, summary)
    elif page == "📐 Position Analysis":
        page_position_analysis(filtered_df, summary)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("Built with Streamlit & Plotly")


if __name__ == "__main__":
    main()

"""ABS Challenge Explorer - Streamlit App

Interactive umpire challenge maps and leaderboards for Spring Training 2026.
Data: cached JSON from output/abs/
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DARK_BG = "#1a1b2e"
CARD_BG = "#232D3F"
ACCENT = "#22D1EE"
TEXT_WHITE = "#E8E8E8"
TEXT_DIM = "#7A8BA0"
OVERTURNED = "#ff6b6b"
UPHELD = "#51cf66"

PLATE_HALF_FT = 0.7083  # half plate width: 17 inches / 2 / 12
DEFAULT_SZ_TOP = 3.4
DEFAULT_SZ_BOT = 1.6
KDE_BW = 0.3
KDE_GRID = 200  # grid resolution for KDE
KDE_NCONTOURS = 20

HOVER_LABEL = dict(bgcolor=CARD_BG, font_color=TEXT_WHITE, bordercolor=ACCENT)

KDE_COLORSCALE = [
    [0, "rgba(26,27,46,0)"],
    [0.1, "rgba(60,0,50,0.3)"],
    [0.2, "rgba(90,0,65,0.45)"],
    [0.3, "rgba(120,0,80,0.55)"],
    [0.4, "rgba(145,0,95,0.65)"],
    [0.5, "rgba(165,10,110,0.72)"],
    [0.6, "rgba(185,20,125,0.78)"],
    [0.7, "rgba(205,30,140,0.82)"],
    [0.8, "rgba(225,45,155,0.86)"],
    [0.9, "rgba(240,60,170,0.90)"],
    [1.0, "rgba(255,80,180,0.92)"],
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def metric_card(label, value, subtext=None, delta=None, delta_color=None):
    """Render a custom metric card with subtext inside the box."""
    delta_html = ""
    if delta:
        if delta_color == "normal":
            d_color = UPHELD if delta.startswith("+") else OVERTURNED
        else:
            d_color = TEXT_DIM
        delta_html = f'<div style="font-size:0.8rem; color:{d_color};">{delta}</div>'
    sub_html = ""
    if subtext:
        sub_html = f'<div style="font-size:0.8rem; color:{TEXT_DIM}; margin-top:0.25rem;">{subtext}</div>'
    return (
        f'<div style="background-color:{CARD_BG}; padding:1rem; border-radius:0.5rem;">'
        f'<div style="font-size:0.85rem; color:{TEXT_DIM};">{label}</div>'
        f'<div style="font-size:2rem; font-weight:600; color:{ACCENT};">{value}</div>'
        f'{delta_html}{sub_html}'
        f'</div>'
    )


def vectorized_zone_distance(px, pz, sz_top, sz_bot):
    """Compute distance from zone edge for each pitch (vectorized)."""
    abs_px = np.abs(px)
    dx = np.maximum(0, abs_px - PLATE_HALF_FT)
    dz_above = np.maximum(0, pz - sz_top)
    dz_below = np.maximum(0, sz_bot - pz)
    dz = np.maximum(dz_above, dz_below)
    outside = (dx > 0) | (dz > 0)
    outside_dist = np.sqrt(dx**2 + dz**2)
    inside_dist = -np.minimum(
        np.minimum(PLATE_HALF_FT - abs_px, abs_px + PLATE_HALF_FT),
        np.minimum(pz - sz_bot, sz_top - pz),
    )
    return np.where(outside, outside_dist, inside_dist)


def build_summary_prompt(filt_df, ump, team, league_avgs, called_df):
    """Build a prompt with rich stats context for the LLM."""
    n = len(filt_df)
    n_ot = (filt_df["result"] == "overturned").sum()
    n_up = n - n_ot
    ot_rate = n_ot / max(n, 1) * 100
    avg_imp = filt_df["impact_score"].mean() if n > 0 else 0

    call_breakdown = ""
    if n > 0:
        by_call = filt_df.groupby("original_call").agg(
            count=("result", "size"),
            overturned=("result", lambda x: (x == "overturned").sum()),
        ).reset_index()
        by_call["ot_pct"] = (by_call["overturned"] / by_call["count"] * 100).round(1)
        for _, r in by_call.iterrows():
            call_breakdown += f"  - {r['original_call']}: {r['count']} challenges, {r['ot_pct']}% overturned\n"

    pitch_breakdown = ""
    if "pitch_name" in filt_df.columns and n > 0:
        by_pitch = filt_df.groupby("pitch_name").agg(
            count=("result", "size"),
            overturned=("result", lambda x: (x == "overturned").sum()),
        ).reset_index().sort_values("count", ascending=False).head(5)
        for _, r in by_pitch.iterrows():
            pt_ot = r["overturned"] / max(r["count"], 1) * 100
            pitch_breakdown += f"  - {r['pitch_name']}: {r['count']} challenges, {pt_ot:.0f}% overturned\n"

    zone_analysis = ""
    if n > 0:
        valid_z = filt_df.dropna(subset=["pX", "pZ"])
        if len(valid_z) > 0:
            zone_analysis = (
                f"  Avg horizontal distance from center: {valid_z['pX'].abs().mean():.2f} ft\n"
                f"  Avg vertical location: {valid_z['pZ'].mean():.2f} ft\n"
                f"  High zone challenges (pZ > 3.2): {(valid_z['pZ'] > 3.2).sum()}\n"
                f"  Low zone challenges (pZ < 1.8): {(valid_z['pZ'] < 1.8).sum()}\n"
                f"  Outside edge challenges (|pX| > 0.7): {(valid_z['pX'].abs() > 0.7).sum()}\n"
            )

    impact_info = ""
    if n > 0:
        impact_info = (
            f"  High impact (70+): {(filt_df['impact_score'] >= 70).sum()}, "
            f"Medium (40-69): {((filt_df['impact_score'] >= 40) & (filt_df['impact_score'] < 70)).sum()}, "
            f"Low (<40): {(filt_df['impact_score'] < 40).sum()}\n"
        )

    zone_info = ""
    if called_df is not None and ump != "All Umpires":
        ump_strikes = called_df[(called_df["umpire"] == ump) & (called_df["call"] == "Called Strike")]
        ump_balls = called_df[(called_df["umpire"] == ump) & (called_df["call"] == "Ball")]
        if len(ump_strikes) > 0:
            avg_strike_px = ump_strikes["pX"].abs().mean()
            zone_info = (
                f"  Called strikes: {len(ump_strikes)}, Called balls: {len(ump_balls)}\n"
                f"  Avg called strike horizontal spread: {avg_strike_px:.2f} ft from center\n"
                f"  Avg called strike height: {ump_strikes['pZ'].mean():.2f} ft\n"
                f"  Zone width tendency: {'wider than avg' if avg_strike_px > 0.55 else 'tighter than avg'}\n"
            )

    ump_label = ump if ump != "All Umpires" else "all umpires"
    team_label = team if team != "All Teams" else "all teams"

    return f"""You are a baseball analytics expert providing a broadcast-ready summary for a radio color commentator. Analyze this ABS (Automated Ball-Strike) challenge data from Spring Training 2026.

Current view: {ump_label}, {team_label}
Total challenges: {n}
Overturned: {n_ot} ({ot_rate:.1f}%)
Upheld: {n_up} ({100-ot_rate:.1f}%)
Avg impact score: {avg_imp:.1f}
MLB avg overturn rate: {league_avgs['overturn_pct']:.1f}%
MLB avg impact: {league_avgs['avg_impact']:.1f}

Breakdown by original call:
{call_breakdown}
Top pitch types challenged:
{pitch_breakdown}
Zone location analysis:
{zone_analysis}
Impact distribution:
{impact_info}
Umpire's established zone (from all called pitches):
{zone_info}

Write a 3-4 sentence analyst summary. Be specific with numbers. Note anything unusual - is the overturn rate above or below average? Are challenges clustered in a certain zone? Which pitch types cause the most trouble? If viewing a specific umpire, comment on their zone tendencies. Keep the tone sharp and informative, like you're briefing a broadcast booth before a game. No filler, no fluff."""


@st.cache_data
def get_ai_summary(prompt):
    """Call Claude Haiku for a fast, cheap summary. Cached by prompt."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            api_key = ""
    if not api_key or api_key == "your-key-here":
        return None

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Cached data loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_challenges():
    for p in [
        Path(__file__).parent.parent / "output" / "abs" / "spring_training_challenges.json",
        Path("output/abs/spring_training_challenges.json"),
    ]:
        if p.exists():
            with open(p) as f:
                raw = json.load(f)
            df = pd.DataFrame(raw)
            df["date"] = pd.to_datetime(df["date"])
            df["impact_score"] = df["impact"].apply(
                lambda x: x.get("impact_score", 0) if isinstance(x, dict) else 0
            )
            df["impact_label"] = df["impact"].apply(
                lambda x: x.get("impact_label", "") if isinstance(x, dict) else ""
            )
            return df
    st.error("Challenge data not found. Expected at output/abs/spring_training_challenges.json")
    st.stop()


@st.cache_data
def load_called_pitches(cache_bust=None):
    for p in [
        Path(__file__).parent.parent / "output" / "abs" / "umpire_called_pitches.json",
        Path("output/abs/umpire_called_pitches.json"),
    ]:
        if p.exists():
            with open(p) as f:
                return pd.DataFrame(json.load(f))
    return None


@st.cache_data
def compute_league_averages(_df_hash):
    """Compute MLB-wide averages. Takes hash to work with cache."""
    df = load_challenges()
    by_ump = df.groupby("umpire").agg(
        challenges=("result", "size"),
        overturned=("result", lambda x: (x == "overturned").sum()),
        avg_impact=("impact_score", "mean"),
    ).reset_index()
    by_ump["overturn_pct"] = by_ump["overturned"] / by_ump["challenges"] * 100
    by_ump["upheld_pct"] = 100 - by_ump["overturn_pct"]
    return {
        "challenges": by_ump["challenges"].mean(),
        "overturn_pct": by_ump["overturn_pct"].mean(),
        "upheld_pct": by_ump["upheld_pct"].mean(),
        "avg_impact": by_ump["avg_impact"].mean(),
    }


@st.cache_data
def compute_kde(px_values, pz_values, bw=KDE_BW):
    """Cached KDE computation - the expensive part."""
    xmin, xmax = -2.0, 2.0
    zmin, zmax = 0.0, 4.5
    xx, zz = np.mgrid[xmin:xmax:200j, zmin:zmax:200j]
    positions = np.vstack([xx.ravel(), zz.ravel()])
    kernel = gaussian_kde(np.vstack([px_values, pz_values]), bw_method=bw)
    density = np.reshape(kernel(positions), xx.shape)
    return density, np.linspace(xmin, xmax, 200), np.linspace(zmin, zmax, 200)


# ---------------------------------------------------------------------------
# Page config and CSS
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="mlbumpviz | ABS Challenge Explorer",
    page_icon="baseball",
    layout="wide",
)

st.markdown(f"""
<style>
    .stApp {{
        background-color: {DARK_BG};
    }}
    header[data-testid="stHeader"] {{
        background-color: {DARK_BG};
    }}
    .stSelectbox label, .stMultiSelect label {{
        color: {TEXT_DIM} !important;
    }}
    h1, h2, h3, p, span, label {{
        color: {TEXT_WHITE} !important;
    }}
    div[data-testid="stDataFrame"] {{
        background-color: {CARD_BG};
        border-radius: 0.5rem;
    }}
    .credit {{
        text-align: right;
        color: {TEXT_DIM};
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
with st.spinner("Loading data..."):
    df = load_challenges()
    _cp_path = Path(__file__).parent.parent / "output" / "abs" / "umpire_called_pitches.json"
    _cp_mtime = _cp_path.stat().st_mtime if _cp_path.exists() else 0
    called_pitches_df = load_called_pitches(cache_bust=_cp_mtime)
    league_avg = compute_league_averages(_df_hash=len(df))

# Pre-filter umpire's full data once
all_umpires = sorted(df["umpire"].unique().tolist())
all_teams = sorted(df["challenge_team"].unique().tolist())

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("ABS Challenge Explorer")
st.caption("Spring Training 2026")

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1])

with col_f1:
    selected_umpire = st.selectbox("Umpire", ["All Umpires"] + all_umpires)

# Cross-filter teams based on umpire
if selected_umpire != "All Umpires":
    available_teams = sorted(
        df[df["umpire"] == selected_umpire]["challenge_team"].unique().tolist()
    )
else:
    available_teams = all_teams

with col_f2:
    selected_team = st.selectbox("Challenging Team", ["All Teams"] + available_teams)

with col_f3:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

# Result circle buttons
with col_f4:
    st.markdown("Result")
    btn_col1, btn_col2 = st.columns(2)

    if "show_overturned" not in st.session_state:
        st.session_state.show_overturned = True
    if "show_upheld" not in st.session_state:
        st.session_state.show_upheld = True

    with btn_col1:
        ot_active = st.session_state.show_overturned
        if st.button(
            f"{'●' if ot_active else '○'} Overturned",
            key="btn_ot",
            use_container_width=True,
        ):
            st.session_state.show_overturned = not st.session_state.show_overturned
            st.rerun()

    with btn_col2:
        up_active = st.session_state.show_upheld
        if st.button(
            f"{'●' if up_active else '○'} Upheld",
            key="btn_up",
            use_container_width=True,
        ):
            st.session_state.show_upheld = not st.session_state.show_upheld
            st.rerun()

show_overturned = st.session_state.show_overturned
show_upheld = st.session_state.show_upheld

result_filter = []
if show_overturned:
    result_filter.append("overturned")
if show_upheld:
    result_filter.append("upheld")

# Apply filters
filtered = df

# Date range filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    d_start, d_end = date_range
    filtered = filtered[
        (filtered["date"].dt.date >= d_start) & (filtered["date"].dt.date <= d_end)
    ]

if selected_umpire != "All Umpires":
    filtered = filtered[filtered["umpire"] == selected_umpire]
if selected_team != "All Teams":
    filtered = filtered[filtered["challenge_team"] == selected_team]

# Warn on impossible umpire+team combo
if len(filtered) == 0 and selected_umpire != "All Umpires" and selected_team != "All Teams":
    st.warning(f"No challenges found for {selected_umpire} + {selected_team}.")

# Unfiltered data for this umpire/team (ignores result buttons)
ump_team_all = filtered.copy()

# Now apply result filter for dots
if result_filter:
    filtered = filtered[filtered["result"].isin(result_filter)]
else:
    filtered = filtered.iloc[0:0]

single_umpire = selected_umpire != "All Umpires"
n_total = len(filtered)
n_ot = (filtered["result"] == "overturned").sum()
n_up = (filtered["result"] == "upheld").sum()
ot_pct = n_ot / max(n_total, 1) * 100
avg_impact = filtered["impact_score"].mean() if n_total > 0 else 0

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
total_called = len(called_pitches_df) if called_pitches_df is not None else 0

if single_umpire:
    ump_n = len(ump_team_all)
    ump_ot = (ump_team_all["result"] == "overturned").sum()
    ump_up = ump_n - ump_ot
    accuracy = ump_up / max(ump_n, 1) * 100
    accuracy_delta = accuracy - league_avg["upheld_pct"]
    ump_avg_impact = ump_team_all["impact_score"].mean() if ump_n > 0 else 0
    impact_delta = ump_avg_impact - league_avg["avg_impact"]
    ump_games = df[df["umpire"] == selected_umpire]["game_id"].nunique()

    ump_called = 0
    if called_pitches_df is not None:
        ump_called = len(called_pitches_df[called_pitches_df["umpire"] == selected_umpire])
    challenge_pct = ump_n / max(ump_called, 1) * 100

    games_sub = (
        f"{ump_called:,} called pitches &nbsp;|&nbsp; "
        f"{ump_n:,} challenged "
        f"<span style='font-size:0.7rem;'>({challenge_pct:.1f}%)</span>"
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.markdown(metric_card("Games", ump_games, subtext=games_sub), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Challenges", ump_n, subtext=f"Overturned: {ump_ot} &nbsp;|&nbsp; Upheld: {ump_up}"), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Accuracy", f"{accuracy:.0f}%", delta=f"{accuracy_delta:+.1f}pp vs avg", delta_color="normal"), unsafe_allow_html=True)
    col_m4.markdown(metric_card("Avg Impact", f"{ump_avg_impact:.1f}", delta=f"{impact_delta:+.1f} vs avg"), unsafe_allow_html=True)
else:
    all_games = df["game_id"].nunique()
    all_n = len(ump_team_all)
    all_ot = (ump_team_all["result"] == "overturned").sum()
    all_up = all_n - all_ot
    all_ot_pct = all_ot / max(all_n, 1) * 100
    challenge_pct = all_n / max(total_called, 1) * 100

    games_sub = (
        f"{total_called:,} called pitches &nbsp;|&nbsp; "
        f"{all_n:,} challenged "
        f"<span style='font-size:0.7rem;'>({challenge_pct:.1f}%)</span>"
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    all_up_pct = 100 - all_ot_pct

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    col_m1.markdown(metric_card("Games", all_games, subtext=games_sub), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Challenges", all_n, subtext=f"Overturned: {all_ot} &nbsp;|&nbsp; Upheld: {all_up}"), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Overturn Rate", f"{all_ot_pct:.0f}%", subtext=f"{all_ot:,} overturned"), unsafe_allow_html=True)
    col_m4.markdown(metric_card("Upheld Rate", f"{all_up_pct:.0f}%", subtext=f"{all_up:,} upheld"), unsafe_allow_html=True)
    col_m5.markdown(metric_card("Avg Impact", f"{ump_team_all['impact_score'].mean():.1f}" if all_n > 0 else "0"), unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Challenge Map (zone always renders; dots only when challenges match)
# ---------------------------------------------------------------------------
valid = filtered.dropna(subset=["pX", "pZ"]) if n_total > 0 else pd.DataFrame()

if len(valid) > 0:
    valid = valid.copy()
    sz_t = valid["sz_top"].fillna(DEFAULT_SZ_TOP).values
    sz_b = valid["sz_bottom"].fillna(DEFAULT_SZ_BOT).values
    dist = vectorized_zone_distance(valid["pX"].values, valid["pZ"].values, sz_t, sz_b)
    valid["zone_dist"] = dist
    valid["zone_dist_label"] = [
        f"{abs(d) * 12:.1f} in {'outside' if d > 0 else 'inside'} zone" for d in dist
    ]

fig = go.Figure()

# -- Established zone heatmap from ALL called strikes --
zone_source_label = ""
if called_pitches_df is not None:
    all_strikes = called_pitches_df[called_pitches_df["call"] == "Called Strike"]
    has_team_col = "batting_team" in called_pitches_df.columns

    if single_umpire:
        zone_strikes = all_strikes[all_strikes["umpire"] == selected_umpire]
        zone_source_label = f"{selected_umpire}'s zone ({len(zone_strikes)} called strikes)"
    elif selected_team != "All Teams" and has_team_col:
        zone_strikes = all_strikes[all_strikes["batting_team"] == selected_team]
        zone_source_label = f"{selected_team} batting zone ({len(zone_strikes)} called strikes)"
    else:
        zone_strikes = all_strikes
        zone_source_label = f"MLB avg zone ({len(zone_strikes):,} called strikes)"

    if len(zone_strikes) >= 20:
        try:
            density, x_grid, z_grid = compute_kde(
                zone_strikes["pX"].values, zone_strikes["pZ"].values
            )
            fig.add_trace(go.Contour(
                x=x_grid, y=z_grid, z=density.T,
                colorscale=KDE_COLORSCALE,
                ncontours=KDE_NCONTOURS,
                contours=dict(coloring="fill", showlines=True, showlabels=False),
                line=dict(width=0.5, color="rgba(255,255,255,0.08)"),
                showscale=True,
                colorbar=dict(
                    title="", orientation="h",
                    y=-0.08, yanchor="top", x=0.25, xanchor="center",
                    len=0.35, thickness=12, tickvals=[], ticktext=[],
                ),
                hoverinfo="skip",
                showlegend=False,
            ))
        except np.linalg.LinAlgError:
            st.caption("Zone heatmap unavailable - insufficient data for this selection.")

    # Secondary team zone contour when both umpire and team selected
    if single_umpire and selected_team != "All Teams" and has_team_col:
        team_strikes = all_strikes[all_strikes["batting_team"] == selected_team]
        if len(team_strikes) >= 20:
            try:
                td, tx, tz = compute_kde(team_strikes["pX"].values, team_strikes["pZ"].values)
                fig.add_trace(go.Contour(
                    x=tx, y=tz, z=td.T,
                    contours=dict(
                        coloring="none", showlines=True, showlabels=False,
                        start=td.max() * 0.20, end=td.max() * 0.20, size=1,
                    ),
                    line=dict(width=2.5, color="#FFD93D", dash="dot"),
                    showscale=False, hoverinfo="skip",
                    showlegend=True,
                    name=f"{selected_team} Batting Zone ({len(team_strikes)} CS)",
                ))
            except np.linalg.LinAlgError:
                pass

# Rule book strike zone
sz_top = DEFAULT_SZ_TOP
sz_bot = DEFAULT_SZ_BOT
if len(valid) > 0 and "sz_top" in valid.columns:
    sz_top = valid["sz_top"].mean()
    sz_bot = valid["sz_bottom"].mean()
elif called_pitches_df is not None and single_umpire:
    ump_cp = called_pitches_df[called_pitches_df["umpire"] == selected_umpire]
    if len(ump_cp) > 0:
        sz_top = ump_cp["sz_top"].mean()
        sz_bot = ump_cp["sz_bottom"].mean()

# Zone box (using shapes instead of traces)
for x0, x1, y0, y1 in [
    (-PLATE_HALF_FT, PLATE_HALF_FT, sz_bot, sz_bot),
    (-PLATE_HALF_FT, PLATE_HALF_FT, sz_top, sz_top),
    (-PLATE_HALF_FT, -PLATE_HALF_FT, sz_bot, sz_top),
    (PLATE_HALF_FT, PLATE_HALF_FT, sz_bot, sz_top),
]:
    fig.add_shape(type="line", x0=x0, x1=x1, y0=y0, y1=y1,
                  line=dict(color="rgba(255,255,255,0.5)", width=2))

# Inner zone grid
third_h = (sz_top - sz_bot) / 3
third_w = PLATE_HALF_FT * 2 / 3
for i in range(1, 3):
    fig.add_shape(type="line",
                  x0=-PLATE_HALF_FT, x1=PLATE_HALF_FT,
                  y0=sz_bot + third_h * i, y1=sz_bot + third_h * i,
                  line=dict(color="rgba(255,255,255,0.12)", width=0.5, dash="dot"))
    fig.add_shape(type="line",
                  x0=-PLATE_HALF_FT + third_w * i, x1=-PLATE_HALF_FT + third_w * i,
                  y0=sz_bot, y1=sz_top,
                  line=dict(color="rgba(255,255,255,0.12)", width=0.5, dash="dot"))

# Home plate
plate_y = 0.5
fig.add_trace(go.Scatter(
    x=[-PLATE_HALF_FT, -PLATE_HALF_FT, 0, PLATE_HALF_FT, PLATE_HALF_FT, -PLATE_HALF_FT],
    y=[plate_y, plate_y - 0.15, plate_y - 0.3, plate_y - 0.15, plate_y, plate_y],
    mode="lines",
    line=dict(color="rgba(255,255,255,0.3)", width=1),
    fill="toself", fillcolor="rgba(255,255,255,0.05)",
    showlegend=False, hoverinfo="skip",
))

# Challenge dots (only when challenges exist)
if len(valid) > 0:
    for result_val, color, marker_symbol, label_prefix in [
        ("overturned", OVERTURNED, "circle", "Overturned"),
        ("upheld", UPHELD, "circle", "Upheld"),
    ]:
        subset = valid[valid["result"] == result_val]
        if len(subset) == 0:
            continue

        fig.add_trace(go.Scatter(
            x=subset["pX"], y=subset["pZ"],
            mode="markers+text",
            marker=dict(
                size=16, color=color, opacity=0.75, symbol=marker_symbol,
                line=dict(width=2, color="white"),
            ),
            text=subset["challenge_team"],
            textfont=dict(size=7, color="white"),
            textposition="middle center",
            name=f"{label_prefix} ({len(subset)})",
            customdata=np.stack([
                subset["umpire"],
                subset["batter"],
                subset["pitcher"],
                subset["pitch_name"],
                subset["speed"].round(1).astype(str),
                subset["original_call"],
                subset["impact_score"].round(0).astype(str),
                subset["date"].dt.strftime("%m/%d"),
                subset["zone_dist_label"],
                subset["pitch_type"].fillna(""),
            ], axis=-1),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[7]} | %{customdata[5]}<br>"
                "%{customdata[1]} vs %{customdata[2]}<br>"
                "%{customdata[3]} (%{customdata[9]}) @ %{customdata[4]} mph<br>"
                "Impact: %{customdata[6]}<br>"
                "<b>%{customdata[8]}</b><br>"
                "pX: %{x:.2f} | pZ: %{y:.2f}"
                "<extra></extra>"
            ),
        ))

        # Pitch type labels as a separate text-only trace (no per-row loop)
        has_pt = subset["pitch_type"].notna() & (subset["pitch_type"] != "")
        if has_pt.any():
            pt_sub = subset[has_pt]
            fig.add_trace(go.Scatter(
                x=pt_sub["pX"] + 0.12, y=pt_sub["pZ"],
                mode="text",
                text=pt_sub["pitch_type"],
                textfont=dict(size=8, color=TEXT_DIM),
                textposition="middle right",
                showlegend=False, hoverinfo="skip",
            ))

# Title
ump_label = selected_umpire if single_umpire else "All Umpires"
team_label = selected_team if selected_team != "All Teams" else "All Teams"
n_challenges_shown = len(valid)

title_line1 = f"<b>ABS Challenge Map: {ump_label}</b>"
subtitle_parts = ["Spring Training 2026"]
if selected_team != "All Teams":
    subtitle_parts.append(team_label)
if zone_source_label:
    subtitle_parts.append(zone_source_label)
title_line2 = f"<span style='font-size:13px;color:{TEXT_DIM}'>{' | '.join(subtitle_parts)}</span>"

if n_challenges_shown > 0:
    ch_ot = (valid["result"] == "overturned").sum()
    ch_up = n_challenges_shown - ch_ot
    ch_ot_pct = ch_ot / n_challenges_shown * 100
    title_line3 = (
        f"<span style='font-size:13px;color:{TEXT_DIM}'>"
        f"{n_challenges_shown} challenges | "
        f"{ch_ot} overturned ({ch_ot_pct:.0f}%) | "
        f"{ch_up} upheld ({100 - ch_ot_pct:.0f}%)</span>"
    )
else:
    title_line3 = f"<span style='font-size:13px;color:{TEXT_DIM}'>No challenges selected</span>"

fig.update_layout(
    title=dict(
        text=f"{title_line1}<br>{title_line2}<br>{title_line3}",
        font=dict(size=18, color="white"),
        x=0.5,
    ),
    xaxis=dict(
        title="Horizontal Location (ft from center)",
        range=[-2, 2], autorange=False,
        zeroline=False,
        gridcolor="rgba(255,255,255,0.05)",
        color=TEXT_DIM,
    ),
    yaxis=dict(
        title="Vertical Location (ft)",
        range=[0, 4.5], autorange=False,
        zeroline=False,
        gridcolor="rgba(255,255,255,0.05)",
        color=TEXT_DIM,
        scaleanchor="x",
    ),
    plot_bgcolor=DARK_BG,
    paper_bgcolor=DARK_BG,
    font=dict(color="white"),
    hoverlabel=HOVER_LABEL,
    legend=dict(
        orientation="h", yanchor="bottom", y=-0.12,
        xanchor="right", x=0.98,
        font=dict(size=14, color=TEXT_WHITE),
        bgcolor="rgba(0,0,0,0)",
        itemsizing="constant",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    ),
    height=750,
    margin=dict(t=120, b=120),
)

# Annotations
fig.add_annotation(x=-1.5, y=4.3, text="Ump's left", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=1.5, y=4.3, text="Ump's right", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=0, y=0.1, text="Umpire's view (behind catcher)", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))

# Colorbar legend
fig.add_annotation(x=0.08, y=-0.1, xref="paper", yref="paper",
                   text="No strikes", showarrow=False, font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=0.25, y=-0.1, xref="paper", yref="paper",
                   text="Fringe", showarrow=False, font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=0.42, y=-0.1, xref="paper", yref="paper",
                   text="Core zone", showarrow=False, font=dict(size=10, color=TEXT_DIM))

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# AI Summary
# ---------------------------------------------------------------------------
if HAS_ANTHROPIC:
    summary_src = ump_team_all if len(ump_team_all) > 0 else df

    if len(summary_src) > 0:
        filter_key = f"{selected_umpire}_{selected_team}_{show_overturned}_{show_upheld}"
        if "ai_filter_key" not in st.session_state:
            st.session_state.ai_filter_key = ""
        if "ai_summary_text" not in st.session_state:
            st.session_state.ai_summary_text = ""
        if st.session_state.ai_filter_key != filter_key:
            st.session_state.ai_summary_text = ""
            st.session_state.ai_filter_key = filter_key

        if st.button("Generate AI Summary", key="ai_summary_btn", type="primary"):
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if not api_key or api_key == "your-key-here":
                st.warning("Add your ANTHROPIC_API_KEY to .env (local) or Streamlit secrets (cloud).")
            else:
                with st.spinner("Analyzing..."):
                    try:
                        prompt = build_summary_prompt(
                            summary_src, selected_umpire, selected_team,
                            league_avg, called_pitches_df,
                        )
                        result = get_ai_summary(prompt)
                        if result:
                            st.session_state.ai_summary_text = result
                        else:
                            st.warning("No summary returned. Check your API key.")
                    except Exception as e:
                        st.error(f"API error: {e}")

        if st.session_state.ai_summary_text:
            st.markdown(
                f'<div style="background-color:{CARD_BG}; padding:1rem 1.5rem; '
                f'border-radius:0.5rem; border-left:4px solid {ACCENT}; margin:0.5rem 0 1rem 0;">'
                f'<span style="color:{ACCENT}; font-weight:600; font-size:0.85rem;">AI ANALYSIS</span><br>'
                f'<span style="color:{TEXT_WHITE}; font-size:0.95rem; line-height:1.6;">'
                f'{st.session_state.ai_summary_text}</span></div>',
                unsafe_allow_html=True,
            )

st.markdown("---")

# ---------------------------------------------------------------------------
# Bottom section: table + chart
# ---------------------------------------------------------------------------
bottom_df = ump_team_all if len(ump_team_all) > 0 else df

if len(bottom_df) > 0:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Challenges by Original Call")
        by_call = (
            bottom_df[bottom_df["original_call"].notna() & (bottom_df["original_call"] != "")]
            .groupby("original_call")
            .agg(
                Challenges=("result", "size"),
                Overturned=("result", lambda x: (x == "overturned").sum()),
            )
            .reset_index()
        )
        by_call["Overturn %"] = (by_call["Overturned"] / by_call["Challenges"] * 100).round(1)
        by_call = by_call.sort_values("Challenges", ascending=False)
        by_call = by_call.rename(columns={"original_call": "Original Call"})
        st.dataframe(by_call, use_container_width=True, hide_index=True)

    with col_right:
        if single_umpire:
            st.subheader(f"{selected_umpire} - Challenge Results")

            pie_ot = (ump_team_all["result"] == "overturned").sum()
            pie_up = (ump_team_all["result"] == "upheld").sum()

            pie_fig = go.Figure(go.Pie(
                labels=["Overturned", "Upheld"],
                values=[pie_ot, pie_up],
                marker=dict(
                    colors=[OVERTURNED, UPHELD],
                    line=dict(color=DARK_BG, width=3),
                ),
                hole=0.45,
                textinfo="label+value+percent",
                textfont=dict(size=14, color=TEXT_WHITE),
                textposition="auto",
                pull=[0.06, 0],
                direction="clockwise",
                sort=False,
                hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
            ))
            pie_fig.add_annotation(
                text=f"<b>{pie_ot + pie_up}</b><br><span style='font-size:12px;color:{TEXT_DIM}'>total</span>",
                x=0.5, y=0.5, xref="paper", yref="paper",
                showarrow=False, font=dict(size=24, color=TEXT_WHITE),
            )
            pie_fig.update_layout(
                plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
                font=dict(color=TEXT_WHITE),
                hoverlabel=HOVER_LABEL,
                showlegend=False, height=350,
                margin=dict(l=40, r=40, t=20, b=40),
            )
            st.plotly_chart(pie_fig, use_container_width=True)

        else:
            st.subheader("Top Umpires by Challenge Count")

            ump_stats = (
                bottom_df.groupby("umpire")
                .agg(
                    challenges=("result", "size"),
                    overturned=("result", lambda x: (x == "overturned").sum()),
                )
                .reset_index()
            )
            ump_stats["overturn_rate"] = (
                ump_stats["overturned"] / ump_stats["challenges"] * 100
            ).round(1)
            ump_stats = ump_stats.sort_values("challenges", ascending=True).tail(15)

            bar_fig = go.Figure()
            bar_fig.add_trace(go.Bar(
                y=ump_stats["umpire"],
                x=ump_stats["overturned"],
                name="Overturned",
                orientation="h",
                marker=dict(color=OVERTURNED, line=dict(width=1, color=DARK_BG)),
                text=ump_stats["overturn_rate"].apply(lambda x: f"{x:.0f}%"),
                textposition="inside",
                textfont=dict(size=11, color="white"),
                hovertemplate="%{y}<br>Overturned: %{x}<br>Rate: %{text}<extra></extra>",
            ))
            bar_fig.add_trace(go.Bar(
                y=ump_stats["umpire"],
                x=ump_stats["challenges"] - ump_stats["overturned"],
                name="Upheld",
                orientation="h",
                marker=dict(color=UPHELD, line=dict(width=1, color=DARK_BG)),
                text=(ump_stats["challenges"] - ump_stats["overturned"]).astype(str),
                textposition="inside",
                textfont=dict(size=11, color="white"),
                hovertemplate="%{y}<br>Upheld: %{x}<extra></extra>",
            ))
            bar_fig.update_layout(
                barmode="stack",
                plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
                font=dict(color=TEXT_WHITE),
                hoverlabel=HOVER_LABEL,
                legend=dict(
                    orientation="h", yanchor="top", y=-0.25,
                    xanchor="center", x=0.5,
                    font=dict(size=12), bgcolor="rgba(0,0,0,0)",
                ),
                height=500,
                xaxis=dict(title="Challenges", gridcolor="rgba(255,255,255,0.05)", color=TEXT_DIM),
                yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color=TEXT_WHITE, automargin=True),
                margin=dict(l=10, r=10, t=10, b=80),
            )
            st.plotly_chart(bar_fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Rolling overturn rate (all umpires view)
# ---------------------------------------------------------------------------
if not single_umpire and len(bottom_df) >= 100:
    st.markdown("---")
    st.subheader("Rolling 100 Challenges - Overturn%")

    rolling_df = bottom_df.sort_values("date").reset_index(drop=True)
    rolling_df["is_overturned"] = (rolling_df["result"] == "overturned").astype(int)
    rolling_df["rolling_ot_pct"] = rolling_df["is_overturned"].rolling(100, min_periods=100).mean() * 100
    rolling_valid = rolling_df.dropna(subset=["rolling_ot_pct"])

    if len(rolling_valid) > 0:
        overall_ot_pct = rolling_df["is_overturned"].mean() * 100

        # One point per date (end-of-day value) to avoid vertical box artifacts
        daily = rolling_valid.groupby(rolling_valid["date"].dt.date)["rolling_ot_pct"].last().reset_index()
        daily.columns = ["date", "rolling_ot_pct"]

        roll_fig = go.Figure()
        roll_fig.add_trace(go.Scatter(
            x=daily["date"], y=daily["rolling_ot_pct"],
            mode="lines",
            line=dict(color=ACCENT, width=2.5, shape="spline", smoothing=1.0),
            name="Rolling 100",
            hovertemplate="%{x|%b %d}<br>Overturn rate: %{y:.1f}%<extra></extra>",
        ))
        roll_fig.add_hline(
            y=overall_ot_pct, line_dash="dot", line_color=TEXT_DIM,
            annotation_text=f"Overall: {overall_ot_pct:.1f}%",
            annotation_position="top right",
            annotation_font=dict(size=12, color=TEXT_DIM),
        )
        roll_fig.update_layout(
            plot_bgcolor=DARK_BG, paper_bgcolor=DARK_BG,
            font=dict(color=TEXT_WHITE),
            hoverlabel=HOVER_LABEL,
            hovermode="x unified",
            xaxis=dict(title="Date", gridcolor="rgba(255,255,255,0.05)", color=TEXT_DIM),
            yaxis=dict(
                title="Overturn %",
                gridcolor="rgba(255,255,255,0.05)", color=TEXT_DIM,
                range=[
                    max(0, rolling_valid["rolling_ot_pct"].min() - 5),
                    min(100, rolling_valid["rolling_ot_pct"].max() + 5),
                ],
            ),
            height=350,
            margin=dict(l=10, r=10, t=10, b=60),
            showlegend=False,
        )
        st.plotly_chart(roll_fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<p class="credit">@sabrmagician</p>', unsafe_allow_html=True)

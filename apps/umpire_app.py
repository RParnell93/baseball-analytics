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

def metric_card(label, value, subtext=None, delta=None, delta_color=None, donut=None, sparkline=None):
    """Render a custom metric card with subtext inside the box.

    donut: optional dict with keys 'overturned', 'upheld' to render a mini donut.
    sparkline: optional list of y-values to render as an SVG sparkline.
    """
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

    donut_html = ""
    if donut:
        ot = donut["overturned"]
        up = donut["upheld"]
        total = ot + up
        if total > 0:
            ot_pct = ot / total * 100
            up_pct = up / total * 100
            r = 22
            circ = 2 * 3.14159 * r
            ot_dash = circ * ot_pct / 100
            up_dash = circ * up_pct / 100
            donut_html = f"""
                <div style="display:flex; align-items:center; justify-content:center; gap:0.75rem; margin-top:0.35rem;">
                    <svg width="65" height="65" viewBox="0 0 65 65" style="flex-shrink:0;">
                        <circle cx="32.5" cy="32.5" r="{r}" fill="none" stroke="{UPHELD}" stroke-width="6"
                            stroke-dasharray="{up_dash:.1f} {circ:.1f}"
                            stroke-dashoffset="0" transform="rotate(-90 32.5 32.5)" opacity="0.85"/>
                        <circle cx="32.5" cy="32.5" r="{r}" fill="none" stroke="{OVERTURNED}" stroke-width="6"
                            stroke-dasharray="{ot_dash:.1f} {circ:.1f}"
                            stroke-dashoffset="-{up_dash:.1f}" transform="rotate(-90 32.5 32.5)" opacity="0.85"/>
                        <text x="32.5" y="31" text-anchor="middle" fill="{ACCENT}" font-size="15" font-weight="700" font-family="Montserrat,sans-serif">{total}</text>
                        <text x="32.5" y="41" text-anchor="middle" fill="{TEXT_DIM}" font-size="6" font-weight="600" font-family="Montserrat,sans-serif" letter-spacing="0.5">TOTAL</text>
                    </svg>
                    <div style="font-family:'Montserrat',sans-serif;">
                        <div style="display:flex; align-items:center; gap:0.25rem; margin-bottom:0.2rem;">
                            <span style="width:7px; height:7px; border-radius:50%; background:{OVERTURNED}; display:inline-block;"></span>
                            <span style="font-size:0.7rem; font-weight:700; color:{OVERTURNED};">{ot}</span>
                            <span style="font-size:0.65rem; font-weight:600; color:{TEXT_DIM};">OT</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:0.25rem;">
                            <span style="width:7px; height:7px; border-radius:50%; background:{UPHELD}; display:inline-block;"></span>
                            <span style="font-size:0.7rem; font-weight:700; color:{UPHELD};">{up}</span>
                            <span style="font-size:0.65rem; font-weight:600; color:{TEXT_DIM};">UH</span>
                        </div>
                    </div>
                </div>"""

    if donut_html:
        return (
            f'<div style="background-color:{CARD_BG}; padding:1rem 1.25rem; border-radius:0.5rem; overflow-wrap:break-word; margin-bottom:0.5rem;">'
            f'<div style="font-size:0.75rem; color:{TEXT_DIM}; font-family:\'Montserrat\',sans-serif; font-weight:800; letter-spacing:0.05em; text-transform:uppercase;">{label}</div>'
            f'{donut_html}'
            f'{sub_html}'
            f'</div>'
        )

    spark_html = ""
    if sparkline and len(sparkline) >= 2:
        w, h = 120, 32
        vals = sparkline
        y_min = min(vals) - 0.5
        y_max = max(vals) + 0.5
        y_range = y_max - y_min if y_max != y_min else 1
        avg_val = sum(vals) / len(vals)
        avg_y = h - (avg_val - y_min) / y_range * h
        points = " ".join(
            f"{i * w / (len(vals) - 1):.1f},{h - (v - y_min) / y_range * h:.1f}"
            for i, v in enumerate(vals)
        )
        spark_html = f"""<div style="margin-top:0.35rem;">
            <svg width="100%" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="display:block;">
                <line x1="0" y1="{avg_y:.1f}" x2="{w}" y2="{avg_y:.1f}" stroke="{TEXT_DIM}" stroke-width="0.5" stroke-dasharray="2,2" opacity="0.5"/>
                <polyline points="{points}" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
            </svg>
        </div>"""

    return (
        f'<div style="background-color:{CARD_BG}; padding:1rem 1.25rem; border-radius:0.5rem; overflow-wrap:break-word; margin-bottom:0.5rem;">'
        f'<div style="font-size:0.75rem; color:{TEXT_DIM}; font-family:\'Montserrat\',sans-serif; font-weight:800; letter-spacing:0.05em; text-transform:uppercase;">{label}</div>'
        f'<div style="font-size:clamp(1.3rem, 4vw, 2rem); font-weight:600; color:{ACCENT};">{value}</div>'
        f'{delta_html}{sub_html}{spark_html}'
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

    scope_desc = ""
    if ump != "All Umpires" and team != "All Teams":
        scope_desc = f"Umpire: {ump} (the home plate umpire whose calls are being challenged by teams). Filtered to challenges from {team}."
    elif ump != "All Umpires":
        scope_desc = f"Umpire: {ump} (the home plate umpire whose ball/strike calls are being challenged by batting teams). All teams included."
    elif team != "All Teams":
        scope_desc = f"Team: {team} (the batting team initiating challenges against umpires). All umpires included."
    else:
        scope_desc = "All umpires and all teams (league-wide view)."

    return f"""You are a baseball analytics expert providing a broadcast-ready summary for a radio color commentator. Analyze this ABS (Automated Ball-Strike) challenge data from Spring Training 2026.

IMPORTANT CONTEXT: In ABS, the BATTING TEAM challenges the HOME PLATE UMPIRE's ball/strike call. When a challenge is "overturned", the umpire's original call was wrong. A high overturn rate means the umpire is making more incorrect calls. A low overturn rate means the umpire's calls are holding up well.

Scope: {scope_desc}
Total challenges against this umpire: {n}
Overturned (umpire was wrong): {n_ot} ({ot_rate:.1f}%)
Upheld (umpire was correct): {n_up} ({100-ot_rate:.1f}%)
Avg impact score: {avg_imp:.1f}
MLB avg overturn rate: {league_avgs['overturn_pct']:.1f}%
MLB avg impact: {league_avgs['avg_impact']:.1f}

Breakdown by original call (what the umpire called before the challenge):
{call_breakdown}
Top pitch types challenged:
{pitch_breakdown}
Zone location analysis:
{zone_analysis}
Impact distribution:
{impact_info}
Umpire's established zone (from all called pitches):
{zone_info}

Write a 3-4 sentence analyst summary. Be specific with numbers. Note anything unusual - is the overturn rate above or below average? Are challenges clustered in a certain zone? Which pitch types cause the most trouble? If viewing a specific umpire, comment on their zone tendencies and accuracy. Remember: the umpire is the one being evaluated, not the one challenging. Keep the tone sharp and informative, like you're briefing a broadcast booth before a game. No filler, no fluff."""


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
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet">
<style>
    .brand-title {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: clamp(1.6rem, 5vw, 2.2rem);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: {TEXT_WHITE} !important;
        margin-bottom: 0.1rem;
    }}
    .brand-subtitle {{
        font-size: 0.85rem;
        color: {TEXT_DIM} !important;
        margin-bottom: 0.75rem;
    }}
    .section-header {{
        font-family: 'Montserrat', sans-serif;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {TEXT_DIM} !important;
        margin-bottom: 0.5rem;
    }}
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
    [data-testid="stSubheader"] {{
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: 0.06em !important;
        font-size: 1rem !important;
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

    /* Section spacing */
    hr {{
        margin: 1.5rem 0 !important;
    }}
    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: 0.25rem;
    }}

    /* Equal height columns - cascade height through all Streamlit wrappers */
    div[data-testid="stHorizontalBlock"] {{
        align-items: stretch !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div > div,
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div > div > div > div {{
        height: 100% !important;
    }}

    /* Subtle AI summary button */
    button[data-testid="stBaseButton-secondary"] {{
        background-color: {CARD_BG} !important;
        color: {TEXT_DIM} !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }}
    button[data-testid="stBaseButton-secondary"]:hover {{
        background-color: rgba(34,209,238,0.1) !important;
        color: {ACCENT} !important;
        border-color: {ACCENT} !important;
    }}

    /* Pills styling */
    [data-testid="stPills"] button {{
        font-size: 0.8rem !important;
    }}

    /* Mobile optimizations */
    @media (max-width: 768px) {{
        .stMainBlockContainer {{
            padding: 1rem 0.5rem;
        }}
        h1 {{ font-size: 1.5rem !important; }}
        h2 {{ font-size: 1.1rem !important; }}
        .brand-title {{ font-size: 1.6rem !important; }}
        .stButton button {{
            min-height: 44px;
            font-size: 0.85rem;
        }}
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
_logo_svg = """
<svg width="44" height="44" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Umpire mask outline -->
  <rect x="4" y="6" width="28" height="22" rx="8" stroke="#22D1EE" stroke-width="2" fill="none"/>
  <!-- Mask bars -->
  <line x1="4" y1="14" x2="32" y2="14" stroke="#22D1EE" stroke-width="1.5" opacity="0.6"/>
  <line x1="4" y1="21" x2="32" y2="21" stroke="#22D1EE" stroke-width="1.5" opacity="0.6"/>
  <!-- Data bars (mini chart inside mask) -->
  <rect x="10" y="23" width="3" height="3" rx="0.5" fill="#ff6b6b" opacity="0.8"/>
  <rect x="15" y="19" width="3" height="7" rx="0.5" fill="#51cf66" opacity="0.8"/>
  <rect x="20" y="16" width="3" height="10" rx="0.5" fill="#22D1EE" opacity="0.8"/>
  <rect x="25" y="21" width="3" height="5" rx="0.5" fill="#ff6b6b" opacity="0.8"/>
</svg>
"""

st.markdown(
    f'<div>'
    f'<div style="display:flex; align-items:center; gap:0.6rem;">'
    f'<div style="flex-shrink:0; line-height:0;">{_logo_svg}</div>'
    f'<div class="brand-title" style="line-height:1;">UMP STATS</div>'
    f'</div>'
    f'<div class="brand-subtitle" style="margin-left:54px;">🌴 Spring Training 2026</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1, 1])

with col_f1:
    selected_umpire = st.selectbox("🔍 Umpire", ["All Umpires"] + all_umpires)

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

# Result filter - native pills
with col_f4:
    selected_results = st.pills(
        "Result",
        options=["🔴 Overturned", "🟢 Upheld"],
        default=["🔴 Overturned", "🟢 Upheld"],
        selection_mode="multi",
    )

show_overturned = "🔴 Overturned" in selected_results
show_upheld = "🟢 Upheld" in selected_results

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
    upheld_rate = ump_up / max(ump_n, 1) * 100
    upheld_delta = upheld_rate - league_avg["upheld_pct"]
    ump_avg_impact = ump_team_all["impact_score"].mean() if ump_n > 0 else 0
    impact_delta = ump_avg_impact - league_avg["avg_impact"]
    ump_games = df[df["umpire"] == selected_umpire]["game_id"].nunique()

    ump_called = 0
    if called_pitches_df is not None:
        ump_called = len(called_pitches_df[called_pitches_df["umpire"] == selected_umpire])
    challenge_pct = ump_n / max(ump_called, 1) * 100

    games_sub = f"{ump_called:,} Called Pitches"

    # Umpire accuracy: how many called pitches were correct (not overturned)
    # Overall accuracy = (called pitches - overturned challenges) / called pitches
    if ump_called > 0:
        overall_accuracy = (ump_called - ump_ot) / ump_called * 100
    else:
        overall_accuracy = 0

    # League avg accuracy for delta
    league_total_called = len(called_pitches_df) if called_pitches_df is not None else 0
    league_total_ot = (df["result"] == "overturned").sum()
    league_accuracy = (league_total_called - league_total_ot) / max(league_total_called, 1) * 100
    accuracy_delta = overall_accuracy - league_accuracy

    # Compute rolling 100-pitch accuracy sparkline
    acc_sparkline = None
    if called_pitches_df is not None:
        _ump_cp = called_pitches_df[called_pitches_df["umpire"] == selected_umpire].copy()
        _ump_cp = _ump_cp.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"])
        if len(_ump_cp) >= 100:
            _ump_cp = _ump_cp.sort_values("date").reset_index(drop=True)
            _in_zone = (
                (_ump_cp["pX"].abs() <= PLATE_HALF_FT)
                & (_ump_cp["pZ"] >= _ump_cp["sz_bottom"])
                & (_ump_cp["pZ"] <= _ump_cp["sz_top"])
            )
            _ump_cp["_correct"] = (
                ((_ump_cp["call"] == "Called Strike") & _in_zone)
                | ((_ump_cp["call"] == "Ball") & ~_in_zone)
            ).astype(int)
            _rolling = _ump_cp["_correct"].rolling(100, min_periods=100).mean() * 100
            _valid = _rolling.dropna()
            if len(_valid) > 0:
                # Sample ~30 points for a clean sparkline
                step = max(1, len(_valid) // 30)
                acc_sparkline = _valid.iloc[::step].tolist()

    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
    col_m1.markdown(metric_card("Games", f"{ump_games:,}", subtext=games_sub), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Challenges", f"{ump_n:,}", subtext=f"{challenge_pct:.1f}% of Called Pitches", donut={"overturned": ump_ot, "upheld": ump_up}), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Upheld Rate", f"{upheld_rate:.0f}%", delta=f"{upheld_delta:+.1f}pp vs avg", delta_color="normal"), unsafe_allow_html=True)
    col_m4.markdown(metric_card("Accuracy", f"{overall_accuracy:.1f}%", delta=f"{accuracy_delta:+.1f}pp vs avg", delta_color="normal", sparkline=acc_sparkline), unsafe_allow_html=True)
    col_m5.markdown(metric_card("Avg Impact", f"{ump_avg_impact:.1f}", delta=f"{impact_delta:+.1f} vs avg"), unsafe_allow_html=True)
else:
    all_games = df["game_id"].nunique()
    all_n = len(ump_team_all)
    all_ot = (ump_team_all["result"] == "overturned").sum()
    all_up = all_n - all_ot
    all_ot_pct = all_ot / max(all_n, 1) * 100
    challenge_pct = all_n / max(total_called, 1) * 100

    games_sub = f"{total_called:,} Called Pitches"

    all_up_pct = 100 - all_ot_pct

    # League-wide accuracy
    if total_called > 0:
        league_overall_accuracy = (total_called - all_ot) / total_called * 100
    else:
        league_overall_accuracy = 0

    col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
    col_m1.markdown(metric_card("Games", f"{all_games:,}", subtext=games_sub), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Challenges", f"{all_n:,}", subtext=f"{challenge_pct:.1f}% of Called Pitches", donut={"overturned": all_ot, "upheld": all_up}), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Overturn Rate", f"{all_ot_pct:.0f}%", subtext=f"{all_ot:,} Overturned"), unsafe_allow_html=True)
    col_m4.markdown(metric_card("Upheld Rate", f"{all_up_pct:.0f}%", subtext=f"{all_up:,} Upheld"), unsafe_allow_html=True)
    col_m5.markdown(metric_card("Accuracy", f"{league_overall_accuracy:.1f}%"), unsafe_allow_html=True)
    col_m6.markdown(metric_card("Avg Impact", f"{ump_team_all['impact_score'].mean():.1f}" if all_n > 0 else "0"), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Percentile Sliders (single umpire only, unfiltered by team)
# ---------------------------------------------------------------------------
if single_umpire and called_pitches_df is not None:
    # Compute stats for ALL umpires (ignoring team/date filters)
    # Called pitches by umpire, split by call type
    cp_by_ump = called_pitches_df.groupby(["umpire", "call"]).size().unstack(fill_value=0).reset_index()
    if "Called Strike" not in cp_by_ump.columns:
        cp_by_ump["Called Strike"] = 0
    if "Ball" not in cp_by_ump.columns:
        cp_by_ump["Ball"] = 0
    cp_by_ump["called_pitches"] = cp_by_ump["Called Strike"] + cp_by_ump["Ball"]
    cp_by_ump = cp_by_ump.rename(columns={"Called Strike": "called_strikes", "Ball": "called_balls"})

    # Challenges by umpire, split by original call
    ch_by_ump = df.groupby("umpire").agg(
        challenges=("result", "size"),
        overturned=("result", lambda x: (x == "overturned").sum()),
    ).reset_index()

    # Strike/ball overturns
    strike_ot = df[df["original_call"] == "Called Strike"].groupby("umpire").agg(
        strike_overturned=("result", lambda x: (x == "overturned").sum()),
    ).reset_index()
    ball_ot = df[df["original_call"] == "Ball"].groupby("umpire").agg(
        ball_overturned=("result", lambda x: (x == "overturned").sum()),
    ).reset_index()

    all_ump = ch_by_ump.merge(cp_by_ump[["umpire", "called_pitches", "called_strikes", "called_balls"]], on="umpire", how="inner")
    all_ump = all_ump.merge(strike_ot, on="umpire", how="left").fillna(0)
    all_ump = all_ump.merge(ball_ot, on="umpire", how="left").fillna(0)
    all_ump = all_ump[all_ump["challenges"] >= 5]

    # Metrics
    all_ump["total_accuracy"] = (all_ump["called_pitches"] - all_ump["overturned"]) / all_ump["called_pitches"] * 100
    all_ump["strike_accuracy"] = (all_ump["called_strikes"] - all_ump["strike_overturned"]) / all_ump["called_strikes"].clip(lower=1) * 100
    all_ump["ball_accuracy"] = (all_ump["called_balls"] - all_ump["ball_overturned"]) / all_ump["called_balls"].clip(lower=1) * 100
    all_ump["challenge_pct"] = all_ump["challenges"] / all_ump["called_pitches"] * 100
    all_ump["overturn_rate"] = all_ump["overturned"] / all_ump["challenges"] * 100

    ump_row = all_ump[all_ump["umpire"] == selected_umpire]
    if len(ump_row) > 0:
        ump_row = ump_row.iloc[0]

        def percentile_of(series, value):
            return (series < value).sum() / len(series) * 100

        def percentile_of_inverse(series, value):
            """Higher percentile = better, but for metrics where LOWER value = better."""
            return (series > value).sum() / len(series) * 100

        # Higher percentile = better for all sliders
        metrics = [
            ("Total Accuracy", ump_row["total_accuracy"], f"{ump_row['total_accuracy']:.1f}%",
             percentile_of(all_ump["total_accuracy"], ump_row["total_accuracy"])),
            ("Strike Accuracy", ump_row["strike_accuracy"], f"{ump_row['strike_accuracy']:.1f}%",
             percentile_of(all_ump["strike_accuracy"], ump_row["strike_accuracy"])),
            ("Ball Accuracy", ump_row["ball_accuracy"], f"{ump_row['ball_accuracy']:.1f}%",
             percentile_of(all_ump["ball_accuracy"], ump_row["ball_accuracy"])),
            ("Challenge %", ump_row["challenge_pct"], f"{ump_row['challenge_pct']:.1f}%",
             percentile_of_inverse(all_ump["challenge_pct"], ump_row["challenge_pct"])),
            ("Overturns", ump_row["overturn_rate"], f"{ump_row['overturn_rate']:.0f}%",
             percentile_of_inverse(all_ump["overturn_rate"], ump_row["overturn_rate"])),
        ]

        def pct_color(pct):
            """Smooth gradient: dark navy (0) -> steel blue (30) -> light blue (50) -> light red (70) -> deep red (100)."""
            pct = max(0, min(100, pct))
            if pct <= 50:
                # Blue side: dark navy (0) -> light steel blue (50)
                t = pct / 50  # 0..1
                r = int(21 + t * (80 - 21))     # 21 -> 80
                g = int(67 + t * (140 - 67))    # 67 -> 140
                b = int(120 + t * (190 - 120))  # 120 -> 190
            else:
                # Red side: light red (50) -> deep red (100)
                t = (pct - 50) / 50  # 0..1
                r = int(160 + t * (183 - 160))  # 160 -> 183
                g = int(100 - t * (72))          # 100 -> 28
                b = int(100 - t * (72))          # 100 -> 28
            return f"rgb({r},{g},{b})"

        slider_html = f'<div style="background:{CARD_BG}; border-radius:0.5rem; padding:1.25rem 1.25rem; margin-bottom:0.75rem; height:100%; box-sizing:border-box; display:flex; flex-direction:column;">'
        slider_html += f'<div class="section-header">Umpire Percentile Rankings</div>'
        slider_html += f'<div style="flex:1; display:flex; flex-direction:column; justify-content:space-evenly;">'

        for label, val, display, pct in metrics:
            color = pct_color(pct)
            pct_int = int(round(pct))
            bar_width = max(pct_int, 2)
            circle_left = f"calc({bar_width}% - 14px)" if bar_width > 5 else "0px"
            slider_html += f"""
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <div style="width:120px; font-size:0.7rem; color:{TEXT_DIM}; text-align:right; flex-shrink:0; font-family:'Montserrat',sans-serif; font-weight:800; letter-spacing:0.03em; text-transform:uppercase;">{label}</div>
                <div style="flex:1; background:rgba(255,255,255,0.06); border-radius:4px; height:10px; position:relative;">
                    <div style="width:{bar_width}%; height:100%; background:{color}; border-radius:4px;"></div>
                    <div style="position:absolute; top:50%; left:{circle_left}; transform:translateY(-50%); width:28px; height:28px; border-radius:50%; background:{color}; display:flex; align-items:center; justify-content:center; border:2px solid {CARD_BG}; box-shadow:0 0 0 1px rgba(255,255,255,0.1);">
                        <span style="font-size:0.65rem; font-weight:700; color:{TEXT_WHITE};">{pct_int}</span>
                    </div>
                </div>
                <div style="width:55px; font-size:0.75rem; color:{TEXT_WHITE}; flex-shrink:0; text-align:right;">{display}</div>
            </div>"""

        slider_html += '</div></div>'
        # Store for side-by-side rendering below
        st.session_state["_slider_html"] = slider_html

    # --- Pitch Type Breakdown Table (umpire-only, no team filter) ---
    ump_all = df[df["umpire"] == selected_umpire]
    if "pitch_name" in ump_all.columns and len(ump_all) > 0:
        ump_pt = ump_all[ump_all["pitch_name"].notna() & (ump_all["pitch_name"] != "")]
        league_pt = df[df["pitch_name"].notna() & (df["pitch_name"] != "")]

        if len(ump_pt) > 0:
            # Total called pitches by pitch type for this umpire
            ump_cp = called_pitches_df[called_pitches_df["umpire"] == selected_umpire] if called_pitches_df is not None else pd.DataFrame()
            cp_by_pitch = pd.DataFrame()
            if len(ump_cp) > 0 and "pitch_name" in ump_cp.columns:
                cp_by_pitch = ump_cp[ump_cp["pitch_name"].notna() & (ump_cp["pitch_name"] != "")].groupby("pitch_name").size().reset_index(name="total_pitches")

            # Umpire stats by pitch type with strike/ball split
            ump_by_pitch = ump_pt.groupby("pitch_name").agg(
                challenges=("result", "size"),
                overturned=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()

            # Strike/ball challenge accuracy per pitch type
            strike_ch = ump_pt[ump_pt["original_call"] == "Called Strike"].groupby("pitch_name").agg(
                strike_challenges=("result", "size"),
                strike_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()
            ball_ch = ump_pt[ump_pt["original_call"] == "Ball"].groupby("pitch_name").agg(
                ball_challenges=("result", "size"),
                ball_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()

            ump_by_pitch = ump_by_pitch.merge(strike_ch, on="pitch_name", how="left").fillna(0)
            ump_by_pitch = ump_by_pitch.merge(ball_ch, on="pitch_name", how="left").fillna(0)
            if len(cp_by_pitch) > 0:
                ump_by_pitch = ump_by_pitch.merge(cp_by_pitch, on="pitch_name", how="left").fillna(0)
            else:
                ump_by_pitch["total_pitches"] = 0

            ump_by_pitch["challenge_pct"] = (ump_by_pitch["challenges"] / ump_by_pitch["challenges"].sum() * 100).round(1)
            ump_by_pitch["ot_rate"] = (ump_by_pitch["overturned"] / ump_by_pitch["challenges"] * 100).round(1)
            ump_by_pitch["total_acc"] = ((ump_by_pitch["total_pitches"] - ump_by_pitch["overturned"]) / ump_by_pitch["total_pitches"].clip(lower=1) * 100).round(1)
            ump_by_pitch["strike_acc"] = ((ump_by_pitch["strike_challenges"] - ump_by_pitch["strike_ot"]) / ump_by_pitch["strike_challenges"].clip(lower=1) * 100).round(1)
            ump_by_pitch["ball_acc"] = ((ump_by_pitch["ball_challenges"] - ump_by_pitch["ball_ot"]) / ump_by_pitch["ball_challenges"].clip(lower=1) * 100).round(1)

            # League averages
            lg_by_pitch = league_pt.groupby("pitch_name").agg(
                lg_ch=("result", "size"),
                lg_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()
            lg_strike = league_pt[league_pt["original_call"] == "Called Strike"].groupby("pitch_name").agg(
                lg_s_ch=("result", "size"), lg_s_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()
            lg_ball = league_pt[league_pt["original_call"] == "Ball"].groupby("pitch_name").agg(
                lg_b_ch=("result", "size"), lg_b_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()

            lg_by_pitch = lg_by_pitch.merge(lg_strike, on="pitch_name", how="left").fillna(0)
            lg_by_pitch = lg_by_pitch.merge(lg_ball, on="pitch_name", how="left").fillna(0)
            lg_by_pitch["lg_ot_rate"] = (lg_by_pitch["lg_ot"] / lg_by_pitch["lg_ch"] * 100).round(1)
            lg_by_pitch["lg_strike_acc"] = ((lg_by_pitch["lg_s_ch"] - lg_by_pitch["lg_s_ot"]) / lg_by_pitch["lg_s_ch"].clip(lower=1) * 100).round(1)
            lg_by_pitch["lg_ball_acc"] = ((lg_by_pitch["lg_b_ch"] - lg_by_pitch["lg_b_ot"]) / lg_by_pitch["lg_b_ch"].clip(lower=1) * 100).round(1)

            # League total accuracy per pitch type (from called pitches)
            if called_pitches_df is not None and "pitch_name" in called_pitches_df.columns:
                lg_cp_by_pitch = called_pitches_df[called_pitches_df["pitch_name"].notna() & (called_pitches_df["pitch_name"] != "")].groupby("pitch_name").size().reset_index(name="lg_total_pitches")
                lg_by_pitch = lg_by_pitch.merge(lg_cp_by_pitch, on="pitch_name", how="left").fillna(0)
                lg_by_pitch["lg_total_acc"] = ((lg_by_pitch["lg_total_pitches"] - lg_by_pitch["lg_ot"]) / lg_by_pitch["lg_total_pitches"].clip(lower=1) * 100).round(1)
            else:
                lg_by_pitch["lg_total_acc"] = 0

            merged = ump_by_pitch.merge(lg_by_pitch[["pitch_name", "lg_ot_rate", "lg_strike_acc", "lg_ball_acc", "lg_total_acc"]], on="pitch_name", how="left")
            merged = merged.sort_values("total_pitches", ascending=False)

            def cell_color_spectrum(val, lg_val, higher_is_better=True, threshold=1.0):
                """Spectrum color: deep red (much better) -> light red -> neutral -> light blue -> deep blue (much worse)."""
                diff = val - lg_val
                if not higher_is_better:
                    diff = -diff
                if abs(diff) < threshold:
                    return f"background:transparent; color:{TEXT_WHITE}"
                # Clamp to [-20, 20] so colors saturate faster and look uniform
                clamped = max(-20, min(20, diff))
                intensity = abs(clamped) / 20  # 0 to 1
                if clamped > 0:
                    # Better: red spectrum
                    alpha = 0.18 + intensity * 0.27  # 0.18 to 0.45
                    return f"background:rgba(180,50,40,{alpha:.2f}); color:rgb({int(220 + intensity * 35)},{int(100 - intensity * 40)},{int(80 - intensity * 30)})"
                else:
                    # Worse: blue spectrum
                    alpha = 0.18 + intensity * 0.27
                    return f"background:rgba(40,90,160,{alpha:.2f}); color:rgb({int(100 + intensity * 50)},{int(170 + intensity * 30)},{int(220 + intensity * 35)})"

            _th = f"text-align:center; padding:0.5rem 0.75rem; color:{TEXT_DIM}; font-family:'Montserrat',sans-serif; font-weight:800; font-size:0.7rem; letter-spacing:0.05em; text-transform:uppercase;"
            _td = f"text-align:center; padding:0.45rem 0.75rem; color:{TEXT_WHITE};"
            has_total = ump_by_pitch["total_pitches"].sum() > 0
            table_html = f"""
            <div style="background:{CARD_BG}; border-radius:0.5rem; padding:1.25rem 1.25rem; margin-bottom:0.75rem; overflow-x:auto; -webkit-overflow-scrolling:touch; height:100%; box-sizing:border-box;">
                <div class="section-header">Pitch Type Breakdown</div>
                <table style="width:100%; border-collapse:collapse; font-size:0.8rem;">
                    <thead>
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.1);">
                            <th style="text-align:left; padding:0.5rem 0.75rem; color:{TEXT_DIM}; font-family:'Montserrat',sans-serif; font-weight:800; font-size:0.7rem; letter-spacing:0.05em; text-transform:uppercase;">Pitch</th>
                            {"<th style='" + _th + "'>PITCHES</th>" if has_total else ""}
                            <th style="{_th}">Challenges</th>
                            <th style="{_th}">OT Rate</th>
                            <th style="{_th}">Accuracy</th>
                            <th style="{_th}">Strike Acc.</th>
                            <th style="{_th}">Ball Acc.</th>
                        </tr>
                    </thead>
                    <tbody>"""

            for _, row in merged.iterrows():
                ot_style = cell_color_spectrum(row["ot_rate"], row.get("lg_ot_rate", 50), higher_is_better=False, threshold=0.5)
                ta_style = cell_color_spectrum(row["total_acc"], row.get("lg_total_acc", 99), higher_is_better=True, threshold=0.1) if row["total_pitches"] > 0 else f"background:transparent; color:{TEXT_DIM}"
                sa_style = cell_color_spectrum(row["strike_acc"], row.get("lg_strike_acc", 50), higher_is_better=True, threshold=0.5) if row["strike_challenges"] > 0 else f"background:transparent; color:{TEXT_DIM}"
                ba_style = cell_color_spectrum(row["ball_acc"], row.get("lg_ball_acc", 50), higher_is_better=True, threshold=0.5) if row["ball_challenges"] > 0 else f"background:transparent; color:{TEXT_DIM}"
                ta_val = f"{row['total_acc']:.1f}%" if row["total_pitches"] > 0 else "-"
                sa_val = f"{row['strike_acc']:.0f}%" if row["strike_challenges"] > 0 else "-"
                ba_val = f"{row['ball_acc']:.0f}%" if row["ball_challenges"] > 0 else "-"
                tp_val = f"{int(row['total_pitches']):,}" if row["total_pitches"] > 0 else "-"
                table_html += f"""
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                            <td style="padding:0.45rem 0.75rem; color:{TEXT_WHITE};">{row['pitch_name']}</td>
                            {"<td style='" + _td + "'>" + tp_val + "</td>" if has_total else ""}
                            <td style="{_td}">{int(row['challenges'])}</td>
                            <td style="{_td} border-radius:3px; {ot_style};">{row['ot_rate']:.0f}%</td>
                            <td style="{_td} border-radius:3px; {ta_style};">{ta_val}</td>
                            <td style="{_td} border-radius:3px; {sa_style};">{sa_val}</td>
                            <td style="{_td} border-radius:3px; {ba_style};">{ba_val}</td>
                        </tr>"""

            table_html += f"""
                    </tbody>
                </table>
                <div style="font-size:0.65rem; color:{TEXT_DIM}; margin-top:0.4rem;">Red = better than league avg | Blue = worse | Strike/Ball Acc. = % of challenged calls upheld by ABS</div>
            </div>"""
            st.session_state["_table_html"] = table_html

    # Render sliders and table side by side in a single HTML block (CSS grid for equal height)
    _s_html = st.session_state.get("_slider_html", "")
    _t_html = st.session_state.get("_table_html", "")
    if _s_html or _t_html:
        if _s_html and _t_html:
            combined = f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; align-items:stretch;">
                {_s_html}
                {_t_html}
            </div>"""
            st.markdown(combined, unsafe_allow_html=True)
        elif _s_html:
            st.markdown(_s_html, unsafe_allow_html=True)
        else:
            st.markdown(_t_html, unsafe_allow_html=True)
    # Clean up
    st.session_state.pop("_slider_html", None)
    st.session_state.pop("_table_html", None)

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
        zone_source_label = f"{selected_umpire}'s zone ({len(zone_strikes)} called pitches)"
    elif selected_team != "All Teams" and has_team_col:
        zone_strikes = all_strikes[all_strikes["batting_team"] == selected_team]
        zone_source_label = f"{selected_team} batting zone ({len(zone_strikes)} called pitches)"
    else:
        zone_strikes = all_strikes
        zone_source_label = f"MLB avg zone ({len(zone_strikes):,} called pitches)"

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
                    y=-0.17, yanchor="top", x=0.5, xanchor="center",
                    len=0.45, thickness=10, tickvals=[], ticktext=[],
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
    # Scale markers: smaller when many dots, larger when few
    n_dots = len(valid)
    if n_dots > 500:
        dot_size, dot_text_size, dot_opacity = 8, 0, 0.6
        dot_mode = "markers"
    elif n_dots > 200:
        dot_size, dot_text_size, dot_opacity = 10, 0, 0.65
        dot_mode = "markers"
    elif n_dots > 50:
        dot_size, dot_text_size, dot_opacity = 13, 6, 0.7
        dot_mode = "markers+text"
    else:
        dot_size, dot_text_size, dot_opacity = 16, 7, 0.75
        dot_mode = "markers+text"

    for result_val, color, marker_symbol, label_prefix in [
        ("overturned", OVERTURNED, "circle", "Overturned"),
        ("upheld", UPHELD, "circle", "Upheld"),
    ]:
        subset = valid[valid["result"] == result_val]
        if len(subset) == 0:
            continue

        fig.add_trace(go.Scatter(
            x=subset["pX"], y=subset["pZ"],
            mode=dot_mode,
            marker=dict(
                size=dot_size, color=color, opacity=dot_opacity, symbol=marker_symbol,
                line=dict(width=1 if n_dots > 200 else 2, color=TEXT_WHITE),
            ),
            text=subset["challenge_team"] if dot_text_size > 0 else None,
            textfont=dict(size=dot_text_size if dot_text_size > 0 else 7, color=TEXT_WHITE),
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

fig.update_layout(
    title=dict(
        text=f"{title_line1}<br>{title_line2}",
        font=dict(size=22, color=TEXT_WHITE),
        x=0.5, xanchor="center",
    ),
    xaxis=dict(
        title="Horizontal Location (ft from center)",
        range=[-2, 2], autorange=False, fixedrange=True,
        zeroline=False,
        gridcolor="rgba(255,255,255,0.05)",
        color=TEXT_DIM,
        constrain="domain",
    ),
    yaxis=dict(
        title="Vertical Location (ft)",
        range=[0, 4.5], autorange=False, fixedrange=True,
        zeroline=False,
        gridcolor="rgba(255,255,255,0.05)",
        color=TEXT_DIM,
        scaleanchor="x",
        constrain="domain",
    ),
    plot_bgcolor=DARK_BG,
    paper_bgcolor=DARK_BG,
    font=dict(color=TEXT_WHITE),
    hoverlabel=HOVER_LABEL,
    legend=dict(
        orientation="h", yanchor="top", y=-0.23,
        xanchor="center", x=0.5,
        font=dict(size=11, color=TEXT_WHITE),
        bgcolor="rgba(0,0,0,0)",
        itemsizing="constant",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    ),
    height=620,
    margin=dict(t=90, b=160),
)

# Annotations
fig.add_annotation(x=-1.5, y=4.3, text="Ump's left", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=1.5, y=4.3, text="Ump's right", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=0, y=0.1, text="Umpire's view (behind catcher)", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))

# Colorbar legend (aligned with bar at x=0.5, len=0.45 -> spans 0.275 to 0.725)
fig.add_annotation(x=0.28, y=-0.19, xref="paper", yref="paper",
                   text="No strikes", showarrow=False, font=dict(size=9, color=TEXT_DIM))
fig.add_annotation(x=0.5, y=-0.19, xref="paper", yref="paper",
                   text="Fringe", showarrow=False, font=dict(size=9, color=TEXT_DIM))
fig.add_annotation(x=0.72, y=-0.19, xref="paper", yref="paper",
                   text="Core zone", showarrow=False, font=dict(size=9, color=TEXT_DIM))

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}

# Side-by-side: challenge map (left) + worst calls (right) for single umpire
if single_umpire and "zone_dist" in valid.columns and len(valid) > 0:
    _map_col, _worst_col = st.columns([3, 1])
    with _map_col:
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)
    with _worst_col:
        _ot_valid = valid[valid["result"] == "overturned"].copy() if "result" in valid.columns else valid.copy()
        if len(_ot_valid) == 0:
            _ot_valid = valid.copy()
        _worst = _ot_valid.nlargest(5, "zone_dist")
        _th_style = f"padding:0.4rem 0.5rem; color:{TEXT_DIM}; font-family:'Montserrat',sans-serif; font-weight:800; font-size:0.6rem; letter-spacing:0.03em; text-transform:uppercase; text-align:left;"
        _td_style = f"padding:0.35rem 0.5rem; color:{TEXT_WHITE}; font-size:0.75rem; border-bottom:1px solid rgba(255,255,255,0.05);"
        _worst_html = f"""
        <div style="background:{CARD_BG}; border-radius:0.5rem; padding:1rem; height:100%; box-sizing:border-box;">
            <div class="section-header" style="margin-bottom:0.5rem; font-size:0.85rem;">Worst Calls</div>
            <div style="font-size:0.65rem; color:{TEXT_DIM}; margin-bottom:0.5rem;">By distance from zone edge</div>
            <table style="width:100%; border-collapse:collapse;">
                <thead>
                    <tr>
                        <th style="{_th_style}">Call</th>
                        <th style="{_th_style}">Pitch</th>
                        <th style="{_th_style} text-align:right;">Dist</th>
                    </tr>
                </thead>
                <tbody>"""
        for _, _row in _worst.iterrows():
            _call = _row.get("original_call", "")
            _call_short = "STK" if "trike" in str(_call) else "BALL"
            _call_color = OVERTURNED if _row.get("result", "") == "overturned" else UPHELD
            _pitch = _row.get("pitch_name", _row.get("pitch_type", ""))
            _dist_in = abs(_row["zone_dist"]) * 12
            _team = _row.get("batting_team", "")
            _worst_html += f"""
                    <tr>
                        <td style="{_td_style}"><span style="color:{_call_color}; font-weight:700;">{_call_short}</span> <span style="color:{TEXT_DIM}; font-size:0.6rem;">{_team}</span></td>
                        <td style="{_td_style} font-size:0.65rem;">{_pitch}</td>
                        <td style="{_td_style} text-align:right; font-weight:700; color:{OVERTURNED};">{_dist_in:.1f}in</td>
                    </tr>"""
        _worst_html += """
                </tbody>
            </table>
        </div>"""
        st.markdown(_worst_html, unsafe_allow_html=True)
else:
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

# ---------------------------------------------------------------------------
# AI Summary Section
# ---------------------------------------------------------------------------
st.markdown("---")
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

        st.markdown(f'<div class="section-header" style="margin-bottom:0.5rem;">AI Analysis</div>', unsafe_allow_html=True)
        st.markdown(
            '<style>.ai-gen-btn button { background-color: #4fc3f7 !important; color: #0a0a1a !important; '
            'font-weight: 700 !important; font-family: "Montserrat", sans-serif !important; '
            'letter-spacing: 0.05em !important; text-transform: uppercase !important; '
            'font-size: 0.8rem !important; padding: 0.3rem 1.2rem !important; border: none !important; }</style>',
            unsafe_allow_html=True,
        )
        with st.container():
            st.markdown('<div class="ai-gen-btn">', unsafe_allow_html=True)
            _gen_btn = st.button("Generate", key="ai_summary_btn", type="secondary")
            st.markdown('</div>', unsafe_allow_html=True)

        if _gen_btn:
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
                f'border-radius:0.5rem; border-left:4px solid {ACCENT}; margin:0.75rem 0 1rem 0;">'
                f'<span style="color:{TEXT_WHITE}; font-size:0.95rem; line-height:1.6;">'
                f'{st.session_state.ai_summary_text}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="color:{TEXT_DIM}; font-size:0.85rem; margin-bottom:0.5rem;">'
                f'Click Generate for a Claude-powered analysis of the current umpire data.</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------------------
# Bottom section: bar chart (all umpires only)
# ---------------------------------------------------------------------------
bottom_df = ump_team_all if len(ump_team_all) > 0 else df

if len(bottom_df) > 0 and not single_umpire:
    st.markdown("---")
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
    ump_stats = ump_stats.sort_values("challenges", ascending=True).tail(10)
    ump_stats["upheld"] = ump_stats["challenges"] - ump_stats["overturned"]

    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        y=ump_stats["umpire"],
        x=ump_stats["overturned"],
        name="Overturned",
        orientation="h",
        marker=dict(color=OVERTURNED, line=dict(width=1, color=DARK_BG)),
        text=ump_stats["overturned"].astype(str),
        textposition="inside",
        textfont=dict(size=11, color=TEXT_WHITE),
        hovertemplate="%{y}<br>Overturned: %{x}<br>OT Rate: %{customdata[0]:.0f}%<extra></extra>",
        customdata=ump_stats[["overturn_rate"]].values,
    ))
    bar_fig.add_trace(go.Bar(
        y=ump_stats["umpire"],
        x=ump_stats["upheld"],
        name="Upheld",
        orientation="h",
        marker=dict(color=UPHELD, line=dict(width=1, color=DARK_BG)),
        text=ump_stats["upheld"].astype(str),
        textposition="inside",
        textfont=dict(size=11, color=TEXT_WHITE),
        hovertemplate="%{y}<br>Upheld: %{x}<extra></extra>",
    ))
    for _, row in ump_stats.iterrows():
        bar_fig.add_annotation(
            y=row["umpire"], x=row["challenges"] + 0.5,
            text=f"<b>{row['overturn_rate']:.0f}%</b> OT",
            showarrow=False,
            font=dict(size=10, color=ACCENT),
            xanchor="left",
        )
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
        height=400,
        xaxis=dict(title="Challenges", gridcolor="rgba(255,255,255,0.05)", color=TEXT_DIM, fixedrange=True),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", color=TEXT_WHITE, automargin=True, fixedrange=True),
        margin=dict(l=10, r=40, t=10, b=80),
    )
    st.plotly_chart(bar_fig, width="stretch", config=PLOTLY_CONFIG)

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
        roll_fig.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )
        st.plotly_chart(roll_fig, width="stretch", config=PLOTLY_CONFIG)

# ---------------------------------------------------------------------------
# Data Dictionary
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("📖 Data Dictionary"):
    st.markdown(f"""
| Term | Definition |
|------|-----------|
| **ABS (Automated Ball-Strike System)** | MLB's computerized system that tracks pitches and allows teams to challenge ball/strike calls. |
| **Challenge** | A team's formal request to review a ball/strike call using ABS. Each team gets a limited number per game. |
| **Overturned** | The ABS system reversed the umpire's original call. The umpire got it wrong. |
| **Upheld** | The ABS system confirmed the umpire's original call. The umpire got it right. |
| **Overturn Rate** | Percentage of challenges where the umpire's call was reversed. Higher = more umpire mistakes caught. |
| **Upheld Rate** | Percentage of challenges where the umpire's call was confirmed correct. Inverse of overturn rate. |
| **Accuracy** | Percentage of all called pitches (balls and called pitches) where the umpire's call matched the true zone. Calculated as (called pitches - overturned challenges) / called pitches. |
| **Impact Score** | A 0-100 score measuring how much a challenge affected the game. Combines run expectancy change (how the base/out state shifted) with count leverage (how critical the pitch count was). A 90+ score means the challenge significantly changed the game's outcome. |
| **Called Pitches** | All pitches where the umpire made a ball or called strike ruling (not swings, fouls, or hit-by-pitch). |
| **Established Zone** | The pink heatmap on the strike zone chart. Shows where an umpire (or the league average) consistently calls strikes, based on kernel density estimation of all called pitches ruled as strikes. Denser pink = more strikes called in that area. |
| **Zone Distance** | How far a pitch was from the nearest edge of the strike zone, measured in inches. "Inside zone" means the pitch was within the zone; "outside zone" means it was off the plate. |
| **Strike Zone** | The white rectangle on the chart. Width is the 17-inch plate. Height is the batter's individual zone (knees to midpoint of torso). |
| **pX / pZ** | Pitch coordinates in feet. pX is horizontal distance from the center of the plate (0 = middle). pZ is vertical height above the ground. |
| **pp (percentage points)** | The unit for comparing percentages. If one umpire has 55% overturn rate vs. 50% league average, that's +5.0pp. |

**Data source:** MLB Stats API, Spring Training 2026. Challenge data and called pitch locations are collected from live game feeds.
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<p class="credit">@sabrmagician</p>', unsafe_allow_html=True)

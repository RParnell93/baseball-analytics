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
BALL_RADIUS_FT = 0.121  # baseball radius (~1.45 in / 12)
ZONE_EDGE_FT = PLATE_HALF_FT + BALL_RADIUS_FT  # 0.8293 ft - strike if any part of ball crosses zone
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
            # Treat -0.0 / +0.0 as neutral
            _delta_stripped = delta.lstrip("+-").replace("pp", "").replace("vs avg", "").strip()
            try:
                _is_zero = abs(float(_delta_stripped)) < 0.05
            except ValueError:
                _is_zero = False
            if _is_zero:
                d_color = TEXT_DIM
            else:
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
            r = 27
            circ = 2 * 3.14159 * r
            ot_dash = circ * ot_pct / 100
            up_dash = circ * up_pct / 100
            donut_html = f"""
                <div style="display:flex; align-items:center; justify-content:center; gap:0.75rem; flex:1;">
                    <svg width="75" height="75" viewBox="0 0 75 75" style="flex-shrink:0;">
                        <circle cx="37.5" cy="37.5" r="{r}" fill="none" stroke="{UPHELD}" stroke-width="7"
                            stroke-dasharray="{up_dash:.1f} {circ:.1f}"
                            stroke-dashoffset="0" transform="rotate(-90 37.5 37.5)" opacity="0.85"/>
                        <circle cx="37.5" cy="37.5" r="{r}" fill="none" stroke="{OVERTURNED}" stroke-width="7"
                            stroke-dasharray="{ot_dash:.1f} {circ:.1f}"
                            stroke-dashoffset="-{up_dash:.1f}" transform="rotate(-90 37.5 37.5)" opacity="0.85"/>
                        <text x="37.5" y="34" text-anchor="middle" fill="{ACCENT}" font-size="17" font-weight="700" font-family="Montserrat,sans-serif">{total}</text>
                        <text x="37.5" y="45" text-anchor="middle" fill="{TEXT_DIM}" font-size="7" font-weight="600" font-family="Montserrat,sans-serif" letter-spacing="0.5">TOTAL</text>
                    </svg>
                    <div style="font-family:'Montserrat',sans-serif;">
                        <div style="display:flex; align-items:center; gap:0.25rem; margin-bottom:0.2rem;">
                            <span style="width:7px; height:7px; border-radius:50%; background:{OVERTURNED}; display:inline-block;"></span>
                            <span style="font-size:0.7rem; font-weight:700; color:{OVERTURNED};">{ot}</span>
                            <span style="font-size:0.65rem; font-weight:600; color:{TEXT_DIM};">Overturned ({ot_pct:.0f}%)</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:0.25rem;">
                            <span style="width:7px; height:7px; border-radius:50%; background:{UPHELD}; display:inline-block;"></span>
                            <span style="font-size:0.7rem; font-weight:700; color:{UPHELD};">{up}</span>
                            <span style="font-size:0.65rem; font-weight:600; color:{TEXT_DIM};">Upheld ({up_pct:.0f}%)</span>
                        </div>
                    </div>
                </div>"""

    _card_style = f"background-color:{CARD_BG}; padding:0.75rem 1rem; border-radius:0.5rem; overflow-wrap:break-word; margin-bottom:0.5rem; min-height:185px; display:flex; flex-direction:column; overflow:hidden;"

    if donut_html:
        return (
            f'<div style="{_card_style}">'
            f'<div style="font-size:0.75rem; color:{TEXT_DIM}; font-family:\'Montserrat\',sans-serif; font-weight:800; letter-spacing:0.05em; text-transform:uppercase;">{label}</div>'
            f'{donut_html}'
            f'{sub_html}'
            f'{delta_html}'
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
        spark_html = f"""<div style="margin-top:0.1rem;">
            <div style="font-size:0.55rem; color:{TEXT_DIM}; margin-bottom:2px; font-weight:600; letter-spacing:0.03em;">ROLLING 100-PITCH</div>
            <svg width="100%" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="display:block;">
                <line x1="0" y1="{avg_y:.1f}" x2="{w}" y2="{avg_y:.1f}" stroke="{TEXT_DIM}" stroke-width="0.5" stroke-dasharray="2,2" opacity="0.5"/>
                <polyline points="{points}" fill="none" stroke="{ACCENT}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
            </svg>
        </div>"""

    spark_wrapper = f'<div style="margin-top:auto;">{spark_html}</div>' if spark_html else ""
    return (
        f'<div style="{_card_style}">'
        f'<div>'
        f'<div style="font-size:0.75rem; color:{TEXT_DIM}; font-family:\'Montserrat\',sans-serif; font-weight:800; letter-spacing:0.05em; text-transform:uppercase;">{label}</div>'
        f'<div style="font-size:clamp(1.3rem, 4vw, 2rem); font-weight:600; color:{ACCENT};">{value}</div>'
        f'{delta_html}{sub_html}'
        f'</div>'
        f'{spark_wrapper}'
        f'</div>'
    )


def vectorized_zone_distance(px, pz, sz_top, sz_bot):
    """Compute distance from zone edge for each pitch (vectorized)."""
    abs_px = np.abs(px)
    dx = np.maximum(0, abs_px - ZONE_EDGE_FT)
    dz_above = np.maximum(0, pz - sz_top)
    dz_below = np.maximum(0, sz_bot - pz)
    dz = np.maximum(dz_above, dz_below)
    outside = (dx > 0) | (dz > 0)
    outside_dist = np.sqrt(dx**2 + dz**2)
    inside_dist = -np.minimum(
        np.minimum(ZONE_EDGE_FT - abs_px, abs_px + ZONE_EDGE_FT),
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
_favicon_path = Path(__file__).parent / "favicon_umpire.svg"
st.set_page_config(
    page_title="mlbumpviz | ABS Challenge Explorer",
    page_icon=str(_favicon_path) if _favicon_path.exists() else "baseball",
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

    /* Hide Streamlit header toolbar to prevent overlap */
    header[data-testid="stHeader"] {{
        display: none !important;
    }}
    .stMainBlockContainer {{
        padding-top: 1rem !important;
    }}

    /* Mobile optimizations */
    @media (max-width: 768px) {{
        .stMainBlockContainer {{
            padding: 0.75rem 0.5rem !important;
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
<svg width="48" height="56" viewBox="0 0 48 56" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Outer mask frame - classic umpire mask: dome top, wide cheeks, narrow chin -->
  <path d="M8 20 C8 8, 14 3, 24 3 C34 3, 40 8, 40 20 L41 28 C41 35, 36 42, 24 44 C12 42, 7 35, 7 28 Z" stroke="#7ec8e3" stroke-width="2.8" fill="rgba(126,200,227,0.06)"/>
  <!-- Top padding/visor bar -->
  <path d="M11 12 Q24 9, 37 12" stroke="#7ec8e3" stroke-width="3" fill="none" stroke-linecap="round"/>
  <!-- Horizontal cage bars -->
  <line x1="10" y1="16" x2="38" y2="16" stroke="#7ec8e3" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>
  <line x1="9" y1="24" x2="39" y2="24" stroke="#7ec8e3" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>
  <line x1="9" y1="32" x2="39" y2="32" stroke="#7ec8e3" stroke-width="1.8" stroke-linecap="round" opacity="0.5"/>
  <!-- Bar chart inside mask (data grid look) -->
  <rect x="12" y="28" width="4" height="10" rx="1" fill="#7ec8e3" opacity="0.7"/>
  <rect x="18" y="22" width="4" height="16" rx="1" fill="#7ec8e3" opacity="0.8"/>
  <rect x="24" y="18" width="4" height="20" rx="1" fill="#7ec8e3" opacity="0.9"/>
  <rect x="30" y="25" width="4" height="13" rx="1" fill="#7ec8e3" opacity="0.75"/>
  <rect x="36" y="30" width="4" height="8" rx="1" fill="#7ec8e3" opacity="0.65"/>
  <!-- Ear guards - curved pads on sides -->
  <path d="M8 17 C3 19, 2 25, 4 30 C5 33, 7 34, 8 33" stroke="#7ec8e3" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M40 17 C45 19, 46 25, 44 30 C43 33, 41 34, 40 33" stroke="#7ec8e3" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <!-- Chin guard -->
  <path d="M18 43 Q24 48, 30 43" stroke="#7ec8e3" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6"/>
  <!-- Throat protector -->
  <path d="M20 48 Q24 54, 28 48" stroke="#7ec8e3" stroke-width="1.8" fill="none" opacity="0.35"/>
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
col_f1, col_f2, col_f3, _col_spacer = st.columns([1, 1, 1, 1.5])

with col_f1:
    _default_ump = "Jen Pawol" if "Jen Pawol" in all_umpires else "All Umpires"
    _ump_options = ["All Umpires"] + all_umpires
    _default_idx = _ump_options.index(_default_ump) if _default_ump in _ump_options else 0
    selected_umpire = st.selectbox("🔍 Umpire", _ump_options, index=_default_idx)

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

# Always show both results
show_overturned = True
show_upheld = True
result_filter = ["overturned", "upheld"]

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

    games_sub = None

    # Umpire accuracy: zone geometry (correct calls / total called pitches)
    overall_accuracy = 0
    league_accuracy = 0
    if called_pitches_df is not None:
        _acc_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
        _acc_in_zone = (
            (_acc_cp["pX"].abs() <= ZONE_EDGE_FT)
            & (_acc_cp["pZ"] >= _acc_cp["sz_bottom"])
            & (_acc_cp["pZ"] <= _acc_cp["sz_top"])
        )
        _acc_cp["_correct"] = (
            ((_acc_cp["call"] == "Called Strike") & _acc_in_zone)
            | ((_acc_cp["call"] == "Ball") & ~_acc_in_zone)
        )
        # League avg (per-umpire mean, not pitch-level, for meaningful delta)
        _per_ump_acc = _acc_cp.groupby("umpire")["_correct"].mean() * 100
        league_accuracy = _per_ump_acc.mean() if len(_per_ump_acc) > 0 else 0
        # This umpire
        _acc_ump = _acc_cp[_acc_cp["umpire"] == selected_umpire]
        overall_accuracy = _acc_ump["_correct"].mean() * 100 if len(_acc_ump) > 0 else 0
    accuracy_delta = overall_accuracy - league_accuracy

    # Compute rolling 100-pitch accuracy sparkline
    acc_sparkline = None
    if called_pitches_df is not None:
        _ump_cp = called_pitches_df[called_pitches_df["umpire"] == selected_umpire].copy()
        _ump_cp = _ump_cp.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"])
        if len(_ump_cp) >= 100:
            _ump_cp = _ump_cp.sort_values("date").reset_index(drop=True)
            _in_zone = (
                (_ump_cp["pX"].abs() <= ZONE_EDGE_FT)
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

    # Check if this umpire has #1 accuracy in MLB (min 3 games, zone geometry)
    _is_top_accuracy = False
    if called_pitches_df is not None:
        _top_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
        _top_iz = (
            (_top_cp["pX"].abs() <= ZONE_EDGE_FT)
            & (_top_cp["pZ"] >= _top_cp["sz_bottom"])
            & (_top_cp["pZ"] <= _top_cp["sz_top"])
        )
        _top_cp["_correct"] = (
            ((_top_cp["call"] == "Called Strike") & _top_iz)
            | ((_top_cp["call"] == "Ball") & ~_top_iz)
        )
        _top_games = df.groupby("umpire")["game_id"].nunique().reset_index(name="games")
        _top_acc = _top_cp.groupby("umpire")["_correct"].mean().reset_index(name="accuracy")
        _top_acc = _top_acc.merge(_top_games, on="umpire")
        _top_acc = _top_acc[_top_acc["games"] >= 3]
        if len(_top_acc) > 0:
            _best_ump = _top_acc.loc[_top_acc["accuracy"].idxmax(), "umpire"]
            _is_top_accuracy = (_best_ump == selected_umpire)

    _acc_label = "Accuracy"
    if _is_top_accuracy:
        _acc_label = 'Accuracy <span style="background:linear-gradient(90deg,#ffd700,#ffaa00); color:#1a1a2e; font-size:0.55rem; font-weight:800; padding:1px 6px; border-radius:8px; margin-left:6px; vertical-align:middle;">#1 MLB</span>'

    # Challenge rate delta vs league avg
    _lg_total_challenges = len(df)
    _lg_challenge_rate = _lg_total_challenges / max(total_called, 1) * 100
    _cr_delta = challenge_pct - _lg_challenge_rate

    # Strike % for this umpire
    _ump_strike_pct = 0
    _lg_strike_pct = 0
    _strike_delta = 0
    if called_pitches_df is not None:
        _ump_cp = called_pitches_df[called_pitches_df["umpire"] == selected_umpire]
        _ump_strikes = (_ump_cp["call"] == "Called Strike").sum()
        _ump_strike_pct = _ump_strikes / max(len(_ump_cp), 1) * 100
        _lg_strikes = (called_pitches_df["call"] == "Called Strike").sum()
        _lg_strike_pct = _lg_strikes / max(len(called_pitches_df), 1) * 100
        _strike_delta = _ump_strike_pct - _lg_strike_pct

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.markdown(metric_card("Games", f"{ump_games:,}", subtext=games_sub), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Called Pitches", f"{ump_called:,}", subtext=f"{_ump_strike_pct:.1f}% called strikes", delta=f"{_strike_delta:+.1f}pp vs avg", delta_color="normal"), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Challenges", f"{ump_n:,}", subtext=f"{challenge_pct:.1f}% of called pitches", delta=f"{_cr_delta:+.1f}pp vs avg", delta_color="normal", donut={"overturned": ump_ot, "upheld": ump_up}), unsafe_allow_html=True)
    col_m4.markdown(metric_card(_acc_label, f"{overall_accuracy:.1f}%", delta=f"{accuracy_delta:+.1f}pp vs avg", delta_color="normal", sparkline=acc_sparkline), unsafe_allow_html=True)
else:
    all_games = df["game_id"].nunique()
    all_n = len(ump_team_all)
    all_ot = (ump_team_all["result"] == "overturned").sum()
    all_up = all_n - all_ot
    all_ot_pct = all_ot / max(all_n, 1) * 100
    challenge_pct = all_n / max(total_called, 1) * 100

    all_up_pct = 100 - all_ot_pct

    # League-wide accuracy (zone geometry)
    league_overall_accuracy = 0
    if called_pitches_df is not None:
        _lg_acc_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"])
        if len(_lg_acc_cp) > 0:
            _lg_iz = (
                (_lg_acc_cp["pX"].abs() <= ZONE_EDGE_FT)
                & (_lg_acc_cp["pZ"] >= _lg_acc_cp["sz_bottom"])
                & (_lg_acc_cp["pZ"] <= _lg_acc_cp["sz_top"])
            )
            _lg_correct = (
                ((_lg_acc_cp["call"] == "Called Strike") & _lg_iz)
                | ((_lg_acc_cp["call"] == "Ball") & ~_lg_iz)
            )
            league_overall_accuracy = _lg_correct.mean() * 100

    # League-wide strike %
    _lg_strike_pct = 0
    if called_pitches_df is not None and len(called_pitches_df) > 0:
        _lg_strikes = (called_pitches_df["call"] == "Called Strike").sum()
        _lg_strike_pct = _lg_strikes / len(called_pitches_df) * 100

    # League-wide rolling 100-pitch accuracy sparkline
    _lg_acc_sparkline = None
    if called_pitches_df is not None:
        _all_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
        if len(_all_cp) >= 100:
            _all_cp = _all_cp.sort_values("date").reset_index(drop=True)
            _in_zone = (
                (_all_cp["pX"].abs() <= ZONE_EDGE_FT)
                & (_all_cp["pZ"] >= _all_cp["sz_bottom"])
                & (_all_cp["pZ"] <= _all_cp["sz_top"])
            )
            _all_cp["_correct"] = (
                ((_all_cp["call"] == "Called Strike") & _in_zone)
                | ((_all_cp["call"] == "Ball") & ~_in_zone)
            ).astype(int)
            _rolling = _all_cp["_correct"].rolling(500, min_periods=500).mean() * 100
            _valid = _rolling.dropna()
            if len(_valid) > 0:
                step = max(1, len(_valid) // 30)
                _lg_acc_sparkline = _valid.iloc[::step].tolist()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.markdown(metric_card("Games", f"{all_games:,}"), unsafe_allow_html=True)
    col_m2.markdown(metric_card("Called Pitches", f"{total_called:,}", subtext=f"{_lg_strike_pct:.1f}% called strikes"), unsafe_allow_html=True)
    col_m3.markdown(metric_card("Challenges", f"{all_n:,}", subtext=f"{challenge_pct:.1f}% of called pitches", donut={"overturned": all_ot, "upheld": all_up}), unsafe_allow_html=True)
    col_m4.markdown(metric_card("Accuracy", f"{league_overall_accuracy:.1f}%", sparkline=_lg_acc_sparkline), unsafe_allow_html=True)

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

    all_ump = ch_by_ump.merge(cp_by_ump[["umpire", "called_pitches", "called_strikes", "called_balls"]], on="umpire", how="inner")
    all_ump = all_ump[all_ump["challenges"] >= 5]

    # Zone-geometry accuracy per umpire (correct calls / total calls)
    _zg_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
    _zg_in_zone = (
        (_zg_cp["pX"].abs() <= ZONE_EDGE_FT)
        & (_zg_cp["pZ"] >= _zg_cp["sz_bottom"])
        & (_zg_cp["pZ"] <= _zg_cp["sz_top"])
    )
    _zg_cp["_correct"] = (
        ((_zg_cp["call"] == "Called Strike") & _zg_in_zone)
        | ((_zg_cp["call"] == "Ball") & ~_zg_in_zone)
    )
    # Total accuracy per umpire
    _zg_total = _zg_cp.groupby("umpire").agg(
        _total=("_correct", "size"), _total_correct=("_correct", "sum"),
    ).reset_index()
    _zg_total["total_accuracy"] = (_zg_total["_total_correct"] / _zg_total["_total"] * 100)
    # Strike accuracy per umpire
    _zg_strikes = _zg_cp[_zg_cp["call"] == "Called Strike"].groupby("umpire").agg(
        _s_total=("_correct", "size"), _s_correct=("_correct", "sum"),
    ).reset_index()
    _zg_strikes["strike_accuracy"] = (_zg_strikes["_s_correct"] / _zg_strikes["_s_total"] * 100)
    # Ball accuracy per umpire
    _zg_balls = _zg_cp[_zg_cp["call"] == "Ball"].groupby("umpire").agg(
        _b_total=("_correct", "size"), _b_correct=("_correct", "sum"),
    ).reset_index()
    _zg_balls["ball_accuracy"] = (_zg_balls["_b_correct"] / _zg_balls["_b_total"] * 100)

    all_ump = all_ump.merge(_zg_total[["umpire", "total_accuracy"]], on="umpire", how="left")
    all_ump = all_ump.merge(_zg_strikes[["umpire", "strike_accuracy"]], on="umpire", how="left")
    all_ump = all_ump.merge(_zg_balls[["umpire", "ball_accuracy"]], on="umpire", how="left")
    all_ump["total_accuracy"] = all_ump["total_accuracy"].fillna(0)
    all_ump["strike_accuracy"] = all_ump["strike_accuracy"].fillna(0)
    all_ump["ball_accuracy"] = all_ump["ball_accuracy"].fillna(0)

    # Metrics
    all_ump["challenge_pct"] = all_ump["challenges"] / all_ump["called_pitches"] * 100
    all_ump["overturn_rate"] = all_ump["overturned"] / all_ump["challenges"] * 100

    ump_row = all_ump[all_ump["umpire"] == selected_umpire]
    if len(ump_row) > 0:
        ump_row = ump_row.iloc[0]

        def percentile_of(series, value):
            """Percentile using normal distribution CDF for tighter spreads."""
            from scipy.stats import norm
            mu, sigma = series.mean(), series.std()
            if sigma == 0:
                return 50.0
            return norm.cdf(value, loc=mu, scale=sigma) * 100

        def percentile_of_inverse(series, value):
            """Higher percentile = better, for metrics where LOWER value = better."""
            from scipy.stats import norm
            mu, sigma = series.mean(), series.std()
            if sigma == 0:
                return 50.0
            return (1 - norm.cdf(value, loc=mu, scale=sigma)) * 100

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
            """4-stop gradient: blue(0) -> light blue(33) -> light red(66) -> red(100)."""
            pct = max(0, min(100, pct))
            # Stops: 0%=(40,80,160), 33%=(100,160,210), 66%=(210,130,120), 100%=(200,60,60)
            stops = [
                (0,   40,  80, 160),   # blue
                (33, 100, 160, 210),   # light blue
                (66, 210, 130, 120),   # light red / salmon
                (100, 200,  60,  60),  # red
            ]
            for i in range(len(stops) - 1):
                p0, r0, g0, b0 = stops[i]
                p1, r1, g1, b1 = stops[i + 1]
                if pct <= p1:
                    t = (pct - p0) / (p1 - p0) if p1 != p0 else 0
                    r = int(r0 + t * (r1 - r0))
                    g = int(g0 + t * (g1 - g0))
                    b = int(b0 + t * (b1 - b0))
                    return f"rgb({r},{g},{b})"
            return f"rgb(200,60,60)"

        slider_html = f'<div style="background:{CARD_BG}; border-radius:0.5rem; padding:1.25rem 1.25rem; margin-bottom:0.75rem; height:100%; box-sizing:border-box; display:flex; flex-direction:column;">'
        slider_html += f'<div class="section-header">Umpire Percentile Rankings <span style="font-size:0.7rem; font-weight:400; color:{TEXT_DIM}; letter-spacing:0; text-transform:none;">{selected_umpire}</span></div>'
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

            # Umpire stats by pitch type (from challenges)
            ump_by_pitch = ump_pt.groupby("pitch_name").agg(
                challenges=("result", "size"),
                overturned=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()

            if len(cp_by_pitch) > 0:
                ump_by_pitch = ump_by_pitch.merge(cp_by_pitch, on="pitch_name", how="left").fillna(0)
            else:
                ump_by_pitch["total_pitches"] = 0

            # Zone-geometry accuracy from called pitches
            # Strike Acc = called strikes actually in zone / total called strikes
            # Ball Acc = called balls actually outside zone / total called balls
            # Total Acc = all correct calls / all called pitches
            _sa_by_pitch = pd.DataFrame(columns=["pitch_name", "strike_acc", "called_strikes"]).astype({"strike_acc": "float64", "called_strikes": "float64"})
            _ba_by_pitch = pd.DataFrame(columns=["pitch_name", "ball_acc", "called_balls"]).astype({"ball_acc": "float64", "called_balls": "float64"})
            _ta_by_pitch = pd.DataFrame(columns=["pitch_name", "total_acc"]).astype({"total_acc": "float64"})
            if len(ump_cp) > 0 and all(c in ump_cp.columns for c in ["pX", "pZ", "sz_top", "sz_bottom", "call"]):
                _cp = ump_cp.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
                _cp = _cp[_cp["pitch_name"].notna() & (_cp["pitch_name"] != "")]
                if len(_cp) > 0:
                    _in_zone = (
                        (_cp["pX"].abs() <= ZONE_EDGE_FT)
                        & (_cp["pZ"] >= _cp["sz_bottom"])
                        & (_cp["pZ"] <= _cp["sz_top"])
                    )
                    _cp["_correct"] = (
                        ((_cp["call"] == "Called Strike") & _in_zone)
                        | ((_cp["call"] == "Ball") & ~_in_zone)
                    )
                    # Total accuracy per pitch type (all calls)
                    _tg = _cp.groupby("pitch_name").agg(
                        _total=("_correct", "size"),
                        _total_correct=("_correct", "sum"),
                    ).reset_index()
                    _tg["total_acc"] = (_tg["_total_correct"] / _tg["_total"] * 100).round(1)
                    _ta_by_pitch = _tg[["pitch_name", "total_acc"]]
                    # Strike accuracy per pitch type
                    _strikes = _cp[_cp["call"] == "Called Strike"]
                    if len(_strikes) > 0:
                        _sg = _strikes.groupby("pitch_name").agg(
                            called_strikes=("_correct", "size"),
                            correct_strikes=("_correct", "sum"),
                        ).reset_index()
                        _sg["strike_acc"] = (_sg["correct_strikes"] / _sg["called_strikes"] * 100).round(1)
                        _sa_by_pitch = _sg[["pitch_name", "strike_acc", "called_strikes"]]
                    # Ball accuracy per pitch type
                    _balls = _cp[_cp["call"] == "Ball"]
                    if len(_balls) > 0:
                        _bg = _balls.groupby("pitch_name").agg(
                            called_balls=("_correct", "size"),
                            correct_balls=("_correct", "sum"),
                        ).reset_index()
                        _bg["ball_acc"] = (_bg["correct_balls"] / _bg["called_balls"] * 100).round(1)
                        _ba_by_pitch = _bg[["pitch_name", "ball_acc", "called_balls"]]

            ump_by_pitch = ump_by_pitch.merge(_ta_by_pitch, on="pitch_name", how="left")
            ump_by_pitch = ump_by_pitch.merge(_sa_by_pitch, on="pitch_name", how="left")
            ump_by_pitch = ump_by_pitch.merge(_ba_by_pitch, on="pitch_name", how="left")
            ump_by_pitch["called_strikes"] = ump_by_pitch["called_strikes"].fillna(0).astype(float)
            ump_by_pitch["called_balls"] = ump_by_pitch["called_balls"].fillna(0).astype(float)

            ump_by_pitch["challenge_pct"] = (ump_by_pitch["challenges"] / ump_by_pitch["challenges"].sum() * 100).round(1)
            ump_by_pitch["ot_rate"] = (ump_by_pitch["overturned"] / ump_by_pitch["challenges"] * 100).round(1)

            # League averages (same zone geometry approach)
            lg_by_pitch = league_pt.groupby("pitch_name").agg(
                lg_ch=("result", "size"),
                lg_ot=("result", lambda x: (x == "overturned").sum()),
            ).reset_index()
            lg_by_pitch["lg_ot_rate"] = (lg_by_pitch["lg_ot"] / lg_by_pitch["lg_ch"] * 100).round(1)

            _lg_sa_by_pitch = pd.DataFrame(columns=["pitch_name", "lg_strike_acc"])
            _lg_ba_by_pitch = pd.DataFrame(columns=["pitch_name", "lg_ball_acc"])
            _lg_ta_by_pitch = pd.DataFrame(columns=["pitch_name", "lg_total_acc"])
            if called_pitches_df is not None and all(c in called_pitches_df.columns for c in ["pX", "pZ", "sz_top", "sz_bottom", "call"]):
                _lg_cp = called_pitches_df.dropna(subset=["pX", "pZ", "sz_top", "sz_bottom"]).copy()
                _lg_cp = _lg_cp[_lg_cp["pitch_name"].notna() & (_lg_cp["pitch_name"] != "")]
                if len(_lg_cp) > 0:
                    _lg_in_zone = (
                        (_lg_cp["pX"].abs() <= ZONE_EDGE_FT)
                        & (_lg_cp["pZ"] >= _lg_cp["sz_bottom"])
                        & (_lg_cp["pZ"] <= _lg_cp["sz_top"])
                    )
                    _lg_cp["_correct"] = (
                        ((_lg_cp["call"] == "Called Strike") & _lg_in_zone)
                        | ((_lg_cp["call"] == "Ball") & ~_lg_in_zone)
                    )
                    # League total accuracy per pitch type
                    _lg_tg = _lg_cp.groupby("pitch_name").agg(
                        _n=("_correct", "size"), _c=("_correct", "sum"),
                    ).reset_index()
                    _lg_tg["lg_total_acc"] = (_lg_tg["_c"] / _lg_tg["_n"] * 100).round(1)
                    _lg_ta_by_pitch = _lg_tg[["pitch_name", "lg_total_acc"]]
                    # League strike accuracy per pitch type
                    _lg_s = _lg_cp[_lg_cp["call"] == "Called Strike"]
                    if len(_lg_s) > 0:
                        _lg_sg = _lg_s.groupby("pitch_name").agg(
                            _n=("_correct", "size"), _c=("_correct", "sum"),
                        ).reset_index()
                        _lg_sg["lg_strike_acc"] = (_lg_sg["_c"] / _lg_sg["_n"] * 100).round(1)
                        _lg_sa_by_pitch = _lg_sg[["pitch_name", "lg_strike_acc"]]
                    # League ball accuracy per pitch type
                    _lg_b = _lg_cp[_lg_cp["call"] == "Ball"]
                    if len(_lg_b) > 0:
                        _lg_bg = _lg_b.groupby("pitch_name").agg(
                            _n=("_correct", "size"), _c=("_correct", "sum"),
                        ).reset_index()
                        _lg_bg["lg_ball_acc"] = (_lg_bg["_c"] / _lg_bg["_n"] * 100).round(1)
                        _lg_ba_by_pitch = _lg_bg[["pitch_name", "lg_ball_acc"]]

            lg_by_pitch = lg_by_pitch.merge(_lg_ta_by_pitch, on="pitch_name", how="left")
            lg_by_pitch = lg_by_pitch.merge(_lg_sa_by_pitch, on="pitch_name", how="left")
            lg_by_pitch = lg_by_pitch.merge(_lg_ba_by_pitch, on="pitch_name", how="left")
            lg_by_pitch["lg_total_acc"] = lg_by_pitch["lg_total_acc"].fillna(0)

            merged = ump_by_pitch.merge(lg_by_pitch[["pitch_name", "lg_ot_rate", "lg_strike_acc", "lg_ball_acc", "lg_total_acc"]], on="pitch_name", how="left")
            merged = merged.sort_values("total_pitches", ascending=False)

            def _table_pct_color(pct):
                """Same 4-stop gradient as percentile sliders: blue(0)->light blue(33)->light red(66)->red(100)."""
                pct = max(0, min(100, pct))
                stops = [(0, 40, 80, 160), (33, 100, 160, 210), (66, 210, 130, 120), (100, 200, 60, 60)]
                for i in range(len(stops) - 1):
                    p0, r0, g0, b0 = stops[i]
                    p1, r1, g1, b1 = stops[i + 1]
                    if pct <= p1:
                        t = (pct - p0) / (p1 - p0) if p1 != p0 else 0
                        return int(r0 + t * (r1 - r0)), int(g0 + t * (g1 - g0)), int(b0 + t * (b1 - b0))
                return 200, 60, 60

            def cell_color_spectrum(val, lg_val, higher_is_better=True, threshold=1.0):
                """Percentile-style gradient matching slider colors."""
                diff = val - lg_val
                if not higher_is_better:
                    diff = -diff
                # Map diff to 0-100 percentile scale: 0 at -15pp, 50 at 0pp, 100 at +15pp
                pct = 50 + (diff / 15) * 50
                pct = max(0, min(100, pct))
                r, g, b = _table_pct_color(pct)
                alpha = 0.15 + abs(pct - 50) / 50 * 0.30  # 0.15 at center, 0.45 at extremes
                return f"background:rgba({r},{g},{b},{alpha:.2f}); color:rgb({r},{g},{b})"

            _th = f"text-align:center; padding:0.5rem 0.75rem; color:{TEXT_DIM}; font-family:'Montserrat',sans-serif; font-weight:800; font-size:0.7rem; letter-spacing:0.05em; text-transform:uppercase;"
            _td = f"text-align:center; padding:0.45rem 0.75rem; color:{TEXT_WHITE};"
            has_total = ump_by_pitch["total_pitches"].sum() > 0
            table_html = f"""
            <div style="background:{CARD_BG}; border-radius:0.5rem; padding:1.25rem 1.25rem; margin-bottom:0.75rem; overflow-x:auto; -webkit-overflow-scrolling:touch; height:100%; box-sizing:border-box;">
                <div class="section-header">Pitch Type Breakdown <span style="font-size:0.7rem; font-weight:400; color:{TEXT_DIM}; letter-spacing:0; text-transform:none;">{selected_umpire}</span></div>
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

            # Overall league averages for color comparison
            _lg_total_ch = len(league_pt) if len(league_pt) > 0 else 1
            _lg_total_ot = (league_pt["result"] == "overturned").sum() if len(league_pt) > 0 else 0
            _overall_ot_rate = _lg_total_ot / _lg_total_ch * 100
            # Overall league strike/ball accuracy from zone geometry
            _overall_strike_acc = _lg_sa_by_pitch["lg_strike_acc"].mean() if len(_lg_sa_by_pitch) > 0 else 95
            _overall_ball_acc = _lg_ba_by_pitch["lg_ball_acc"].mean() if len(_lg_ba_by_pitch) > 0 else 95

            for _, row in merged.iterrows():
                _lg_ot = _overall_ot_rate
                ot_style = cell_color_spectrum(row["ot_rate"], _lg_ot, higher_is_better=False, threshold=0.5)
                _has_ta = pd.notna(row.get("total_acc")) and row["total_pitches"] > 0
                _lg_ta = row.get("lg_total_acc", 99) if pd.notna(row.get("lg_total_acc")) else 99
                ta_style = cell_color_spectrum(float(row["total_acc"]), _lg_ta, higher_is_better=True, threshold=0.1) if _has_ta else f"background:transparent; color:{TEXT_DIM}"
                _sa_val_raw = row.get("strike_acc")
                _ba_val_raw = row.get("ball_acc")
                _has_sa = pd.notna(_sa_val_raw) and row.get("called_strikes", 0) > 0
                _has_ba = pd.notna(_ba_val_raw) and row.get("called_balls", 0) > 0
                _lg_sa = row.get("lg_strike_acc", _overall_strike_acc) if pd.notna(row.get("lg_strike_acc")) else _overall_strike_acc
                _lg_ba = row.get("lg_ball_acc", _overall_ball_acc) if pd.notna(row.get("lg_ball_acc")) else _overall_ball_acc
                sa_style = cell_color_spectrum(float(_sa_val_raw), _lg_sa, higher_is_better=True, threshold=0.5) if _has_sa else f"background:transparent; color:{TEXT_DIM}"
                ba_style = cell_color_spectrum(float(_ba_val_raw), _lg_ba, higher_is_better=True, threshold=0.5) if _has_ba else f"background:transparent; color:{TEXT_DIM}"
                ta_val = f"{float(row['total_acc']):.1f}%" if _has_ta else "-"
                sa_val = f"{float(_sa_val_raw):.1f}%" if _has_sa else "-"
                ba_val = f"{float(_ba_val_raw):.1f}%" if _has_ba else "-"
                tp_val = f"{int(row['total_pitches']):,}" if row["total_pitches"] > 0 else "-"
                # Tooltip with MLB avg for colored cells
                _ot_tip = f"MLB avg: {_lg_ot:.0f}%"
                _ta_tip = f"MLB avg: {_lg_ta:.1f}%" if _has_ta else ""
                _sa_tip = f"MLB avg: {_lg_sa:.1f}%" if _has_sa else ""
                _ba_tip = f"MLB avg: {_lg_ba:.1f}%" if _has_ba else ""
                table_html += f"""
                        <tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                            <td style="padding:0.45rem 0.75rem; color:{TEXT_WHITE};">{row['pitch_name']}</td>
                            {"<td style='" + _td + "'>" + tp_val + "</td>" if has_total else ""}
                            <td style="{_td}">{int(row['challenges'])}</td>
                            <td style="{_td} border-radius:3px; {ot_style}; cursor:default;" title="{_ot_tip}">{row['ot_rate']:.0f}%</td>
                            <td style="{_td} border-radius:3px; {ta_style}; cursor:default;" title="{_ta_tip}">{ta_val}</td>
                            <td style="{_td} border-radius:3px; {sa_style}; cursor:default;" title="{_sa_tip}">{sa_val}</td>
                            <td style="{_td} border-radius:3px; {ba_style}; cursor:default;" title="{_ba_tip}">{ba_val}</td>
                        </tr>"""

            table_html += f"""
                    </tbody>
                </table>
                <div style="font-size:0.65rem; color:{TEXT_DIM}; margin-top:0.4rem;">Red = above league avg | Blue = below | Strike/Ball Acc. = correct calls / total calls (zone geometry)</div>
            </div>"""
            st.session_state["_table_html"] = table_html

    # Render sliders and table side by side in a single HTML block (CSS grid for equal height)
    _s_html = st.session_state.get("_slider_html", "")
    _t_html = st.session_state.get("_table_html", "")
    if _s_html or _t_html:
        if _s_html and _t_html:
            combined = f"""
            <style>.resp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; align-items:stretch; }}
            @media (max-width: 768px) {{ .resp-grid {{ grid-template-columns:1fr; }} }}</style>
            <div class="resp-grid">
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
            # Established zone: uniform pink fill INSIDE the contour
            d_max = density.max()
            threshold = d_max * 0.15
            # Plotly constraint fillcolor fills the EXCLUDED region,
            # so use "<" to exclude (and fill) outside, keeping inside clear,
            # then layer: first trace fills outside with transparent bg,
            # second trace fills inside with pink using inverted density.
            neg_density = -density
            fig.add_trace(go.Contour(
                x=x_grid, y=z_grid, z=neg_density.T,
                contours=dict(
                    type="constraint", operation="<=", value=-threshold,
                ),
                fillcolor="rgba(255,80,180,0.15)",
                line=dict(width=2, color="rgba(255,80,180,0.6)"),
                showscale=False,
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
        ("upheld", UPHELD, "circle", "Stands"),
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
    plot_bgcolor=CARD_BG,
    paper_bgcolor=CARD_BG,
    font=dict(color=TEXT_WHITE),
    hoverlabel=HOVER_LABEL,
    legend=dict(
        orientation="h", yanchor="top", y=-0.12,
        xanchor="center", x=0.5,
        font=dict(size=11, color=TEXT_WHITE),
        bgcolor="rgba(0,0,0,0)",
        itemsizing="constant",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    ),
    height=850,
    margin=dict(t=70, b=90, l=40, r=40),
)

# Annotations
fig.add_annotation(x=-1.5, y=4.3, text="Ump's left", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=1.5, y=4.3, text="Ump's right", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))
fig.add_annotation(x=0, y=0.1, text="Umpire's view (behind catcher)", showarrow=False,
                   font=dict(size=10, color=TEXT_DIM))

# Established zone legend (below dot legend)
fig.add_annotation(x=0.5, y=-0.19, xref="paper", yref="paper",
                   text="<span style='color:rgba(255,80,180,0.8); font-size:14px; letter-spacing:-2px;'>&#126;&#126;&#126;</span>&nbsp;&nbsp;Established Zone (where ump calls strikes)",
                   showarrow=False, font=dict(size=10, color=TEXT_DIM))

PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}

# Build worst calls HTML (works for single umpire AND all umpires)
# Use ump_team_all (umpire+team filtered, ignores result toggle)
_worst_calls_html = ""
_wc_src = ump_team_all.dropna(subset=["pX", "pZ"]).copy() if len(ump_team_all) > 0 else pd.DataFrame()
if len(_wc_src) > 0:
    _wc_sz_t = _wc_src["sz_top"].fillna(DEFAULT_SZ_TOP).values
    _wc_sz_b = _wc_src["sz_bottom"].fillna(DEFAULT_SZ_BOT).values
    _wc_src["zone_dist"] = vectorized_zone_distance(_wc_src["pX"].values, _wc_src["pZ"].values, _wc_sz_t, _wc_sz_b)
if "zone_dist" in _wc_src.columns and len(_wc_src) > 0:
    _ot_valid = _wc_src.copy()
    _ot_valid["_abs_zone_dist"] = _ot_valid["zone_dist"].abs()
    _worst = _ot_valid.nlargest(10, "_abs_zone_dist")
    if len(_worst) > 0:
        _wc_title = "Worst Calls" if single_umpire else "Worst Calls This Spring"
        _rows_html = ""
        for _i, (_, _row) in enumerate(_worst.iterrows()):
            _call_short = "STK" if "trike" in str(_row.get("original_call", "")) else "BALL"
            _call_color = OVERTURNED if _row.get("result", "") == "overturned" else UPHELD
            _pitch_raw = _row.get("pitch_name", _row.get("pitch_type", ""))
            _pitch_abbrevs = {"Four-Seam Fastball": "4-Seam", "Two-Seam Fastball": "2-Seam", "Split-Finger": "Splitter", "Knuckle Curve": "K-Curve"}
            _pitch = _pitch_abbrevs.get(_pitch_raw, _pitch_raw)
            _dist_in = abs(_row["zone_dist"]) * 12
            _pitcher = str(_row.get("pitcher", "")).split()[-1] if _row.get("pitcher") else ""
            _batter = str(_row.get("batter", "")).split()[-1] if _row.get("batter") else ""
            _count = f"{int(_row.get('balls') or 0)}-{int(_row.get('strikes') or 0)}"
            _date_str = str(_row.get("date", ""))[:10]
            _away = _row.get("away", "")
            _home = _row.get("home", "")
            _umpire_name = str(_row.get("umpire", "")).split()[-1] if not single_umpire and _row.get("umpire") else ""
            _badge_bg = 'rgba(227,96,105,0.2)' if _row.get('result', '') == 'overturned' else 'rgba(110,194,120,0.2)'
            _badge_color = OVERTURNED if _row.get('result', '') == 'overturned' else UPHELD
            _badge_text = 'OVERTURNED' if _row.get('result', '') == 'overturned' else 'STANDS'
            # Determine challenger side: batter or defense
            _half = str(_row.get("half", ""))
            _ct = str(_row.get("challenge_team", ""))
            _batting_team = _home if _half == "bottom" else _away
            _challenger_side = "BAT" if _ct == _batting_team else "DEF"
            _side_bg = 'rgba(100,149,237,0.2)' if _challenger_side == "BAT" else 'rgba(255,165,0,0.2)'
            _side_color = '#6495ED' if _challenger_side == "BAT" else '#FFA500'
            _border_top = f'border-top:1px solid rgba(255,255,255,0.06);' if _i > 0 else ''
            _ump_line = f' <span style="color:{ACCENT}; font-weight:700;">{_umpire_name}</span> &middot;' if _umpire_name else ''
            _row_bg = 'rgba(255,255,255,0.02)' if _i % 2 == 0 else 'transparent'
            _accent_bar = _badge_color
            _rows_html += f'''
                <div style="display:flex; align-items:center; gap:1rem; padding:0.75rem 0.75rem; margin:0 -0.5rem;
                            background:{_row_bg}; border-radius:6px; border-left:3px solid {_accent_bar};">
                    <div style="font-size:0.75rem; color:{TEXT_DIM}; font-weight:800; font-family:'Montserrat',sans-serif; min-width:1.8rem; text-align:center;">#{_i+1}</div>
                    <div style="min-width:5rem;">
                        <div style="font-size:1.4rem; font-weight:800; color:{OVERTURNED}; font-family:'Montserrat',sans-serif; line-height:1; white-space:nowrap;">
                            {_dist_in:.1f}<span style="font-size:0.7rem; color:{TEXT_DIM}; font-weight:600;"> in</span>
                        </div>
                    </div>
                    <div style="flex:1; min-width:0;">
                        <div style="font-size:0.75rem; color:{TEXT_WHITE}; font-family:'Montserrat',sans-serif; line-height:1.4; font-weight:600;">
                            {_ump_line}<span style="color:{_call_color}; font-weight:800;">{_call_short}</span> &middot; {_count} &middot; {_pitch} &middot; {_pitcher} v {_batter}
                        </div>
                        <div style="font-size:0.6rem; color:{TEXT_DIM}; font-family:'Montserrat',sans-serif; margin-top:2px;">{_date_str} &middot; {_away} @ {_home}</div>
                    </div>
                    <div style="display:flex; flex-direction:column; align-items:flex-end; gap:3px; flex-shrink:0;">
                        <span style="font-size:0.5rem; font-weight:700; font-family:'Montserrat',sans-serif;
                                    padding:3px 7px; border-radius:4px; letter-spacing:0.04em;
                                    background:{_badge_bg}; color:{_badge_color}; white-space:nowrap;">{_badge_text}</span>
                        <span style="font-size:0.5rem; font-weight:600; font-family:'Montserrat',sans-serif;
                                    padding:3px 7px; border-radius:4px; letter-spacing:0.04em;
                                    background:{_side_bg}; color:{_side_color}; white-space:nowrap;">{_challenger_side}</span>
                    </div>
                </div>'''
        _worst_calls_html = f'''
            <div style="background:{CARD_BG}; border-radius:0.5rem; padding:1.25rem 1.5rem; box-sizing:border-box; height:920px; overflow-y:auto;">
                <div class="section-header" style="margin-bottom:0.15rem;">{_wc_title}</div>
                <div style="font-size:0.65rem; color:{TEXT_DIM}; margin-bottom:1rem;">Ranked by distance from zone edge</div>
                <div style="display:flex; flex-direction:column; gap:0.35rem;">
                    {_rows_html}
                </div>
            </div>'''

# Strike zone + Worst calls side by side
if _worst_calls_html:
    _zone_col, _worst_col = st.columns([3, 2])
    with _zone_col:
        st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)
    with _worst_col:
        st.html(_worst_calls_html)
else:
    st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)

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
# AI Summary Section
# ---------------------------------------------------------------------------
st.markdown("---")
if HAS_ANTHROPIC:
    summary_src = ump_team_all if len(ump_team_all) > 0 else df

    if len(summary_src) > 0:
        filter_key = f"{selected_umpire}_{selected_team}_{show_overturned}_{show_upheld}_{date_range}"
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
            if not api_key:
                try:
                    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                except Exception:
                    api_key = ""
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
| **Established Zone** | The pink filled region on the strike zone chart. Shows the boundary where an umpire (or the league average) consistently calls strikes, based on kernel density estimation of all called pitches ruled as strikes. |
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

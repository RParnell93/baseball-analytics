"""Player stat card generator - inspired by Pitcher List's stat card format.

Generates shareable single-image stat cards for pitchers and hitters
using Statcast data. Designed for social media posting.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd
from .style import PALETTE, CREDIT
from .team_colors import get_color, get_team_name

# Consistent pitch type colors (matching Pitcher List convention)
PITCH_COLORS = {
    "FF": "#E04040",   # 4-seam - red
    "SI": "#F5A623",   # sinker - orange
    "FC": "#E88DA0",   # cutter - pink
    "CH": "#4CAF50",   # changeup - green
    "SL": "#2196F3",   # slider - blue
    "CU": "#5C6BC0",   # curveball - indigo
    "ST": "#E040C0",   # sweeper - magenta
    "SV": "#7B1FA2",   # slurve - purple
    "KC": "#E91E63",   # knuckle curve - deep pink
    "FS": "#26C6DA",   # splitter - cyan
    "KN": "#795548",   # knuckleball - brown
}

# Dark theme colors
DARK_BG = "#1C2331"
CARD_BG = "#232D3F"
ACCENT = "#22D1EE"
TEXT_WHITE = "#EAEAEA"
TEXT_DIM = "#8899AA"
GRID_DIM = "#2A3649"


def pitcher_stat_card(pitch_df, player_name, team_abbr, age=None,
                      game_date=None, game_line=None, save_path=None):
    """Generate a pitcher stat card from Statcast pitch data.

    Args:
        pitch_df: DataFrame of Statcast pitches for this pitcher (one game or season)
        player_name: "First Last" format
        team_abbr: e.g. "BAL"
        age: player age (optional)
        game_date: date string (optional)
        game_line: summary string like "6.0 IP, 1 ER, 8 K" (optional)
        save_path: file path to save PNG (optional)

    Returns:
        matplotlib figure
    """
    fig = plt.figure(figsize=(10, 16), facecolor=DARK_BG)

    # Layout: header, usage bars, movement+location, metrics table (2 rows)
    gs = gridspec.GridSpec(5, 2, figure=fig, hspace=0.45, wspace=0.25,
                           left=0.08, right=0.94, top=0.94, bottom=0.03,
                           height_ratios=[0.8, 1.4, 1.8, 1, 1])

    df = pitch_df.dropna(subset=["pitch_type"]).copy()
    pitch_types = df["pitch_type"].value_counts()
    total_pitches = len(df)

    # ── HEADER ──
    ax_header = fig.add_subplot(gs[0, :])
    ax_header.set_facecolor(DARK_BG)
    ax_header.axis("off")

    team_color = get_color(team_abbr)
    team_name = get_team_name(team_abbr)

    # Player name
    ax_header.text(0.0, 0.85, player_name, fontsize=28, fontweight="bold",
                   color=TEXT_WHITE, transform=ax_header.transAxes, va="top")

    # Team / position / age line
    info_parts = [team_abbr]
    if age:
        info_parts.append(f"Age: {age}")
    ax_header.text(0.0, 0.55, " | ".join(info_parts),
                   fontsize=12, color=TEXT_DIM, transform=ax_header.transAxes, va="top")

    # Game line
    if game_line:
        ax_header.text(0.0, 0.25, game_line,
                       fontsize=11, color=ACCENT, transform=ax_header.transAxes, va="top",
                       bbox=dict(boxstyle="round,pad=0.4", facecolor=GRID_DIM, edgecolor=ACCENT, linewidth=1))

    # Brand
    ax_header.text(1.0, 0.85, CREDIT, fontsize=10, color=TEXT_DIM,
                   transform=ax_header.transAxes, va="top", ha="right")

    # Thin team color stripe at the very top
    fig.patches.append(patches.Rectangle(
        (0.0, 0.975), 1.0, 0.025, transform=fig.transFigure,
        facecolor=team_color, edgecolor="none", zorder=0
    ))

    # ── PITCH ARSENAL / USAGE ──
    ax_usage = fig.add_subplot(gs[1, :])
    ax_usage.set_facecolor(CARD_BG)

    y_pos = 0
    for ptype, count in pitch_types.items():
        pct = count / total_pitches * 100
        color = PITCH_COLORS.get(ptype, "#999999")

        # Avg velo for this pitch
        avg_velo = df[df["pitch_type"] == ptype]["release_speed"].mean()
        velo_str = f"{avg_velo:.1f}" if not pd.isna(avg_velo) else "--"

        # Bar
        ax_usage.barh(y_pos, pct, height=0.6, color=color, alpha=0.85)
        # Label
        ax_usage.text(-1, y_pos, f"{ptype}", fontsize=10, color=color,
                      va="center", ha="right", fontweight="bold")
        # Percentage
        ax_usage.text(pct + 1, y_pos, f"{pct:.0f}%  ({velo_str} mph)",
                      fontsize=9, color=TEXT_DIM, va="center")
        y_pos -= 1

    ax_usage.set_xlim(-8, 65)
    ax_usage.set_ylim(y_pos - 0.5, 0.8)
    ax_usage.set_title("Pitch Usage & Velocity", fontsize=12, color=TEXT_WHITE,
                       fontweight="bold", loc="left", pad=10)
    ax_usage.axis("off")

    # ── MOVEMENT PLOT ──
    ax_move = fig.add_subplot(gs[2, 0])
    ax_move.set_facecolor(CARD_BG)

    for ptype in pitch_types.index:
        subset = df[df["pitch_type"] == ptype].dropna(subset=["pfx_x", "pfx_z"])
        if len(subset) == 0:
            continue
        color = PITCH_COLORS.get(ptype, "#999999")
        ax_move.scatter(
            subset["pfx_x"] * 12, subset["pfx_z"] * 12,
            alpha=0.5, s=25, c=color, label=ptype, edgecolors="none"
        )

    ax_move.axhline(0, color=GRID_DIM, linewidth=0.8)
    ax_move.axvline(0, color=GRID_DIM, linewidth=0.8)
    ax_move.set_xlabel("Horizontal Break (in)", fontsize=9, color=TEXT_DIM)
    ax_move.set_ylabel("Induced Vertical Break (in)", fontsize=9, color=TEXT_DIM)
    ax_move.set_title("Movement", fontsize=12, color=TEXT_WHITE, fontweight="bold", loc="left")
    ax_move.tick_params(colors=TEXT_DIM, labelsize=8)
    ax_move.set_facecolor(CARD_BG)
    for spine in ax_move.spines.values():
        spine.set_color(GRID_DIM)

    # ── LOCATION PLOT ──
    ax_loc = fig.add_subplot(gs[2, 1])
    ax_loc.set_facecolor(CARD_BG)

    for ptype in pitch_types.index:
        subset = df[df["pitch_type"] == ptype].dropna(subset=["plate_x", "plate_z"])
        if len(subset) == 0:
            continue
        color = PITCH_COLORS.get(ptype, "#999999")
        ax_loc.scatter(
            subset["plate_x"], subset["plate_z"],
            alpha=0.4, s=15, c=color, edgecolors="none"
        )

    # Strike zone
    zone = patches.Rectangle((-0.83, 1.5), 1.66, 2.0,
                              linewidth=1.5, edgecolor=TEXT_DIM, facecolor="none", linestyle="--")
    ax_loc.add_patch(zone)
    ax_loc.set_xlim(-2.5, 2.5)
    ax_loc.set_ylim(0, 5)
    ax_loc.set_title("Locations", fontsize=12, color=TEXT_WHITE, fontweight="bold", loc="left")
    ax_loc.set_aspect("equal")
    ax_loc.tick_params(colors=TEXT_DIM, labelsize=8)
    for spine in ax_loc.spines.values():
        spine.set_color(GRID_DIM)

    # ── PITCH METRICS TABLE ──
    ax_table = fig.add_subplot(gs[3:, :])
    ax_table.set_facecolor(CARD_BG)
    ax_table.axis("off")

    # Build metrics per pitch type
    rows = []
    for ptype in pitch_types.index:
        sub = df[df["pitch_type"] == ptype]
        count = len(sub)
        avg_velo = sub["release_speed"].mean()
        avg_ivb = sub["pfx_z"].mean() * 12 if "pfx_z" in sub.columns else 0
        avg_hb = sub["pfx_x"].mean() * 12 if "pfx_x" in sub.columns else 0

        # Strike/ball/whiff rates
        called_strikes = sub["description"].isin(["called_strike"]).sum()
        swinging_strikes = sub["description"].isin(["swinging_strike", "swinging_strike_blocked"]).sum()
        fouls = sub["description"].isin(["foul", "foul_tip"]).sum()
        balls = sub["description"].isin(["ball", "blocked_ball"]).sum()

        str_pct = (called_strikes + swinging_strikes + fouls) / max(count, 1) * 100
        whiff_pct = swinging_strikes / max(count, 1) * 100
        csw_pct = (called_strikes + swinging_strikes) / max(count, 1) * 100

        rows.append({
            "Type": ptype, "#": count,
            "Velo": f"{avg_velo:.1f}" if not pd.isna(avg_velo) else "--",
            "IVB": f'{avg_ivb:.1f}"',
            "HB": f'{avg_hb:.1f}"',
            "Str%": f"{str_pct:.0f}%",
            "Whiff%": f"{whiff_pct:.0f}%",
            "CSW%": f"{csw_pct:.0f}%",
        })

    if rows:
        table_df = pd.DataFrame(rows)
        col_labels = list(table_df.columns)

        table = ax_table.table(
            cellText=table_df.values,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.6)

        # Style the table
        for (row, col), cell in table.get_celld().items():
            cell.set_facecolor(CARD_BG)
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
            else:
                cell.set_text_props(color=TEXT_WHITE)
                # Color the Type column by pitch color
                if col == 0 and row > 0:
                    ptype = table_df.iloc[row - 1]["Type"]
                    cell.set_text_props(color=PITCH_COLORS.get(ptype, TEXT_WHITE), fontweight="bold")

        ax_table.set_title("Pitch Type Metrics", fontsize=12, color=TEXT_WHITE,
                          fontweight="bold", loc="left", pad=15)

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig

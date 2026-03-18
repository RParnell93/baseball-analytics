"""Batted ball metrics by pitch type with conditional formatting.

Shows a hitter's performance broken down by pitch type with color-coded
comparisons to league average.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from ..utils.db import query
from .team_colors import get_color
from .style import CREDIT

# Dark theme colors (matching stat_cards.py)
DARK_BG = "#1C2331"
CARD_BG = "#232D3F"
ACCENT = "#22D1EE"
TEXT_WHITE = "#E8E8E8"
TEXT_DIM = "#7A8BA0"
GRID_DIM = "#2A3A50"

# Pitch type name mapping
PITCH_NAMES = {
    "FF": "Four-Seam", "SI": "Sinker", "FC": "Cutter", "SL": "Slider",
    "CU": "Curveball", "CH": "Changeup", "FS": "Splitter", "KC": "Knuckle Curve",
    "ST": "Sweeper", "SV": "Slurve", "KN": "Knuckleball", "CS": "Slow Curve",
}


def lookup_batter_id(player_name):
    """Search for a batter's MLBAM ID by name.

    Args:
        player_name: Full name like "Juan Soto" or "Soto, Juan"

    Returns:
        int: MLBAM ID

    Raises:
        ValueError: If player not found or name is ambiguous
    """
    # Handle "Last, First" or "First Last" format
    if "," in player_name:
        last, first = [p.strip() for p in player_name.split(",", 1)]
    else:
        parts = player_name.strip().split()
        if len(parts) < 2:
            raise ValueError(f"Invalid name format: {player_name}")
        first = parts[0]
        last = " ".join(parts[1:])

    # Search player_ids table
    df = query(f"""
        SELECT key_mlbam, name_first, name_last
        FROM player_ids
        WHERE LOWER(name_first) = LOWER('{first}')
        AND LOWER(name_last) = LOWER('{last}')
        AND key_mlbam IS NOT NULL
        ORDER BY mlb_played_last DESC NULLS LAST
        LIMIT 1
    """)

    if len(df) == 0:
        raise ValueError(f"Player not found: {player_name}")

    return int(df.iloc[0]["key_mlbam"])


def generate_batted_ball_by_pitch_type(batter_id, player_name, team_abbr=None, save_path=None):
    """Generate a batted ball metrics table by pitch type with conditional formatting.

    Args:
        batter_id: MLBAM ID of the batter
        player_name: Display name ("First Last")
        team_abbr: Team abbreviation (e.g. "NYY") for color accent
        save_path: Optional path to save PNG

    Returns:
        matplotlib figure
    """
    # Query batter's batted balls by pitch type
    batter_df = query(f"""
        SELECT
            pitch_type,
            launch_speed,
            launch_angle,
            estimated_woba_using_speedangle as xwoba,
            bb_type
        FROM statcast_pitches
        WHERE batter = {batter_id}
        AND description = 'hit_into_play'
        AND launch_speed IS NOT NULL
        AND pitch_type IS NOT NULL
    """)

    if len(batter_df) == 0:
        raise ValueError(f"No batted ball data found for batter ID {batter_id}")

    # Query league averages by pitch type
    league_df = query("""
        SELECT
            pitch_type,
            AVG(launch_speed) as lg_ev,
            AVG(launch_angle) as lg_la,
            AVG(estimated_woba_using_speedangle) as lg_xwoba,
            SUM(CASE WHEN bb_type = 'ground_ball' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as lg_gb_pct
        FROM statcast_pitches
        WHERE description = 'hit_into_play'
        AND launch_speed IS NOT NULL
        AND pitch_type IS NOT NULL
        GROUP BY pitch_type
    """)

    # Calculate batter stats by pitch type
    pitch_stats = []
    for pitch_type in batter_df["pitch_type"].unique():
        subset = batter_df[batter_df["pitch_type"] == pitch_type]
        n = len(subset)

        if n < 10:  # Filter to pitch types with at least 10 BBE
            continue

        avg_ev = subset["launch_speed"].mean()
        avg_la = subset["launch_angle"].mean()
        avg_xwoba = subset["xwoba"].mean()
        gb_count = (subset["bb_type"] == "ground_ball").sum()
        gb_pct = gb_count / n * 100

        # Get league averages for this pitch type
        lg_row = league_df[league_df["pitch_type"] == pitch_type]
        if len(lg_row) == 0:
            continue

        lg_ev = lg_row.iloc[0]["lg_ev"]
        lg_la = lg_row.iloc[0]["lg_la"]
        lg_xwoba = lg_row.iloc[0]["lg_xwoba"]
        lg_gb_pct = lg_row.iloc[0]["lg_gb_pct"]

        pitch_stats.append({
            "pitch_type": pitch_type,
            "n": n,
            "avg_ev": avg_ev,
            "avg_la": avg_la,
            "avg_xwoba": avg_xwoba,
            "gb_pct": gb_pct,
            "lg_ev": lg_ev,
            "lg_la": lg_la,
            "lg_xwoba": lg_xwoba,
            "lg_gb_pct": lg_gb_pct,
        })

    if len(pitch_stats) == 0:
        raise ValueError(f"Not enough batted balls (min 10 per pitch type) for batter ID {batter_id}")

    # Sort by sample size descending
    pitch_stats = sorted(pitch_stats, key=lambda x: x["n"], reverse=True)

    # Calculate league averages across all pitch types for the bottom row
    total_bbe = batter_df.shape[0]
    overall_lg_ev = league_df["lg_ev"].mean()
    overall_lg_la = league_df["lg_la"].mean()
    overall_lg_xwoba = league_df["lg_xwoba"].mean()
    overall_lg_gb_pct = league_df["lg_gb_pct"].mean()

    # Create figure with height based on number of rows (data + header + league avg row)
    n_rows = len(pitch_stats) + 1  # +1 for league avg row
    fig, ax = plt.subplots(figsize=(12, max(4, 2.5 + n_rows * 0.65)), facecolor=DARK_BG)
    ax.set_facecolor(CARD_BG)
    ax.axis("off")

    # Build table data
    col_labels = ["Pitch", "BBE", "EV", "LA", "xwOBA", "GB%"]
    table_data = []
    cell_colors = []

    for stat in pitch_stats:
        # Get full pitch name, fall back to code if not found
        pitch_name = PITCH_NAMES.get(stat["pitch_type"], stat["pitch_type"])

        row = [
            pitch_name,
            str(stat["n"]),
            f"{stat['avg_ev']:.1f}",
            f"{stat['avg_la']:.1f}°",
            f"{stat['avg_xwoba']:.3f}",
            f"{stat['gb_pct']:.1f}%",
        ]
        table_data.append(row)

        # Calculate color intensity based on difference from league avg
        # Green = good, Red = bad
        def get_color_for_metric(value, lg_value, higher_is_better=True):
            diff = value - lg_value

            # Determine if this is good or bad
            if higher_is_better:
                is_good = diff > 0
            else:
                is_good = diff < 0

            # Normalize difference to 0-1 scale for color intensity
            # Use standard deviations as reference
            abs_diff = abs(diff)
            if higher_is_better:
                # For EV: 2 mph is significant
                # For LA: 3 degrees is significant
                # For xwOBA: 0.05 is significant
                if "ev" in str(lg_value):
                    intensity = min(abs_diff / 4.0, 1.0)
                elif abs(lg_value) < 1:  # xwOBA
                    intensity = min(abs_diff / 0.08, 1.0)
                else:  # launch angle
                    intensity = min(abs_diff / 6.0, 1.0)
            else:  # GB% - lower is better
                intensity = min(abs_diff / 15.0, 1.0)

            # Return RGB color
            if is_good:
                # Green: interpolate from CARD_BG to bright green
                r = int(0x23 + (0x00 - 0x23) * intensity)
                g = int(0x2D + (0xCC - 0x2D) * intensity)
                b = int(0x3F + (0x00 - 0x3F) * intensity)
            else:
                # Red: interpolate from CARD_BG to bright red
                r = int(0x23 + (0xDD - 0x23) * intensity)
                g = int(0x2D + (0x00 - 0x2D) * intensity)
                b = int(0x3F + (0x00 - 0x3F) * intensity)

            return f"#{r:02x}{g:02x}{b:02x}"

        # Row colors: pitch type (no color), BBE (no color), then metrics with conditional coloring
        row_colors = [
            CARD_BG,  # Pitch type
            CARD_BG,  # BBE
            get_color_for_metric(stat["avg_ev"], stat["lg_ev"], higher_is_better=True),
            get_color_for_metric(stat["avg_la"], stat["lg_la"], higher_is_better=True),
            get_color_for_metric(stat["avg_xwoba"], stat["lg_xwoba"], higher_is_better=True),
            get_color_for_metric(stat["gb_pct"], stat["lg_gb_pct"], higher_is_better=False),
        ]
        cell_colors.append(row_colors)

    # Add league average row at bottom
    lg_avg_row = [
        "Lg Avg",
        str(total_bbe),
        f"{overall_lg_ev:.1f}",
        f"{overall_lg_la:.1f}°",
        f"{overall_lg_xwoba:.3f}",
        f"{overall_lg_gb_pct:.1f}%",
    ]
    table_data.append(lg_avg_row)

    # League avg row uses GRID_DIM background for all cells
    lg_avg_colors = [GRID_DIM] * len(col_labels)
    cell_colors.append(lg_avg_colors)

    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellColours=cell_colors,
        colColours=[GRID_DIM] * len(col_labels),
        loc="center",
        cellLoc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)

    # Style the table
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID_DIM)
        cell.set_linewidth(1)

        if row == 0:  # Header row
            cell.set_text_props(color=ACCENT, fontweight="bold", fontsize=12)
        else:
            cell.set_text_props(color=TEXT_WHITE, fontsize=11)

    # Add title and subtitle
    team_color = get_color(team_abbr) if team_abbr else ACCENT

    fig.text(0.08, 0.96, f"{player_name} - Batted Ball Metrics by Pitch Type",
             fontsize=18, fontweight="bold", color=TEXT_WHITE, va="top")

    fig.text(0.08, 0.92, "Color-coded vs. league average (green = better, red = worse)",
             fontsize=11, color=TEXT_DIM, va="top")

    # Add team color stripe at top
    if team_abbr:
        fig.patches.append(patches.Rectangle(
            (0.0, 0.98), 1.0, 0.02, transform=fig.transFigure,
            facecolor=team_color, edgecolor="none", zorder=0
        ))

    # Add watermark
    fig.text(0.92, 0.02, CREDIT, fontsize=10, color=TEXT_DIM,
             ha="right", va="bottom", alpha=0.7)

    plt.tight_layout(rect=[0, 0.05, 1, 0.9])

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig

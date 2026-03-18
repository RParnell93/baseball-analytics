"""Reusable baseball chart functions.

Each function takes data and returns a matplotlib figure.
Use these as building blocks for dashboards and social posts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from .style import apply_style, add_credit, PALETTE
from .team_colors import get_color


def strike_zone_heatmap(pitch_df, title="Strike Zone Heatmap", cmap="YlOrRd"):
    """Create a strike zone heatmap from Statcast pitch data.

    Args:
        pitch_df: DataFrame with plate_x and plate_z columns
        title: chart title
        cmap: matplotlib colormap name

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 8))

    # Filter to pitches with location data
    df = pitch_df.dropna(subset=["plate_x", "plate_z"])

    # 2D histogram
    h = ax.hist2d(
        df["plate_x"], df["plate_z"],
        bins=30, range=[[-2, 2], [0, 5]],
        cmap=cmap, alpha=0.9
    )
    plt.colorbar(h[3], ax=ax, label="Pitch Count")

    # Draw strike zone box (approximate MLB zone)
    zone = patches.Rectangle(
        (-0.83, 1.5), 1.66, 2.0,
        linewidth=2, edgecolor="white", facecolor="none", linestyle="--"
    )
    ax.add_patch(zone)

    ax.set_xlabel("Horizontal Position (ft)")
    ax.set_ylabel("Vertical Position (ft)")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_aspect("equal")
    add_credit(fig)
    return fig, ax


def pitch_movement_plot(pitch_df, title="Pitch Movement Profile"):
    """Create a pitch movement scatter plot colored by pitch type.

    Args:
        pitch_df: DataFrame with pfx_x, pfx_z, pitch_type columns

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 8))

    df = pitch_df.dropna(subset=["pfx_x", "pfx_z", "pitch_type"])

    # Convert to inches (Statcast stores in feet)
    df = df.copy()
    df["pfx_x_in"] = df["pfx_x"] * 12
    df["pfx_z_in"] = df["pfx_z"] * 12

    pitch_colors = {
        "FF": "#D32F2F",  # 4-seam fastball - red
        "SI": "#FF7043",  # sinker - orange
        "FC": "#FF9800",  # cutter - amber
        "CH": "#4CAF50",  # changeup - green
        "SL": "#2196F3",  # slider - blue
        "CU": "#9C27B0",  # curveball - purple
        "ST": "#00BCD4",  # sweeper - teal
        "SV": "#7B1FA2",  # slurve - deep purple
        "KC": "#E91E63",  # knuckle curve - pink
        "FS": "#009688",  # splitter - dark teal
        "KN": "#795548",  # knuckleball - brown
    }

    for ptype in df["pitch_type"].unique():
        subset = df[df["pitch_type"] == ptype]
        color = pitch_colors.get(ptype, "#999999")
        ax.scatter(
            subset["pfx_x_in"], subset["pfx_z_in"],
            alpha=0.4, s=20, c=color, label=f"{ptype} ({len(subset)})"
        )

    # Draw crosshairs at origin
    ax.axhline(y=0, color=PALETTE["grid"], linewidth=0.8)
    ax.axvline(x=0, color=PALETTE["grid"], linewidth=0.8)

    ax.set_xlabel("Horizontal Break (in)")
    ax.set_ylabel("Induced Vertical Break (in)")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)
    add_credit(fig)
    return fig, ax


def exit_velo_launch_angle(batted_df, title="Exit Velo vs Launch Angle"):
    """Scatter plot of exit velocity vs launch angle, colored by outcome.

    Args:
        batted_df: DataFrame with launch_speed, launch_angle, events columns

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    df = batted_df.dropna(subset=["launch_speed", "launch_angle"])

    # Color by outcome
    outcome_colors = {
        "home_run": "#D32F2F",
        "triple": "#FF9800",
        "double": "#4CAF50",
        "single": "#2196F3",
        "field_out": "#BDBDBD",
        "grounded_into_double_play": "#616161",
        "force_out": "#9E9E9E",
        "sac_fly": "#78909C",
        "fielders_choice": "#90A4AE",
        "double_play": "#546E7A",
    }

    # Plot non-hits first (background)
    non_hits = df[~df["events"].isin(["home_run", "triple", "double", "single"])]
    ax.scatter(non_hits["launch_angle"], non_hits["launch_speed"],
               alpha=0.1, s=5, c="#BDBDBD")

    # Plot hits on top
    for event in ["single", "double", "triple", "home_run"]:
        subset = df[df["events"] == event]
        if len(subset) > 0:
            color = outcome_colors.get(event, "#999999")
            ax.scatter(subset["launch_angle"], subset["launch_speed"],
                       alpha=0.5, s=15, c=color, label=f"{event} ({len(subset)})")

    ax.set_xlabel("Launch Angle (degrees)")
    ax.set_ylabel("Exit Velocity (mph)")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-60, 80)
    ax.set_ylim(20, 125)
    add_credit(fig)
    return fig, ax


def rolling_stat_line(player_df, stat_col, window=30, title=None, team_abbr=None):
    """Rolling average line chart for a player stat over a season.

    Args:
        player_df: DataFrame sorted by date with the stat column
        stat_col: column name to plot
        window: rolling window size in games/rows
        title: chart title
        team_abbr: team abbreviation for color

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 5))

    color = get_color(team_abbr) if team_abbr else PALETTE["dark"]
    df = player_df.copy()
    df["rolling"] = df[stat_col].rolling(window=window, min_periods=1).mean()

    ax.plot(df.index, df["rolling"], color=color, linewidth=2.5)
    ax.fill_between(df.index, df["rolling"], alpha=0.1, color=color)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_ylabel(stat_col)
    add_credit(fig)
    return fig, ax


def spray_chart(batted_df, title="Spray Chart", team_abbr=None):
    """Hit spray chart showing batted ball locations on a field outline.

    Args:
        batted_df: DataFrame with hc_x, hc_y columns (Statcast hit coordinates)
        title: chart title
        team_abbr: team abbreviation for color

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 8))

    df = batted_df.dropna(subset=["hc_x", "hc_y"])

    # Statcast coords: home plate ~(125, 200), field fans out upward
    # Flip y so field looks normal (home at bottom)
    x = df["hc_x"]
    y = 250 - df["hc_y"]

    outcome_colors = {
        "home_run": "#D32F2F",
        "triple": "#FF9800",
        "double": "#4CAF50",
        "single": "#2196F3",
    }

    # Plot outs first
    outs = df[~df["events"].isin(outcome_colors.keys())]
    ax.scatter(outs["hc_x"], 250 - outs["hc_y"], alpha=0.15, s=10, c="#999999")

    # Plot hits on top
    for event, color in outcome_colors.items():
        subset = df[df["events"] == event]
        if len(subset) > 0:
            ax.scatter(subset["hc_x"], 250 - subset["hc_y"],
                       alpha=0.6, s=20, c=color, label=f"{event} ({len(subset)})")

    # Draw basic diamond outline
    diamond = np.array([[125, 50], [175, 100], [125, 150], [75, 100], [125, 50]])
    ax.plot(diamond[:, 0], diamond[:, 1], color=PALETTE["grid"], linewidth=1)

    # Foul lines (approximate)
    ax.plot([125, 0], [50, 200], color=PALETTE["grid"], linewidth=0.5, linestyle="--")
    ax.plot([125, 250], [50, 200], color=PALETTE["grid"], linewidth=0.5, linestyle="--")

    ax.set_xlim(0, 250)
    ax.set_ylim(0, 220)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", fontsize=9)
    ax.axis("off")
    add_credit(fig)
    return fig, ax


def expected_vs_actual(player_df, x_col, y_col, name_col="Name",
                       title=None, xlabel=None, ylabel=None):
    """Scatter plot comparing expected vs actual metrics.

    Good for xwOBA vs wOBA, xBA vs BA, xERA vs ERA, etc.

    Args:
        player_df: DataFrame with columns for expected and actual metrics
        x_col: expected metric column name
        y_col: actual metric column name
        name_col: column with player names for labels
        title: chart title
        xlabel: x-axis label
        ylabel: y-axis label

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(10, 10))

    df = player_df.dropna(subset=[x_col, y_col]).copy()

    ax.scatter(df[x_col], df[y_col], alpha=0.5, s=40, c=PALETTE["dark"])

    # Diagonal line (perfect agreement)
    lims = [
        min(df[x_col].min(), df[y_col].min()),
        max(df[x_col].max(), df[y_col].max()),
    ]
    ax.plot(lims, lims, color="#999999", linewidth=1, linestyle="--", zorder=0)

    # Label outliers (players furthest from the diagonal)
    df["diff"] = abs(df[y_col] - df[x_col])
    outliers = df.nlargest(10, "diff")
    for _, row in outliers.iterrows():
        ax.annotate(
            row[name_col],
            (row[x_col], row[y_col]),
            fontsize=7, alpha=0.8,
            xytext=(5, 5), textcoords="offset points",
        )

    ax.set_xlabel(xlabel or x_col, fontsize=11)
    ax.set_ylabel(ylabel or y_col, fontsize=11)
    ax.set_title(title or f"{y_col} vs {x_col}", fontsize=14, fontweight="bold", pad=15)
    add_credit(fig)
    return fig, ax


def player_radar(player_stats, league_avg, stat_labels, player_name="Player",
                 team_abbr=None, title=None):
    """Radar/spider chart comparing a player to league average.

    Args:
        player_stats: list of stat values for the player
        league_avg: list of stat values for league average (same order)
        stat_labels: list of stat names
        player_name: for legend
        team_abbr: team abbreviation for color
        title: chart title

    Returns:
        (fig, ax) tuple
    """
    apply_style()
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    n = len(stat_labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    player_vals = list(player_stats) + [player_stats[0]]
    avg_vals = list(league_avg) + [league_avg[0]]

    color = get_color(team_abbr) if team_abbr else PALETTE["dark"]

    ax.plot(angles, player_vals, color=color, linewidth=2, label=player_name)
    ax.fill(angles, player_vals, color=color, alpha=0.15)
    ax.plot(angles, avg_vals, color="#999999", linewidth=1.5, linestyle="--", label="League Avg")

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(stat_labels, fontsize=9)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.1), fontsize=9)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", pad=25)

    add_credit(fig)
    return fig, ax

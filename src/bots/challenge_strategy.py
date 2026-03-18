"""ABS Challenge Strategy Analysis.

Tracks when and how teams use their challenges to reveal strategic patterns.
Do some teams only challenge in high-leverage spots? Do others burn them early?
Are certain counts or out situations more common for challenges?
"""

import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

from src.visualization.stat_cards import (
    DARK_BG, CARD_BG, ACCENT, TEXT_WHITE, TEXT_DIM, GRID_DIM
)
from src.visualization.team_colors import get_color


def build_strategy_profiles(challenges):
    """Build strategy profiles for each team.

    Tracks challenge usage by count, outs, inning group, call type,
    and whether they challenge on close pitches vs obvious misses.

    Returns dict of team -> profile dict.
    """
    teams = defaultdict(lambda: {
        # By count (balls-strikes before the pitch)
        "by_count": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # By outs
        "by_outs": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # By inning group (early 1-3, mid 4-6, late 7-9, extras 10+)
        "by_inning_group": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # By what they challenged (strike -> ball, or ball -> strike)
        "by_call_type": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # By runners on base
        "by_runners": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # By score differential bucket (trailing, tied, leading)
        "by_score_situation": defaultdict(lambda: {"total": 0, "overturned": 0}),
        # Raw counts
        "total": 0,
        "overturned": 0,
    })

    for c in challenges:
        team = c.get("challenge_team", "")
        if not team:
            continue

        impact = c.get("impact", {})
        is_overturned = c["result"] == "overturned"

        teams[team]["total"] += 1
        if is_overturned:
            teams[team]["overturned"] += 1

        # Count
        count_str = impact.get("count_before", "?-?")
        teams[team]["by_count"][count_str]["total"] += 1
        if is_overturned:
            teams[team]["by_count"][count_str]["overturned"] += 1

        # Outs
        outs = c.get("outs")
        outs_label = str(outs) if outs is not None else "?"
        teams[team]["by_outs"][outs_label]["total"] += 1
        if is_overturned:
            teams[team]["by_outs"][outs_label]["overturned"] += 1

        # Inning group
        inning = c.get("inning", 1)
        if inning <= 3:
            group = "Early (1-3)"
        elif inning <= 6:
            group = "Mid (4-6)"
        elif inning <= 9:
            group = "Late (7-9)"
        else:
            group = "Extras (10+)"
        teams[team]["by_inning_group"][group]["total"] += 1
        if is_overturned:
            teams[team]["by_inning_group"][group]["overturned"] += 1

        # Call type
        call_code = c.get("call_code", "")
        if call_code == "C":
            call_type = "Challenged Strike"
        elif call_code == "B":
            call_type = "Challenged Ball"
        else:
            call_type = "Other"
        teams[team]["by_call_type"][call_type]["total"] += 1
        if is_overturned:
            teams[team]["by_call_type"][call_type]["overturned"] += 1

        # Runners
        runners = impact.get("runners_on", 0)
        runner_label = f"{runners} on" if runners > 0 else "Empty"
        teams[team]["by_runners"][runner_label]["total"] += 1
        if is_overturned:
            teams[team]["by_runners"][runner_label]["overturned"] += 1

        # Score situation
        away_score = c.get("away_score", 0) or 0
        home_score = c.get("home_score", 0) or 0

        if abs(away_score - home_score) == 0:
            sit = "Tied"
        elif abs(away_score - home_score) <= 2:
            sit = "Close (1-2 runs)"
        else:
            sit = "Blowout (3+)"
        teams[team]["by_score_situation"][sit]["total"] += 1
        if is_overturned:
            teams[team]["by_score_situation"][sit]["overturned"] += 1

    return dict(teams)


def generate_league_strategy_heatmap(challenges, save_path=None):
    """Heatmap showing challenge frequency and success rate by count and outs.

    Rows: count (0-0 through 3-2)
    Columns: 0 outs, 1 out, 2 outs
    Color: challenge frequency, text: success rate
    """
    # All possible counts
    counts = ["0-0", "1-0", "0-1", "2-0", "1-1", "0-2",
              "3-0", "2-1", "1-2", "3-1", "2-2", "3-2"]
    outs_labels = ["0 outs", "1 out", "2 outs"]

    # Build grid
    freq = np.zeros((len(counts), 3))
    success = np.zeros((len(counts), 3))
    totals = np.zeros((len(counts), 3))

    for c in challenges:
        impact = c.get("impact", {})
        count_str = impact.get("count_before", "")
        if count_str not in counts:
            continue

        outs_val = c.get("outs")
        if outs_val is None or outs_val > 2:
            continue

        row = counts.index(count_str)
        col = outs_val

        freq[row, col] += 1
        totals[row, col] += 1
        if c["result"] == "overturned":
            success[row, col] += 1

    # Calculate success rate (avoid div by zero)
    rate = np.divide(success, totals, out=np.zeros_like(success), where=totals > 0)

    fig, ax = plt.subplots(figsize=(8, 10), facecolor=DARK_BG)
    ax.set_facecolor(CARD_BG)

    # Plot heatmap of frequency
    im = ax.imshow(freq, cmap="YlOrRd", aspect="auto", alpha=0.7)

    # Text annotations: count / success rate
    for i in range(len(counts)):
        for j in range(3):
            total = int(totals[i, j])
            if total > 0:
                pct = rate[i, j] * 100
                ax.text(j, i, f"{total}\n{pct:.0f}%",
                        ha="center", va="center", fontsize=9,
                        color=TEXT_WHITE, fontweight="bold")
            else:
                ax.text(j, i, "-", ha="center", va="center",
                        fontsize=9, color=TEXT_DIM)

    ax.set_xticks(range(3))
    ax.set_xticklabels(outs_labels, fontsize=11, color=TEXT_WHITE)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts, fontsize=11, color=TEXT_WHITE)
    ax.set_ylabel("Count (B-S)", fontsize=12, color=TEXT_DIM)

    ax.set_title("ABS Challenges by Count & Outs\n(frequency / overturn rate)",
                 fontsize=16, fontweight="bold", color=ACCENT, pad=15)

    # Style
    ax.tick_params(colors=TEXT_DIM)
    for spine in ax.spines.values():
        spine.set_color(GRID_DIM)

    fig.text(0.95, 0.01, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_team_strategy_comparison(challenges, team_list=None,
                                       save_path=None):
    """Compare challenge strategies across teams.

    Shows side-by-side breakdown of when teams challenge:
    inning group, count bucket, score situation.
    """
    profiles = build_strategy_profiles(challenges)

    if team_list is None:
        # Top 8 teams by total challenges
        team_list = sorted(profiles.keys(),
                          key=lambda t: profiles[t]["total"], reverse=True)[:8]

    fig, axes = plt.subplots(1, 3, figsize=(20, max(7, len(team_list) * 0.8)),
                             facecolor=DARK_BG)

    fig.suptitle("ABS Challenge Strategy by Team", fontsize=20,
                 fontweight="bold", color=ACCENT, y=0.98)

    # -- Panel 1: By inning group --
    ax = axes[0]
    ax.set_facecolor(CARD_BG)
    groups = ["Early (1-3)", "Mid (4-6)", "Late (7-9)"]

    y_pos = np.arange(len(team_list))
    bar_height = 0.25

    for i, group in enumerate(groups):
        vals = []
        for team in team_list:
            p = profiles.get(team, {})
            bucket = p.get("by_inning_group", {}).get(group, {"total": 0})
            total = p.get("total", 1)
            vals.append(bucket["total"] / max(total, 1) * 100)

        colors_list = ["#22D1EE", "#FFD93D", "#FF6B6B"]
        ax.barh(y_pos + i * bar_height, vals, bar_height,
                label=group, color=colors_list[i], alpha=0.8)

    ax.set_yticks(y_pos + bar_height)
    ax.set_yticklabels(team_list, fontsize=10, color=TEXT_WHITE, fontweight="bold")
    ax.set_xlabel("% of Challenges", fontsize=10, color=TEXT_DIM)
    ax.set_title("By Inning", fontsize=13, color=TEXT_WHITE, fontweight="bold")
    ax.legend(fontsize=8, loc="lower right", facecolor=CARD_BG,
              edgecolor=GRID_DIM, labelcolor=TEXT_WHITE)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    ax.invert_yaxis()
    for spine in ax.spines.values():
        spine.set_color(GRID_DIM)

    # Color team names
    for i, label in enumerate(ax.get_yticklabels()):
        label.set_color(get_color(team_list[i]))

    # -- Panel 2: By call type --
    ax2 = axes[1]
    ax2.set_facecolor(CARD_BG)

    strike_vals = []
    ball_vals = []
    for team in team_list:
        p = profiles.get(team, {})
        total = max(p.get("total", 1), 1)
        s = p.get("by_call_type", {}).get("Challenged Strike", {"total": 0})["total"]
        b = p.get("by_call_type", {}).get("Challenged Ball", {"total": 0})["total"]
        strike_vals.append(s / total * 100)
        ball_vals.append(b / total * 100)

    ax2.barh(y_pos - 0.15, strike_vals, 0.3, label="Challenged Strike",
             color="#FF6B6B", alpha=0.8)
    ax2.barh(y_pos + 0.15, ball_vals, 0.3, label="Challenged Ball",
             color="#4CAF50", alpha=0.8)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(team_list, fontsize=10, color=TEXT_WHITE, fontweight="bold")
    ax2.set_xlabel("% of Challenges", fontsize=10, color=TEXT_DIM)
    ax2.set_title("Strike vs Ball Challenges", fontsize=13,
                  color=TEXT_WHITE, fontweight="bold")
    ax2.legend(fontsize=8, loc="lower right", facecolor=CARD_BG,
               edgecolor=GRID_DIM, labelcolor=TEXT_WHITE)
    ax2.tick_params(colors=TEXT_DIM, labelsize=9)
    ax2.invert_yaxis()
    for spine in ax2.spines.values():
        spine.set_color(GRID_DIM)

    for i, label in enumerate(ax2.get_yticklabels()):
        label.set_color(get_color(team_list[i]))

    # -- Panel 3: By score situation --
    ax3 = axes[2]
    ax3.set_facecolor(CARD_BG)

    situations = ["Tied", "Close (1-2 runs)", "Blowout (3+)"]
    sit_colors = ["#22D1EE", "#FFD93D", "#FF6B6B"]

    for i, sit in enumerate(situations):
        vals = []
        for team in team_list:
            p = profiles.get(team, {})
            total = max(p.get("total", 1), 1)
            bucket = p.get("by_score_situation", {}).get(sit, {"total": 0})
            vals.append(bucket["total"] / total * 100)

        ax3.barh(y_pos + i * bar_height, vals, bar_height,
                 label=sit, color=sit_colors[i], alpha=0.8)

    ax3.set_yticks(y_pos + bar_height)
    ax3.set_yticklabels(team_list, fontsize=10, color=TEXT_WHITE, fontweight="bold")
    ax3.set_xlabel("% of Challenges", fontsize=10, color=TEXT_DIM)
    ax3.set_title("By Game Situation", fontsize=13,
                  color=TEXT_WHITE, fontweight="bold")
    ax3.legend(fontsize=8, loc="lower right", facecolor=CARD_BG,
               edgecolor=GRID_DIM, labelcolor=TEXT_WHITE)
    ax3.tick_params(colors=TEXT_DIM, labelsize=9)
    ax3.invert_yaxis()
    for spine in ax3.spines.values():
        spine.set_color(GRID_DIM)

    for i, label in enumerate(ax3.get_yticklabels()):
        label.set_color(get_color(team_list[i]))

    fig.text(0.98, 0.01, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    plt.tight_layout(rect=[0.02, 0.02, 1, 0.95])

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_count_strategy_table(challenges, save_path=None):
    """Table showing each team's most common challenge count.

    Reveals if teams tend to challenge on hitter's counts, pitcher's counts,
    or neutral counts.
    """
    profiles = build_strategy_profiles(challenges)

    # Classify counts
    hitter_counts = {"1-0", "2-0", "3-0", "2-1", "3-1"}
    pitcher_counts = {"0-1", "0-2", "1-2", "2-2"}
    neutral_counts = {"0-0", "1-1", "3-2"}

    rows = []
    for team in sorted(profiles.keys()):
        p = profiles[team]
        total = max(p["total"], 1)
        by_count = p["by_count"]

        hitter_n = sum(by_count.get(c, {"total": 0})["total"] for c in hitter_counts)
        pitcher_n = sum(by_count.get(c, {"total": 0})["total"] for c in pitcher_counts)
        neutral_n = sum(by_count.get(c, {"total": 0})["total"] for c in neutral_counts)

        # Most common specific count
        if by_count:
            top_count = max(by_count.items(), key=lambda x: x[1]["total"])
            top_count_str = f"{top_count[0]} ({top_count[1]['total']})"
        else:
            top_count_str = "-"

        # Success rate by count type
        hitter_w = sum(by_count.get(c, {"overturned": 0})["overturned"] for c in hitter_counts)
        pitcher_w = sum(by_count.get(c, {"overturned": 0})["overturned"] for c in pitcher_counts)

        rows.append({
            "team": team,
            "total": p["total"],
            "hitter_pct": hitter_n / total * 100,
            "pitcher_pct": pitcher_n / total * 100,
            "neutral_pct": neutral_n / total * 100,
            "hitter_success": hitter_w / max(hitter_n, 1) * 100,
            "pitcher_success": pitcher_w / max(pitcher_n, 1) * 100,
            "top_count": top_count_str,
            "success_rate": p["overturned"] / total * 100,
        })

    # Sort by hitter count % (aggressive strategy = more hitter count challenges)
    rows.sort(key=lambda r: r["hitter_pct"], reverse=True)

    fig = plt.figure(figsize=(14, max(6, 2 + len(rows) * 0.5)), facecolor=DARK_BG)

    fig.text(0.5, 0.97, "ABS Challenge Count Strategy by Team",
             fontsize=18, fontweight="bold", color=ACCENT, ha="center", va="top")
    fig.text(0.5, 0.935,
             "Hitter counts: 1-0, 2-0, 3-0, 2-1, 3-1  |  "
             "Pitcher counts: 0-1, 0-2, 1-2, 2-2",
             fontsize=10, color=TEXT_DIM, ha="center", va="top")

    col_labels = ["Team", "#", "Hitter Ct%", "Pitcher Ct%", "Neutral%",
                  "HC Win%", "PC Win%", "Top Count", "Overall Win%"]
    table_rows = []
    for r in rows:
        table_rows.append([
            r["team"],
            str(r["total"]),
            f"{r['hitter_pct']:.0f}%",
            f"{r['pitcher_pct']:.0f}%",
            f"{r['neutral_pct']:.0f}%",
            f"{r['hitter_success']:.0f}%",
            f"{r['pitcher_success']:.0f}%",
            r["top_count"],
            f"{r['success_rate']:.0f}%",
        ])

    ax = fig.add_axes([0.03, 0.03, 0.94, 0.87])
    ax.axis("off")
    ax.set_facecolor(DARK_BG)

    table = ax.table(
        cellText=table_rows, colLabels=col_labels,
        loc="upper center", cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.7)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(GRID_DIM)
        if row == 0:
            cell.set_text_props(color=ACCENT, fontweight="bold")
            cell.set_facecolor("#1A2535")
        else:
            cell.set_facecolor(CARD_BG if row % 2 == 1 else "#1E2840")
            cell.set_text_props(color=TEXT_WHITE)

            if col == 0 and row > 0:
                team_abbr = table_rows[row - 1][0]
                cell.set_text_props(color=get_color(team_abbr), fontweight="bold")

    fig.text(0.97, 0.005, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig

"""ABS Challenge Leaderboards - team and umpire rankings.

Generates weekly, monthly, and YTD leaderboards for:
- Teams: ranked by total impact value gained from successful challenges
- Umpires: ranked by overturn rate (most/least accurate)
"""

import matplotlib.pyplot as plt
from collections import defaultdict

from src.visualization.stat_cards import (
    DARK_BG, CARD_BG, ACCENT, TEXT_WHITE, TEXT_DIM, GRID_DIM
)
from src.visualization.team_colors import get_color


def filter_by_date_range(challenges, start_date, end_date):
    """Filter challenges by their game date.

    Args:
        challenges: list of challenge dicts
        start_date: string in YYYY-MM-DD format
        end_date: string in YYYY-MM-DD format

    Returns:
        filtered list of challenges
    """
    return [c for c in challenges
            if start_date <= c.get("date", "") <= end_date]


def aggregate_team_stats(challenges):
    """Aggregate challenge data by team.

    Returns dict of team_abbr -> stats dict.
    """
    teams = defaultdict(lambda: {
        "challenges": 0,
        "overturned": 0,
        "upheld": 0,
        "impact_gained": 0.0,      # sum of impact scores from successful challenges
        "impact_wasted": 0.0,      # sum of impact scores from failed challenges
        "high_leverage_wins": 0,   # overturned challenges with impact >= 50
        "games_with_challenges": set(),
    })

    for c in challenges:
        team = c.get("challenge_team", "")
        if not team:
            continue

        teams[team]["challenges"] += 1
        teams[team]["games_with_challenges"].add(c.get("game_id"))

        impact_score = c.get("impact", {}).get("impact_score", 0)

        if c["result"] == "overturned":
            teams[team]["overturned"] += 1
            teams[team]["impact_gained"] += impact_score
            if impact_score >= 50:
                teams[team]["high_leverage_wins"] += 1
        else:
            teams[team]["upheld"] += 1
            teams[team]["impact_wasted"] += impact_score

    # Calculate derived stats
    for team, stats in teams.items():
        stats["success_rate"] = stats["overturned"] / max(stats["challenges"], 1) * 100
        stats["avg_impact_per_win"] = stats["impact_gained"] / max(stats["overturned"], 1)
        stats["games"] = len(stats["games_with_challenges"])
        stats["challenges_per_game"] = stats["challenges"] / max(stats["games"], 1)
        # Net value: impact gained minus opportunity cost of failed challenges
        stats["net_value"] = stats["impact_gained"] - stats["impact_wasted"] * 0.3
        # Convert set to count for JSON serialization
        stats["games_with_challenges"] = stats["games"]

    return dict(teams)


def aggregate_umpire_stats(challenges):
    """Aggregate challenge data by umpire.

    Returns dict of umpire_name -> stats dict.
    """
    umps = defaultdict(lambda: {
        "challenges_faced": 0,
        "overturned": 0,
        "upheld": 0,
        "games": set(),
        "total_impact": 0.0,
    })

    for c in challenges:
        ump = c.get("umpire", "Unknown")
        umps[ump]["challenges_faced"] += 1
        umps[ump]["games"].add(c.get("game_id"))
        umps[ump]["total_impact"] += c.get("impact", {}).get("impact_score", 0)

        if c["result"] == "overturned":
            umps[ump]["overturned"] += 1
        else:
            umps[ump]["upheld"] += 1

    for ump, stats in umps.items():
        stats["overturn_rate"] = stats["overturned"] / max(stats["challenges_faced"], 1) * 100
        stats["accuracy"] = stats["upheld"] / max(stats["challenges_faced"], 1) * 100
        stats["games_count"] = len(stats["games"])
        stats["challenges_per_game"] = stats["challenges_faced"] / max(len(stats["games"]), 1)
        stats["games"] = len(stats["games"])

    return dict(umps)


def generate_team_leaderboard(challenges, period_label="YTD", save_path=None):
    """Generate team ABS challenge leaderboard image.

    Ranked by net value (impact gained from overturns minus wasted challenges).
    """
    team_stats = aggregate_team_stats(challenges)

    # Sort by net_value descending
    ranked = sorted(team_stats.items(), key=lambda x: x[1]["net_value"], reverse=True)

    n_teams = len(ranked)
    fig = plt.figure(figsize=(14, max(8, 3 + n_teams * 0.55)), facecolor=DARK_BG)

    # Header
    fig.text(0.5, 0.97, f"ABS Challenge Team Rankings - {period_label}",
             fontsize=22, fontweight="bold", color=ACCENT, ha="center", va="top")

    total = sum(s["challenges"] for _, s in ranked)
    total_overturned = sum(s["overturned"] for _, s in ranked)
    fig.text(0.5, 0.935,
             f"{total} total challenges | {total_overturned} overturned | "
             f"{total_overturned / max(total, 1) * 100:.0f}% league overturn rate",
             fontsize=12, color=TEXT_DIM, ha="center", va="top")

    if ranked:
        col_labels = ["Rank", "Team", "Used", "W", "L", "Win%",
                      "Impact Gained", "High Lev W", "Net Value"]
        rows = []
        for i, (team, stats) in enumerate(ranked):
            rows.append([
                str(i + 1),
                team,
                str(stats["challenges"]),
                str(stats["overturned"]),
                str(stats["upheld"]),
                f"{stats['success_rate']:.0f}%",
                f"{stats['impact_gained']:.0f}",
                str(stats["high_leverage_wins"]),
                f"{stats['net_value']:.0f}",
            ])

        ax = fig.add_axes([0.03, 0.03, 0.94, 0.87])
        ax.axis("off")
        ax.set_facecolor(DARK_BG)

        table = ax.table(
            cellText=rows, colLabels=col_labels,
            loc="upper center", cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.7)

        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
                cell.set_facecolor("#1A2535")
            else:
                # Alternate row colors
                cell.set_facecolor(CARD_BG if row % 2 == 1 else "#1E2840")
                cell.set_text_props(color=TEXT_WHITE)

                # Team column - use team color
                if col == 1 and row > 0:
                    team_abbr = rows[row - 1][1]
                    team_color = get_color(team_abbr)
                    cell.set_text_props(color=team_color, fontweight="bold")

                # Win% column - color by performance
                if col == 5 and row > 0:
                    pct = float(rows[row - 1][5].replace("%", ""))
                    if pct >= 70:
                        cell.set_text_props(color="#44FF44", fontweight="bold")
                    elif pct >= 50:
                        cell.set_text_props(color="#FFD93D")
                    else:
                        cell.set_text_props(color="#FF6B6B")

                # Net Value column - color gradient
                if col == 8 and row > 0:
                    val = float(rows[row - 1][8])
                    if val >= 100:
                        cell.set_text_props(color="#44FF44", fontweight="bold")
                    elif val >= 50:
                        cell.set_text_props(color="#FFD93D", fontweight="bold")
                    elif val <= 0:
                        cell.set_text_props(color="#FF6B6B")

    fig.text(0.97, 0.005, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_umpire_leaderboard(challenges, period_label="YTD",
                                 min_challenges=3, save_path=None):
    """Generate umpire accuracy leaderboard image.

    Shows umpires ranked by overturn rate (most overturned = least accurate).
    """
    umpire_stats = aggregate_umpire_stats(challenges)

    # Filter to umpires with minimum challenges
    qualified = {u: s for u, s in umpire_stats.items()
                 if s["challenges_faced"] >= min_challenges}

    # Sort by overturn rate descending (worst accuracy first)
    ranked = sorted(qualified.items(),
                    key=lambda x: x[1]["overturn_rate"], reverse=True)

    n = len(ranked)
    fig = plt.figure(figsize=(12, max(6, 3 + n * 0.5)), facecolor=DARK_BG)

    fig.text(0.5, 0.97, f"Umpire ABS Challenge Accuracy - {period_label}",
             fontsize=20, fontweight="bold", color=ACCENT, ha="center", va="top")
    fig.text(0.5, 0.935, f"Minimum {min_challenges} challenges faced",
             fontsize=11, color=TEXT_DIM, ha="center", va="top")

    if ranked:
        col_labels = ["Rank", "Umpire", "Games", "Faced", "Overturned",
                      "Upheld", "Overturn %", "Accuracy %"]
        rows = []
        for i, (ump, stats) in enumerate(ranked):
            rows.append([
                str(i + 1),
                ump,
                str(stats["games"]),
                str(stats["challenges_faced"]),
                str(stats["overturned"]),
                str(stats["upheld"]),
                f"{stats['overturn_rate']:.0f}%",
                f"{stats['accuracy']:.0f}%",
            ])

        ax = fig.add_axes([0.03, 0.03, 0.94, 0.87])
        ax.axis("off")
        ax.set_facecolor(DARK_BG)

        table = ax.table(
            cellText=rows, colLabels=col_labels,
            loc="upper center", cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.7)

        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
                cell.set_facecolor("#1A2535")
            else:
                cell.set_facecolor(CARD_BG if row % 2 == 1 else "#1E2840")
                cell.set_text_props(color=TEXT_WHITE)

                # Color overturn % (higher = worse for umpire)
                if col == 6 and row > 0:
                    pct = float(rows[row - 1][6].replace("%", ""))
                    if pct >= 70:
                        cell.set_text_props(color="#FF6B6B", fontweight="bold")
                    elif pct >= 50:
                        cell.set_text_props(color="#FFD93D")
                    else:
                        cell.set_text_props(color="#44FF44")

                # Color accuracy (inverse)
                if col == 7 and row > 0:
                    pct = float(rows[row - 1][7].replace("%", ""))
                    if pct >= 70:
                        cell.set_text_props(color="#44FF44", fontweight="bold")
                    elif pct >= 50:
                        cell.set_text_props(color="#FFD93D")
                    else:
                        cell.set_text_props(color="#FF6B6B")

    fig.text(0.97, 0.005, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_team_bar_chart(challenges, period_label="YTD",
                            metric="net_value", save_path=None):
    """Horizontal bar chart of teams ranked by a metric.

    Cleaner visual for social media than a table.
    """
    team_stats = aggregate_team_stats(challenges)
    ranked = sorted(team_stats.items(), key=lambda x: x[1][metric], reverse=True)

    fig, ax = plt.subplots(figsize=(10, max(6, len(ranked) * 0.45)),
                           facecolor=DARK_BG)
    ax.set_facecolor(DARK_BG)

    teams = [t for t, _ in ranked]
    values = [s[metric] for _, s in ranked]
    colors = [get_color(t) for t in teams]

    y_pos = range(len(teams))
    bars = ax.barh(y_pos, values, color=colors, alpha=0.85, height=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(teams, fontsize=11, color=TEXT_WHITE, fontweight="bold")
    ax.invert_yaxis()

    # Value labels on bars
    for i, (bar, val) in enumerate(zip(bars, values)):
        label = f"{val:.0f}"
        x_pos = bar.get_width() + max(values) * 0.02
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                label, fontsize=9, color=TEXT_DIM, va="center")

    # Style
    ax.set_xlabel("Net Challenge Value", fontsize=11, color=TEXT_DIM)
    ax.tick_params(axis="x", colors=TEXT_DIM, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(GRID_DIM)
    ax.spines["left"].set_color(GRID_DIM)

    metric_labels = {
        "net_value": "Net Challenge Value",
        "impact_gained": "Total Impact Gained",
        "overturned": "Successful Challenges",
        "success_rate": "Challenge Success Rate (%)",
    }
    metric_name = metric_labels.get(metric, metric)

    ax.set_title(f"ABS Challenge Rankings: {metric_name} - {period_label}",
                 fontsize=16, fontweight="bold", color=ACCENT, pad=15)

    fig.text(0.97, 0.01, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig

"""ABS Challenge Bot - posts every ball/strike challenge with a viz.

Monitors live MLB game feeds for ABS (Automated Ball-Strike) challenge events.
When a challenge is detected, generates a pitch location image and posts it.
Also generates daily summaries and weekly umpire leaderboards.

ABS Challenge System (2026):
- Each team starts with 2 challenges (successful challenges are returned)
- Hawk-Eye system determines if pitch was ball or strike
- Umpire's call is overturned or upheld within seconds
- reviewDetails appears at both event-level (on the pitch) and play-level

API Structure:
- gameData.absChallenges: team-level counts (usedSuccessful, usedFailed, remaining)
- playEvents[].reviewDetails: individual challenge on a specific pitch
- allPlays[].reviewDetails: challenge at the at-bat level
- reviewDetails keys: isOverturned, inProgress, reviewType ("MJ"), challengeTeamId, player
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import date
import statsapi

from src.visualization.stat_cards import (
    DARK_BG, CARD_BG, ACCENT, TEXT_WHITE, TEXT_DIM, GRID_DIM, PITCH_COLORS
)
from src.visualization.team_colors import get_color
from src.bots.challenge_impact import calculate_challenge_impact, rank_challenges_by_impact


def find_challenges_in_game(game_id):
    """Find all ABS challenges in a completed or live game.

    Returns list of challenge dicts with full context.
    """
    feed = statsapi.get("game", {"gamePk": game_id})
    teams = feed["gameData"]["teams"]
    away_id = teams["away"]["id"]
    away_abbr = teams["away"]["abbreviation"]
    home_abbr = teams["home"]["abbreviation"]
    game_date = feed["gameData"]["datetime"]["officialDate"]

    # Get umpire
    umpire_hp = "Unknown"
    for ump in feed["liveData"].get("boxscore", {}).get("officials", []):
        if ump.get("officialType") == "Home Plate":
            umpire_hp = ump.get("official", {}).get("fullName", "Unknown")
            break

    plays = feed["liveData"]["plays"]["allPlays"]
    challenges = []
    seen_challenges = set()

    for play in plays:
        matchup = play.get("matchup", {})
        about = play.get("about", {})
        batter = matchup.get("batter", {}).get("fullName", "Unknown")
        batter_id = matchup.get("batter", {}).get("id")
        pitcher = matchup.get("pitcher", {}).get("fullName", "Unknown")
        pitcher_id = matchup.get("pitcher", {}).get("id")

        # Event-level challenges (on a specific pitch)
        for ev in play.get("playEvents", []):
            review = ev.get("reviewDetails")
            if not review:
                continue

            details = ev.get("details", {})
            pitch_data = ev.get("pitchData", {})
            coords = pitch_data.get("coordinates", {})
            pitch_type_info = details.get("type", {})

            team_id = review.get("challengeTeamId")
            challenge_team = away_abbr if team_id == away_id else home_abbr

            # Score at time of challenge (scores live in play result, not about)
            play_result = play.get("result", {})
            away_score = play_result.get("awayScore", 0)
            home_score = play_result.get("homeScore", 0)

            # Count at time of pitch
            ev_count = ev.get("count", {})

            challenge_dict = {
                "source": "event",
                "game_id": game_id,
                "date": game_date,
                "away": away_abbr,
                "home": home_abbr,
                "inning": about.get("inning"),
                "half": about.get("halfInning"),
                "batter": batter,
                "batter_id": batter_id,
                "pitcher": pitcher,
                "pitcher_id": pitcher_id,
                "umpire": umpire_hp,
                "original_call": details.get("description", ""),
                "call_code": details.get("code", ""),
                "result": "overturned" if review.get("isOverturned") else "upheld",
                "challenge_team": challenge_team,
                "pX": coords.get("pX"),
                "pZ": coords.get("pZ"),
                "sz_top": pitch_data.get("strikeZoneTop"),
                "sz_bottom": pitch_data.get("strikeZoneBottom"),
                "zone": pitch_data.get("zone"),
                "pitch_type": pitch_type_info.get("code", ""),
                "pitch_name": pitch_type_info.get("description", ""),
                "speed": pitch_data.get("startSpeed"),
                "away_score": away_score,
                "home_score": home_score,
                "balls": ev_count.get("balls"),
                "strikes": ev_count.get("strikes"),
                "outs": ev_count.get("outs"),
            }

            # Calculate impact
            challenge_dict["impact"] = calculate_challenge_impact(
                challenge_dict, play_data=play
            )
            challenges.append(challenge_dict)

            # Track this challenge to avoid duplicates from play-level scan
            challenge_key = (game_id, about.get("inning"), batter_id)
            seen_challenges.add(challenge_key)

        # Play-level challenges (at-bat level)
        play_review = play.get("reviewDetails")
        if play_review:
            # Skip if already captured at event-level
            challenge_key = (game_id, about.get("inning"), batter_id)
            if challenge_key in seen_challenges:
                continue

            team_id = play_review.get("challengeTeamId")
            challenge_team = away_abbr if team_id == away_id else home_abbr

            # Get the challenged pitch (last pitch with location data)
            last_pitch = None
            for ev in reversed(play.get("playEvents", [])):
                if ev.get("isPitch") and ev.get("pitchData", {}).get("coordinates", {}).get("pX") is not None:
                    last_pitch = ev
                    break

            if last_pitch:
                details = last_pitch.get("details", {})
                pitch_data = last_pitch.get("pitchData", {})
                coords = pitch_data.get("coordinates", {})
                pitch_type_info = details.get("type", {})
            else:
                details = {}
                pitch_data = {}
                coords = {}
                pitch_type_info = {}

            play_result = play.get("result", {})
            away_score = play_result.get("awayScore", 0)
            home_score = play_result.get("homeScore", 0)

            # Get count from the last pitch event
            lp_count = last_pitch.get("count", {}) if last_pitch else {}

            challenge_dict = {
                "source": "play",
                "game_id": game_id,
                "date": game_date,
                "away": away_abbr,
                "home": home_abbr,
                "inning": about.get("inning"),
                "half": about.get("halfInning"),
                "batter": batter,
                "batter_id": batter_id,
                "pitcher": pitcher,
                "pitcher_id": pitcher_id,
                "umpire": umpire_hp,
                "original_call": details.get("description", ""),
                "call_code": details.get("code", ""),
                "result": "overturned" if play_review.get("isOverturned") else "upheld",
                "challenge_team": challenge_team,
                "pX": coords.get("pX"),
                "pZ": coords.get("pZ"),
                "sz_top": pitch_data.get("strikeZoneTop"),
                "sz_bottom": pitch_data.get("strikeZoneBottom"),
                "zone": pitch_data.get("zone"),
                "pitch_type": pitch_type_info.get("code", ""),
                "pitch_name": pitch_type_info.get("description", ""),
                "speed": pitch_data.get("startSpeed"),
                "away_score": away_score,
                "home_score": home_score,
                "balls": lp_count.get("balls"),
                "strikes": lp_count.get("strikes"),
                "outs": lp_count.get("outs"),
            }

            challenge_dict["impact"] = calculate_challenge_impact(
                challenge_dict, play_data=play
            )
            challenges.append(challenge_dict)

    return challenges


def find_all_challenges_for_date(target_date=None):
    """Find all ABS challenges across all games for a given date."""
    if target_date is None:
        target_date = date.today()

    date_str = target_date.strftime("%m/%d/%Y")
    schedule = statsapi.schedule(start_date=date_str, end_date=date_str)
    final_games = [g for g in schedule if g["status"] == "Final"]

    all_challenges = []
    for game in final_games:
        challenges = find_challenges_in_game(game["game_id"])
        all_challenges.extend(challenges)

    return all_challenges


def generate_challenge_image(challenge, save_path=None):
    """Generate a single-image viz of one ABS challenge.

    Shows the strike zone with the challenged pitch dot, batter/pitcher info,
    umpire, original call, and the ABS result.
    """
    fig, ax = plt.subplots(figsize=(6, 8), facecolor=DARK_BG)
    ax.set_facecolor(CARD_BG)

    # Strike zone dimensions
    sz_top = challenge.get("sz_top") or 3.5
    sz_bot = challenge.get("sz_bottom") or 1.5
    plate_w = 17 / 12  # 17 inches in feet

    # Zone rectangle
    zone = patches.Rectangle(
        (-plate_w / 2, sz_bot), plate_w, sz_top - sz_bot,
        linewidth=2.5, edgecolor=TEXT_WHITE, facecolor="none"
    )
    ax.add_patch(zone)

    # Inner grid (9 zones)
    tw = plate_w / 3
    th = (sz_top - sz_bot) / 3
    for i in range(1, 3):
        ax.plot([-plate_w / 2, plate_w / 2], [sz_bot + th * i, sz_bot + th * i],
                color=GRID_DIM, linewidth=0.8, linestyle="--")
        ax.plot([-plate_w / 2 + tw * i, -plate_w / 2 + tw * i], [sz_bot, sz_top],
                color=GRID_DIM, linewidth=0.8, linestyle="--")

    # Home plate
    plate_y = sz_bot - 0.3
    plate = plt.Polygon(
        [[-plate_w / 2, plate_y + 0.1], [0, plate_y - 0.05],
         [plate_w / 2, plate_y + 0.1], [plate_w / 2, plate_y + 0.15],
         [-plate_w / 2, plate_y + 0.15]],
        closed=True, facecolor="#555555", edgecolor=TEXT_DIM, linewidth=1
    )
    ax.add_patch(plate)

    # Pitch dot
    px = challenge.get("pX") or 0
    pz = challenge.get("pZ") or 2.5
    result = challenge.get("result", "upheld")

    if result == "overturned":
        dot_color = "#FF4444"
        result_text = "OVERTURNED"
    else:
        dot_color = "#44FF44"
        result_text = "UPHELD"

    # Pitch type color for the dot ring
    ptype_color = PITCH_COLORS.get(challenge.get("pitch_type", ""), "#FFFFFF")

    ax.scatter(px, pz, s=400, c=dot_color, edgecolors="white",
               linewidth=2.5, zorder=10)

    # Speed label below dot
    speed = challenge.get("speed")
    pname = challenge.get("pitch_name", "")
    if speed:
        ax.text(px, pz - 0.22, f"{pname}\n{speed:.0f} mph", fontsize=8,
                color=TEXT_DIM, ha="center", va="top", linespacing=1.3)

    # Axis setup
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(sz_bot - 0.8, sz_top + 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    # -- Text overlays --

    # Title
    half_str = "Top" if challenge.get("half") == "top" else "Bot"
    inning = challenge.get("inning", "?")
    fig.text(0.5, 0.96, "ABS CHALLENGE", fontsize=20, fontweight="bold",
             color=ACCENT, ha="center", va="top")

    # Game + inning
    away = challenge.get("away", "")
    home = challenge.get("home", "")
    fig.text(0.5, 0.92, f"{away} @ {home} - {half_str} {inning}",
             fontsize=12, color=TEXT_DIM, ha="center", va="top")

    # Team color bars
    away_color = get_color(away) if away else "#333"
    home_color = get_color(home) if home else "#333"
    fig.patches.append(patches.Rectangle(
        (0.0, 0.98), 0.5, 0.02, transform=fig.transFigure,
        facecolor=away_color, edgecolor="none"
    ))
    fig.patches.append(patches.Rectangle(
        (0.5, 0.98), 0.5, 0.02, transform=fig.transFigure,
        facecolor=home_color, edgecolor="none"
    ))

    # Matchup
    batter = challenge.get("batter", "")
    pitcher = challenge.get("pitcher", "")
    fig.text(0.05, 0.14, f"Batter: {batter}", fontsize=11,
             color=TEXT_WHITE, va="top")
    fig.text(0.05, 0.10, f"Pitcher: {pitcher}", fontsize=11,
             color=TEXT_WHITE, va="top")
    fig.text(0.05, 0.06, f"HP Umpire: {challenge.get('umpire', 'Unknown')}",
             fontsize=10, color=TEXT_DIM, va="top")

    # Original call
    call = challenge.get("original_call", "")
    challenge_team = challenge.get("challenge_team", "")
    fig.text(0.05, 0.02, f"Call: {call} | Challenged by {challenge_team}",
             fontsize=9, color=TEXT_DIM, va="top")

    # Result (big, right-aligned)
    fig.text(0.95, 0.08, result_text, fontsize=24, fontweight="bold",
             color=dot_color, ha="right", va="center")

    # Brand
    fig.text(0.95, 0.02, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="top")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_daily_summary(challenges, target_date=None, save_path=None):
    """Generate a daily summary image with top impact challenges highlighted.

    Page 1 (top section): headline stats + top 5 highest-impact challenges
    Page 2 (bottom section): full table of all challenges
    """
    if target_date is None:
        target_date = date.today()

    n = len(challenges)
    overturned = sum(1 for c in challenges if c["result"] == "overturned")
    upheld = n - overturned
    success_rate = overturned / max(n, 1) * 100

    # Rank by impact
    ranked = rank_challenges_by_impact(challenges)
    top_challenges = ranked[:5]

    fig = plt.figure(figsize=(12, max(10, 5 + n * 0.4)), facecolor=DARK_BG)

    # -- HEADER --
    date_str = target_date.strftime("%B %d, %Y")
    fig.text(0.5, 0.97, "ABS Challenge Daily Report", fontsize=22,
             fontweight="bold", color=ACCENT, ha="center", va="top")
    fig.text(0.5, 0.945, date_str, fontsize=12, color=TEXT_DIM,
             ha="center", va="top")

    fig.text(0.5, 0.92,
             f"{n} Challenges  |  {overturned} Overturned  |  {upheld} Upheld  |  {success_rate:.0f}% Overturn Rate",
             fontsize=13, color=TEXT_WHITE, ha="center", va="top")

    # -- TOP IMPACT CHALLENGES --
    if top_challenges:
        fig.text(0.05, 0.89, "Biggest Impact Challenges", fontsize=14,
                 fontweight="bold", color=ACCENT, va="top")

        top_col_labels = ["#", "Game", "Inn", "Score", "Count", "Batter", "Pitcher",
                          "Call", "Result", "Impact"]
        top_rows = []
        for i, c in enumerate(top_challenges):
            half = "T" if c.get("half") == "top" else "B"
            impact = c.get("impact", {})
            score = f"{c.get('away_score', 0)}-{c.get('home_score', 0)}"
            count_str = impact.get("count_before", "?")

            top_rows.append([
                str(i + 1),
                f"{c['away']}@{c['home']}",
                f"{half}{c['inning']}",
                score,
                count_str,
                c["batter"].split()[-1],
                c["pitcher"].split()[-1],
                c["original_call"][:12],
                c["result"].upper(),
                f"{impact.get('impact_score', 0):.0f}",
            ])

        # Top challenges table takes ~35% of the figure
        ax_top = fig.add_axes([0.03, 0.58, 0.94, 0.28])
        ax_top.axis("off")
        ax_top.set_facecolor(DARK_BG)

        top_table = ax_top.table(
            cellText=top_rows, colLabels=top_col_labels,
            loc="upper center", cellLoc="center",
        )
        top_table.auto_set_font_size(False)
        top_table.set_fontsize(9)
        top_table.scale(1, 1.8)

        for (row, col), cell in top_table.get_celld().items():
            cell.set_facecolor(CARD_BG if row % 2 == 0 else "#1E2840")
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
                cell.set_facecolor("#1A2535")
            else:
                cell.set_text_props(color=TEXT_WHITE)
                # Color result column
                if col == 8 and row > 0:
                    val = top_rows[row - 1][8]
                    color = "#FF4444" if val == "OVERTURNED" else "#44FF44"
                    cell.set_text_props(color=color, fontweight="bold")
                # Color impact score
                if col == 9 and row > 0:
                    score_val = float(top_rows[row - 1][9])
                    if score_val >= 60:
                        cell.set_text_props(color="#FF6B6B", fontweight="bold")
                    elif score_val >= 30:
                        cell.set_text_props(color="#FFD93D", fontweight="bold")

    # -- FULL TABLE --
    if challenges:
        fig.text(0.05, 0.55, "All Challenges", fontsize=14,
                 fontweight="bold", color=ACCENT, va="top")

        col_labels = ["Game", "Inn", "Batter", "Pitcher", "Ump", "Call", "Team", "Result"]
        rows = []
        for c in challenges:
            half = "T" if c.get("half") == "top" else "B"
            rows.append([
                f"{c['away']}@{c['home']}",
                f"{half}{c['inning']}",
                c["batter"].split()[-1],
                c["pitcher"].split()[-1],
                c["umpire"].split()[-1] if c.get("umpire") else "?",
                c["original_call"][:12],
                c["challenge_team"],
                c["result"].upper(),
            ])

        ax = fig.add_axes([0.03, 0.03, 0.94, 0.49])
        ax.axis("off")
        ax.set_facecolor(DARK_BG)

        table = ax.table(
            cellText=rows, colLabels=col_labels,
            loc="upper center", cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)

        for (row, col), cell in table.get_celld().items():
            cell.set_facecolor(CARD_BG)
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
            else:
                cell.set_text_props(color=TEXT_WHITE)
                if col == 7 and row > 0:
                    val = rows[row - 1][7]
                    color = "#FF4444" if val == "OVERTURNED" else "#44FF44"
                    cell.set_text_props(color=color, fontweight="bold")

    fig.text(0.97, 0.005, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def generate_weekly_umpire_leaderboard(challenges_by_date, save_path=None):
    """Generate weekly umpire leaderboard showing overturn rates.

    Args:
        challenges_by_date: dict of date -> list of challenges
    """
    # Aggregate by umpire
    umpire_stats = {}
    for dt, challenges in challenges_by_date.items():
        for c in challenges:
            ump = c.get("umpire", "Unknown")
            if ump not in umpire_stats:
                umpire_stats[ump] = {"total": 0, "overturned": 0}
            umpire_stats[ump]["total"] += 1
            if c["result"] == "overturned":
                umpire_stats[ump]["overturned"] += 1

    # Sort by most overturned
    ranked = sorted(umpire_stats.items(),
                    key=lambda x: x[1]["overturned"], reverse=True)

    fig = plt.figure(figsize=(10, max(5, 2 + len(ranked) * 0.5)), facecolor=DARK_BG)

    fig.text(0.5, 0.96, "Weekly ABS Challenge Leaderboard",
             fontsize=18, fontweight="bold", color=ACCENT, ha="center", va="top")
    fig.text(0.5, 0.91, "Umpires by Challenges Faced (Most Overturned)",
             fontsize=12, color=TEXT_DIM, ha="center", va="top")

    if ranked:
        col_labels = ["Rank", "Umpire", "Total", "Overturned", "Upheld", "Overturn %"]
        rows = []
        for i, (ump, stats) in enumerate(ranked):
            upheld = stats["total"] - stats["overturned"]
            pct = stats["overturned"] / max(stats["total"], 1) * 100
            rows.append([
                str(i + 1),
                ump,
                str(stats["total"]),
                str(stats["overturned"]),
                str(upheld),
                f"{pct:.0f}%",
            ])

        ax = fig.add_axes([0.05, 0.03, 0.9, 0.82])
        ax.axis("off")
        ax.set_facecolor(DARK_BG)

        table = ax.table(
            cellText=rows, colLabels=col_labels,
            loc="upper center", cellLoc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.8)

        for (row, col), cell in table.get_celld().items():
            cell.set_facecolor(CARD_BG)
            cell.set_edgecolor(GRID_DIM)
            if row == 0:
                cell.set_text_props(color=ACCENT, fontweight="bold")
            else:
                cell.set_text_props(color=TEXT_WHITE)

    fig.text(0.95, 0.01, "@sabrmagician", fontsize=9,
             color=TEXT_DIM, ha="right", va="bottom")

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=200, bbox_inches="tight")

    return fig


def build_challenge_tweet(challenge):
    """Build tweet text for a single ABS challenge."""
    result = "OVERTURNED" if challenge["result"] == "overturned" else "UPHELD"
    half = "Top" if challenge.get("half") == "top" else "Bot"

    lines = [
        f"ABS Challenge: {result}",
        "",
        f"{challenge['away']} @ {challenge['home']} - {half} {challenge['inning']}",
        f"Batter: {challenge['batter']}",
        f"Pitcher: {challenge['pitcher']}",
        f"HP Umpire: {challenge['umpire']}",
        f"Call: {challenge['original_call']}",
        f"Challenged by: {challenge['challenge_team']}",
    ]
    if challenge.get("pitch_name") and challenge.get("speed"):
        lines.append(f"Pitch: {challenge['pitch_name']} ({challenge['speed']:.0f} mph)")

    lines.append("")
    lines.append("#MLB #ABS #ABSChallenge")

    return "\n".join(lines)


def build_daily_tweet(challenges, target_date=None):
    """Build tweet text for daily summary."""
    if target_date is None:
        target_date = date.today()

    n = len(challenges)
    overturned = sum(1 for c in challenges if c["result"] == "overturned")
    rate = overturned / max(n, 1) * 100

    return (
        f"ABS Challenge Daily Recap - {target_date.strftime('%B %d')}\n\n"
        f"{n} total challenges across all games\n"
        f"{overturned} overturned ({rate:.0f}% success rate)\n"
        f"{n - overturned} upheld\n\n"
        f"#MLB #ABS #ABSChallenge"
    )

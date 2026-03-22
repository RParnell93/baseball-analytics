#!/usr/bin/env python3
"""Collect all called pitches (balls + called strikes) per umpire for spring training.

Fetches MLB API game feeds for all spring training games, extracts every
called ball and called strike with pitch coordinates, and caches to JSON.
This data powers the "established zone" overlay in the umpire app.

Usage:
    python scripts/collect_umpire_called_pitches.py
    python scripts/collect_umpire_called_pitches.py --cache  # reuse if exists
"""

import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

import statsapi

OUTPUT_PATH = Path("output/abs/umpire_called_pitches.json")

# Called ball/strike codes from MLB API
CALLED_CODES = {
    "C": "Called Strike",
    "B": "Ball",
    "*B": "Ball",
}


def get_spring_training_game_ids(start_date, end_date):
    """Get all spring training game IDs in date range."""
    game_ids = []
    current = start_date
    while current <= end_date:
        date_str = current.strftime("%m/%d/%Y")
        schedule = statsapi.schedule(date=date_str, sportId=1)
        # Also get spring training (sportId=1 is MLB, but spring games show up)
        st_schedule = statsapi.schedule(date=date_str)
        for game in st_schedule:
            if game.get("game_type") in ("S", "E"):  # Spring training, exhibition
                game_ids.append(game["game_id"])
        current += timedelta(days=1)
    return sorted(set(game_ids))


def collect_called_pitches_from_game(game_id):
    """Extract all called balls and strikes from a game feed."""
    try:
        feed = statsapi.get("game", {"gamePk": game_id})
    except Exception as e:
        print(f"    Error fetching {game_id}: {e}")
        return []

    # Get HP umpire
    umpire_hp = "Unknown"
    for ump in feed["liveData"].get("boxscore", {}).get("officials", []):
        if ump.get("officialType") == "Home Plate":
            umpire_hp = ump.get("official", {}).get("fullName", "Unknown")
            break

    if umpire_hp == "Unknown":
        return []

    game_date = feed["gameData"]["datetime"].get("officialDate", "")
    teams = feed["gameData"]["teams"]
    away_abbr = teams["away"]["abbreviation"]
    home_abbr = teams["home"]["abbreviation"]
    plays = feed["liveData"]["plays"].get("allPlays", [])
    called_pitches = []

    for play in plays:
        # Determine batting team from half inning
        about = play.get("about", {})
        half = about.get("halfInning", "")
        batting_team = away_abbr if half == "top" else home_abbr

        for ev in play.get("playEvents", []):
            if not ev.get("isPitch"):
                continue

            details = ev.get("details", {})
            code = details.get("code", "")

            # Only called strikes and balls (not swinging, foul, etc.)
            if code not in CALLED_CODES:
                continue

            pitch_data = ev.get("pitchData", {})
            coords = pitch_data.get("coordinates", {})
            px = coords.get("pX")
            pz = coords.get("pZ")

            if px is None or pz is None:
                continue

            # Pitch type info
            pitch_type_code = details.get("type", {}).get("code", "")
            pitch_type_desc = details.get("type", {}).get("description", "")

            called_pitches.append({
                "umpire": umpire_hp,
                "game_id": game_id,
                "date": game_date,
                "call": CALLED_CODES[code],
                "code": code,
                "pX": px,
                "pZ": pz,
                "sz_top": pitch_data.get("strikeZoneTop"),
                "sz_bottom": pitch_data.get("strikeZoneBottom"),
                "batting_team": batting_team,
                "pitch_type": pitch_type_code,
                "pitch_name": pitch_type_desc,
            })

    return called_pitches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", action="store_true", help="Reuse cached data")
    parser.add_argument("--start", default="2026-02-20")
    parser.add_argument("--end", default=None)
    args = parser.parse_args()

    if args.cache and OUTPUT_PATH.exists():
        print(f"Cached data exists at {OUTPUT_PATH}")
        with open(OUTPUT_PATH) as f:
            data = json.load(f)
        print(f"  {len(data)} called pitches across {len(set(d['umpire'] for d in data))} umpires")
        return

    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end) if args.end else date.today() - timedelta(days=1)

    # Get game IDs from our challenge data (faster than searching schedule API)
    challenge_path = Path("output/abs/spring_training_challenges.json")
    if challenge_path.exists():
        with open(challenge_path) as f:
            challenges = json.load(f)
        game_ids = sorted(set(c["game_id"] for c in challenges))
        print(f"Found {len(game_ids)} games from challenge data")
    else:
        print(f"Fetching spring training schedule: {start_date} to {end_date}")
        game_ids = get_spring_training_game_ids(start_date, end_date)
        print(f"Found {len(game_ids)} spring training games")

    all_pitches = []
    for i, gid in enumerate(game_ids):
        print(f"  [{i+1}/{len(game_ids)}] Game {gid}...", end=" ", flush=True)
        t0 = time.time()
        pitches = collect_called_pitches_from_game(gid)
        elapsed = time.time() - t0
        all_pitches.extend(pitches)
        print(f"{len(pitches)} called pitches ({elapsed:.1f}s)")
        time.sleep(0.3)  # rate limit

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_pitches, f)

    n_umps = len(set(p["umpire"] for p in all_pitches))
    print(f"\nDone: {len(all_pitches)} called pitches, {n_umps} umpires")
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

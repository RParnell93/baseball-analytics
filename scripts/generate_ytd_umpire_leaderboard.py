#!/usr/bin/env python3
"""Generate YTD Spring Training umpire leaderboard.

Fetches all ABS challenges across the entire spring training period
and generates the umpire accuracy leaderboard.

Usage:
    python scripts/generate_ytd_umpire_leaderboard.py
    python scripts/generate_ytd_umpire_leaderboard.py --min-challenges 5
    python scripts/generate_ytd_umpire_leaderboard.py --cache  # reuse cached data
"""

import argparse
import json
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from datetime import date, timedelta
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bots.abs_challenge_bot import find_all_challenges_for_date
from src.bots.abs_leaderboards import (
    generate_umpire_leaderboard,
    generate_team_leaderboard,
    generate_team_bar_chart,
)

CACHE_PATH = Path("output/abs/spring_training_challenges.json")


def collect_spring_training_challenges(start_date, end_date, use_cache=False):
    """Collect all challenges from start_date through end_date."""
    if use_cache and CACHE_PATH.exists():
        print(f"Loading cached data from {CACHE_PATH}")
        with open(CACHE_PATH) as f:
            return json.load(f)

    all_challenges = []
    current = start_date
    while current <= end_date:
        print(f"  {current.strftime('%Y-%m-%d')}...", end=" ", flush=True)
        t0 = time.time()
        challenges = find_all_challenges_for_date(current)
        elapsed = time.time() - t0
        print(f"{len(challenges)} challenges ({elapsed:.1f}s)")
        all_challenges.extend(challenges)
        current += timedelta(days=1)

    # Cache to disk
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(all_challenges, f)
    print(f"\nCached {len(all_challenges)} challenges to {CACHE_PATH}")

    return all_challenges


def main():
    parser = argparse.ArgumentParser(description="YTD Spring Training Umpire Leaderboard")
    parser.add_argument("--min-challenges", type=int, default=2,
                        help="Minimum challenges faced to qualify (default: 2)")
    parser.add_argument("--cache", action="store_true",
                        help="Use cached challenge data if available")
    parser.add_argument("--start", type=str, default="2026-02-20",
                        help="Start date (default: 2026-02-20)")
    parser.add_argument("--end", type=str, default=None,
                        help="End date (default: yesterday)")
    args = parser.parse_args()

    start_date = date.fromisoformat(args.start)
    end_date = date.fromisoformat(args.end) if args.end else date.today() - timedelta(days=1)

    print(f"Collecting ABS challenges: {start_date} to {end_date}")
    print(f"{'='*50}")
    challenges = collect_spring_training_challenges(start_date, end_date, args.cache)

    n = len(challenges)
    n_ot = sum(1 for c in challenges if c["result"] == "overturned")
    print(f"\nYTD totals: {n} challenges, {n_ot} overturned ({n_ot/max(n,1)*100:.0f}%)")

    output_dir = Path("output/abs/ytd")
    output_dir.mkdir(parents=True, exist_ok=True)

    label = f"Spring Training {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    # Umpire leaderboard
    print(f"\nGenerating umpire leaderboard (min {args.min_challenges} challenges)...")
    fig = generate_umpire_leaderboard(
        challenges, period_label=label,
        min_challenges=args.min_challenges,
        save_path=output_dir / "umpire_leaderboard_ytd.png",
    )
    plt.close(fig)
    print(f"  Saved: {output_dir / 'umpire_leaderboard_ytd.png'}")

    # Team leaderboard
    print("Generating team leaderboard...")
    fig = generate_team_leaderboard(
        challenges, period_label=label,
        save_path=output_dir / "team_leaderboard_ytd.png",
    )
    plt.close(fig)
    print(f"  Saved: {output_dir / 'team_leaderboard_ytd.png'}")

    # Team bar chart
    print("Generating team bar chart...")
    fig = generate_team_bar_chart(
        challenges, period_label=label,
        metric="net_value",
        save_path=output_dir / "team_rankings_ytd.png",
    )
    plt.close(fig)
    print(f"  Saved: {output_dir / 'team_rankings_ytd.png'}")

    print(f"\nDone! All files in {output_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Refresh site images with latest YTD leaderboards.

Regenerates all leaderboard images and copies them to site/images/
for GitHub Pages deployment.

Usage:
    python scripts/refresh_site.py
    python scripts/refresh_site.py --min-challenges 15
"""

import argparse
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from datetime import date, timedelta
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_ytd_umpire_leaderboard import collect_spring_training_challenges
from src.bots.abs_leaderboards import (
    generate_umpire_leaderboard,
    generate_team_leaderboard,
    generate_team_bar_chart,
)


def main():
    parser = argparse.ArgumentParser(description="Refresh site images")
    parser.add_argument("--min-challenges", type=int, default=20)
    args = parser.parse_args()

    start_date = date(2026, 2, 20)
    end_date = date.today() - timedelta(days=1)

    print("Collecting challenges (using cache if available)...")
    challenges = collect_spring_training_challenges(start_date, end_date, use_cache=True)

    n = len(challenges)
    n_ot = sum(1 for c in challenges if c["result"] == "overturned")
    print(f"YTD: {n} challenges, {n_ot} overturned ({n_ot/max(n,1)*100:.0f}%)")

    site_images = Path("site/images")
    site_images.mkdir(parents=True, exist_ok=True)

    label = f"Spring Training {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    print("Generating umpire leaderboard...")
    fig = generate_umpire_leaderboard(
        challenges, period_label=label,
        min_challenges=args.min_challenges,
        save_path=site_images / "umpire_leaderboard_ytd.png",
    )
    plt.close(fig)

    print("Generating team leaderboard...")
    fig = generate_team_leaderboard(
        challenges, period_label=label,
        save_path=site_images / "team_leaderboard_ytd.png",
    )
    plt.close(fig)

    print("Generating team bar chart...")
    fig = generate_team_bar_chart(
        challenges, period_label=label,
        metric="net_value",
        save_path=site_images / "team_rankings_ytd.png",
    )
    plt.close(fig)

    print(f"\nSite images updated in {site_images}/")
    print("Commit and push to deploy to GitHub Pages.")


if __name__ == "__main__":
    main()

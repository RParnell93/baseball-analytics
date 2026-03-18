#!/usr/bin/env python3
"""ABS Challenge Bot - Daily CLI Runner.

Fetches all ABS challenges for a date, generates visualizations,
and optionally posts to Twitter.

Usage:
    python scripts/run_abs_bot.py --date 2026-03-17 --dry-run
    python scripts/run_abs_bot.py --post
"""

import argparse
import matplotlib
matplotlib.use('Agg')  # Headless backend for server/CLI use

import matplotlib.pyplot as plt
from datetime import date, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.bots.abs_challenge_bot import (
    find_all_challenges_for_date,
    generate_challenge_image,
    generate_daily_summary
)
from src.bots.abs_leaderboards import (
    generate_team_leaderboard,
    generate_team_bar_chart
)
from src.bots.challenge_strategy import generate_league_strategy_heatmap
from src.bots.twitter_poster import post_tweet, post_daily_summary
from src.bots.challenge_impact import rank_challenges_by_impact


def main():
    parser = argparse.ArgumentParser(
        description="ABS Challenge Bot - Daily Automation"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Date to fetch challenges for (YYYY-MM-DD). Default: yesterday"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate images but skip posting to Twitter"
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Post to Twitter (requires credentials in .env)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/abs",
        help="Output directory for images. Default: output/abs"
    )

    args = parser.parse_args()

    # Parse date
    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        # Default to yesterday (since games end late and we run next morning)
        target_date = date.today() - timedelta(days=1)

    # Create output directory
    date_str = target_date.strftime("%Y-%m-%d")
    output_path = Path(args.output_dir) / date_str
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"ABS Challenge Bot - {date_str}")
    print(f"Output directory: {output_path}")
    print()

    # 1. Fetch all challenges for the date
    print("Fetching challenges...")
    challenges = find_all_challenges_for_date(target_date)

    if not challenges:
        print("No challenges found for this date.")
        return

    # Print summary stats
    n_total = len(challenges)
    n_overturned = sum(1 for c in challenges if c["result"] == "overturned")
    n_upheld = n_total - n_overturned
    overturn_rate = n_overturned / n_total * 100

    print(f"Found {n_total} challenges:")
    print(f"  - {n_overturned} overturned")
    print(f"  - {n_upheld} upheld")
    print(f"  - {overturn_rate:.1f}% overturn rate")
    print()

    saved_files = []

    # 2. Generate daily summary image
    print("Generating daily summary...")
    summary_path = output_path / "daily_summary.png"
    fig = generate_daily_summary(challenges, target_date, save_path=summary_path)
    plt.close(fig)
    saved_files.append(summary_path)
    print(f"  Saved: {summary_path}")

    # 3. Generate top 5 highest-impact challenge images
    print("\nGenerating top 5 challenge images...")
    ranked = rank_challenges_by_impact(challenges)
    top_5 = ranked[:5]

    for i, challenge in enumerate(top_5):
        impact_score = challenge.get("impact", {}).get("impact_score", 0)
        img_name = f"challenge_{i+1}_impact_{impact_score:.0f}.png"
        img_path = output_path / img_name

        fig = generate_challenge_image(challenge, save_path=img_path)
        plt.close(fig)
        saved_files.append(img_path)

        print(f"  {i+1}. {challenge['batter']} vs {challenge['pitcher']}")
        print(f"     {challenge['away']}@{challenge['home']} - {challenge['result'].upper()}")
        print(f"     Impact: {impact_score:.0f} | Saved: {img_path.name}")

    # 4. Generate count/outs heatmap
    print("\nGenerating strategy heatmap...")
    heatmap_path = output_path / "count_outs_heatmap.png"
    fig = generate_league_strategy_heatmap(challenges, save_path=heatmap_path)
    plt.close(fig)
    saved_files.append(heatmap_path)
    print(f"  Saved: {heatmap_path}")

    # 5. Generate team rankings bar chart
    print("\nGenerating team rankings...")
    rankings_path = output_path / "team_rankings.png"
    fig = generate_team_bar_chart(
        challenges,
        period_label=date_str,
        metric="net_value",
        save_path=rankings_path
    )
    plt.close(fig)
    saved_files.append(rankings_path)
    print(f"  Saved: {rankings_path}")

    # 6. Post to Twitter if requested
    if args.post and not args.dry_run:
        print("\nPosting to Twitter...")

        # Post daily summary first
        print("  Posting daily summary...")
        result = post_daily_summary(challenges, target_date, str(summary_path))
        if result:
            print(f"    Posted: {result.get('url')}")
            parent_id = result.get("tweet_id")

            # Post top 5 as replies
            print("\n  Posting top 5 challenge images as replies...")
            for i, challenge in enumerate(top_5):
                impact_score = challenge.get("impact", {}).get("impact_score", 0)
                img_name = f"challenge_{i+1}_impact_{impact_score:.0f}.png"
                img_path = output_path / img_name

                # Build tweet text
                result_str = "OVERTURNED" if challenge["result"] == "overturned" else "UPHELD"
                half = "T" if challenge.get("half") == "top" else "B"
                tweet_text = (
                    f"#{i+1}: {result_str} - Impact: {impact_score:.0f}\n"
                    f"{challenge['away']}@{challenge['home']} {half}{challenge['inning']}\n"
                    f"{challenge['batter']} vs {challenge['pitcher']}"
                )

                # Note: Twitter API v2 reply threading requires passing in_reply_to_tweet_id
                # The post_tweet function doesn't currently support this, so we'll just post standalone
                # TODO: Enhance post_tweet to support reply_to_tweet_id parameter
                reply_result = post_tweet(tweet_text, str(img_path))
                if reply_result:
                    print(f"    #{i+1} posted: {reply_result.get('url')}")
                else:
                    print(f"    #{i+1} failed to post")
        else:
            print("  Failed to post daily summary")

    elif args.dry_run:
        print("\nDRY RUN - Skipping Twitter posts")

    # 7. Print all saved files
    print("\n" + "="*60)
    print("All saved files:")
    for f in saved_files:
        print(f"  {f}")
    print()
    print(f"Total: {len(saved_files)} files saved to {output_path}")
    print("="*60)


if __name__ == "__main__":
    main()

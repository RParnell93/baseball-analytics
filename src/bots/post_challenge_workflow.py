"""Complete workflow: Find challenge, generate image, post to Twitter.

This is a complete example showing how to use the twitter_poster module
to post ABS challenges as they happen.
"""

import os
import sys
from pathlib import Path
from datetime import date

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.bots.abs_challenge_bot import (
    find_challenges_in_game,
    find_all_challenges_for_date,
    generate_challenge_image,
    generate_daily_summary,
)
from src.bots.twitter_poster import post_challenge, post_daily_summary


def post_single_challenge(game_id, output_dir="/tmp"):
    """Find and post the first challenge from a game.

    Args:
        game_id: MLB game ID
        output_dir: Directory to save images

    Returns:
        bool indicating success
    """
    print(f"Finding challenges in game {game_id}...")
    challenges = find_challenges_in_game(game_id)

    if not challenges:
        print("No challenges found in this game.")
        return False

    challenge = challenges[0]
    print(f"Found challenge: {challenge['result']} call by {challenge['challenge_team']}")

    # Generate image
    image_path = Path(output_dir) / f"challenge_{game_id}_{challenge['inning']}.png"
    print(f"Generating image: {image_path}")
    generate_challenge_image(challenge, save_path=image_path)

    # Post to Twitter
    print("Posting to Twitter...")
    result = post_challenge(challenge, str(image_path))

    if result:
        print(f"Success! Tweet URL: {result['url']}")
        return True
    else:
        print("Failed to post tweet.")
        return False


def post_daily_challenges(target_date=None, output_dir="/tmp"):
    """Find and post all challenges from a specific date.

    Args:
        target_date: date object (defaults to today)
        output_dir: Directory to save images

    Returns:
        int number of challenges posted
    """
    if target_date is None:
        target_date = date.today()

    print(f"Finding challenges for {target_date}...")
    challenges = find_all_challenges_for_date(target_date)

    if not challenges:
        print("No challenges found for this date.")
        return 0

    print(f"Found {len(challenges)} challenges")

    # Post individual challenges
    posted = 0
    for i, challenge in enumerate(challenges):
        image_path = Path(output_dir) / f"challenge_{target_date}_{i}.png"
        print(f"\nChallenge {i+1}/{len(challenges)}: {challenge['away']} @ {challenge['home']}")

        generate_challenge_image(challenge, save_path=image_path)
        result = post_challenge(challenge, str(image_path))

        if result:
            print(f"Posted: {result['url']}")
            posted += 1
        else:
            print("Failed to post")

    # Post daily summary
    print("\nGenerating daily summary...")
    summary_path = Path(output_dir) / f"daily_summary_{target_date}.png"
    generate_daily_summary(challenges, target_date, save_path=summary_path)

    result = post_daily_summary(challenges, target_date, str(summary_path))
    if result:
        print(f"Summary posted: {result['url']}")
    else:
        print("Failed to post summary")

    return posted


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Post ABS challenges to Twitter")
    parser.add_argument("--game-id", type=int, help="Post challenges from a specific game")
    parser.add_argument("--date", type=str, help="Post challenges from date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=str, default="/tmp", help="Directory for images")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode")

    args = parser.parse_args()

    if args.dry_run:
        os.environ["TWITTER_DRY_RUN"] = "1"
        print("DRY RUN MODE ENABLED")

    if args.game_id:
        post_single_challenge(args.game_id, args.output_dir)
    elif args.date:
        target = date.fromisoformat(args.date)
        post_daily_challenges(target, args.output_dir)
    else:
        # Default: today's challenges
        post_daily_challenges(output_dir=args.output_dir)

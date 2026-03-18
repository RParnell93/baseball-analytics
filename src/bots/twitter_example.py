"""Example usage of the Twitter poster module.

Run this to test posting in DRY_RUN mode.
"""

import os
from datetime import date
from pathlib import Path

# Set DRY_RUN mode for testing
os.environ["TWITTER_DRY_RUN"] = "1"

from src.bots.twitter_poster import post_tweet, post_challenge, post_daily_summary
from src.bots.abs_challenge_bot import find_challenges_in_game, generate_challenge_image


def example_simple_tweet():
    """Example: Post a simple text tweet."""
    print("\n=== Example 1: Simple text tweet ===")
    result = post_tweet("Testing the ABS Challenge Bot! #MLB #ABS")
    print(f"Result: {result}")


def example_tweet_with_image():
    """Example: Post a tweet with an image."""
    print("\n=== Example 2: Tweet with image ===")

    # Create a dummy image path (would need to exist in real usage)
    image_path = "/tmp/test_image.png"

    result = post_tweet(
        "ABS Challenge visualization test! #MLB #ABS",
        image_path=image_path
    )
    print(f"Result: {result}")


def example_challenge_post():
    """Example: Post a challenge from real game data."""
    print("\n=== Example 3: Post challenge from game data ===")

    # Sample challenge dict (normally from find_challenges_in_game)
    challenge = {
        "game_id": 745678,
        "away": "NYY",
        "home": "BOS",
        "inning": 3,
        "half": "top",
        "batter": "Aaron Judge",
        "pitcher": "Chris Sale",
        "umpire": "Angel Hernandez",
        "original_call": "Called Strike",
        "result": "overturned",
        "challenge_team": "NYY",
        "pitch_name": "Fastball",
        "speed": 98.5,
    }

    image_path = "/tmp/challenge.png"
    result = post_challenge(challenge, image_path)
    print(f"Result: {result}")


def example_daily_summary():
    """Example: Post daily summary."""
    print("\n=== Example 4: Daily summary ===")

    challenges = [
        {"result": "overturned"},
        {"result": "overturned"},
        {"result": "upheld"},
    ]

    image_path = "/tmp/daily_summary.png"
    result = post_daily_summary(challenges, date.today(), image_path)
    print(f"Result: {result}")


if __name__ == "__main__":
    print("Twitter Poster Examples (DRY_RUN mode)")
    print("=" * 50)

    example_simple_tweet()
    example_tweet_with_image()
    example_challenge_post()
    example_daily_summary()

    print("\n" + "=" * 50)
    print("\nTo post for real:")
    print("1. Set credentials in .env file")
    print("2. Remove TWITTER_DRY_RUN or set it to 0")
    print("3. Run your posting script")

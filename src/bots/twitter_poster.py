"""Twitter/X posting module for ABS Challenge Bot.

Uses tweepy for Twitter API v2 posting. Supports text tweets and image attachments.
Includes a DRY_RUN mode for testing without actually posting.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

try:
    import tweepy
except ImportError:
    tweepy = None

from src.bots.abs_challenge_bot import build_challenge_tweet, build_daily_tweet

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def get_client():
    """Get an authenticated tweepy Client for Twitter API v2.

    Returns:
        tweepy.Client if credentials are available, None otherwise
    """
    if tweepy is None:
        logger.warning("tweepy not installed. Install with: pip install tweepy")
        return None

    # Check for required credentials
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        logger.warning(
            "Twitter credentials not found. Set TWITTER_API_KEY, TWITTER_API_SECRET, "
            "TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_SECRET in .env file."
        )
        return None

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with Twitter: {e}")
        return None


def get_api_v1():
    """Get an authenticated tweepy API object for v1.1 endpoints (media upload).

    Returns:
        tweepy.API if credentials are available, None otherwise
    """
    if tweepy is None:
        return None

    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        return None

    try:
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api = tweepy.API(auth)
        return api
    except Exception as e:
        logger.error(f"Failed to authenticate with Twitter v1.1 API: {e}")
        return None


def post_tweet(text, image_path=None):
    """Post a tweet with optional image attachment.

    Args:
        text: Tweet text (max 280 characters)
        image_path: Optional path to image file to attach

    Returns:
        dict with tweet_id and url if successful, None otherwise
    """
    dry_run = os.getenv("TWITTER_DRY_RUN", "0") == "1"

    if dry_run:
        logger.info("DRY RUN MODE - Would post tweet:")
        logger.info(f"Text: {text}")
        if image_path:
            logger.info(f"Image: {image_path}")
        return {"tweet_id": "dry_run", "url": "https://twitter.com/dry_run"}

    client = get_client()
    if client is None:
        logger.error("Cannot post tweet: Twitter client not available")
        return None

    media_ids = []

    # Upload image if provided (requires v1.1 API)
    if image_path:
        api_v1 = get_api_v1()
        if api_v1 is None:
            logger.error("Cannot upload image: Twitter v1.1 API not available")
            return None

        try:
            if not Path(image_path).exists():
                logger.error(f"Image file not found: {image_path}")
                return None

            media = api_v1.media_upload(filename=image_path)
            media_ids.append(media.media_id)
            logger.info(f"Uploaded image with media_id: {media.media_id}")
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None

    # Post tweet with v2 API
    try:
        response = client.create_tweet(
            text=text,
            media_ids=media_ids if media_ids else None
        )
        tweet_id = response.data["id"]
        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

        logger.info(f"Tweet posted successfully: {tweet_url}")
        return {"tweet_id": tweet_id, "url": tweet_url}

    except Exception as e:
        logger.error(f"Failed to post tweet: {e}")
        return None


def post_challenge(challenge_dict, image_path):
    """Post an ABS challenge tweet with image.

    Args:
        challenge_dict: Challenge data dict from abs_challenge_bot.find_challenges_in_game()
        image_path: Path to the challenge visualization image

    Returns:
        dict with tweet_id and url if successful, None otherwise
    """
    text = build_challenge_tweet(challenge_dict)
    return post_tweet(text, image_path)


def post_daily_summary(challenges, target_date, image_path):
    """Post the daily ABS challenge summary tweet with image.

    Args:
        challenges: List of challenge dicts for the day
        target_date: date object for the summary
        image_path: Path to the daily summary visualization image

    Returns:
        dict with tweet_id and url if successful, None otherwise
    """
    text = build_daily_tweet(challenges, target_date)
    return post_tweet(text, image_path)

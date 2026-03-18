Twitter Posting Module
======================

Module: twitter_poster.py
Uses: tweepy for Twitter/X API v2

Setup
-----

1. Install tweepy (already in requirements.txt):
   pip install tweepy

2. Get Twitter API credentials:
   - Go to https://developer.twitter.com/en/portal/dashboard
   - Create a new app or use existing app
   - Get API Key, API Secret, Access Token, and Access Secret
   - Make sure app has "Read and Write" permissions

3. Add credentials to .env file:
   TWITTER_API_KEY=your_api_key
   TWITTER_API_SECRET=your_api_secret
   TWITTER_ACCESS_TOKEN=your_access_token
   TWITTER_ACCESS_SECRET=your_access_secret
   TWITTER_BEARER_TOKEN=your_bearer_token (optional)

4. Optional: Enable dry run mode for testing:
   TWITTER_DRY_RUN=1


Functions
---------

get_client()
    Returns authenticated tweepy.Client for API v2
    Returns None if credentials not set

get_api_v1()
    Returns authenticated tweepy.API for v1.1 (media upload)
    Returns None if credentials not set

post_tweet(text, image_path=None)
    Post a tweet with optional image
    - text: Tweet text (max 280 chars)
    - image_path: Optional path to image file
    Returns: dict with tweet_id and url

post_challenge(challenge_dict, image_path)
    Post an ABS challenge tweet with image
    - challenge_dict: From find_challenges_in_game()
    - image_path: Path to visualization
    Returns: dict with tweet_id and url

post_daily_summary(challenges, target_date, image_path)
    Post daily recap with summary image
    - challenges: List of challenge dicts
    - target_date: date object
    - image_path: Path to summary visualization
    Returns: dict with tweet_id and url


Examples
--------

# Simple tweet
from src.bots.twitter_poster import post_tweet
result = post_tweet("Test tweet! #MLB")

# Challenge with image
from src.bots.twitter_poster import post_challenge
from src.bots.abs_challenge_bot import find_challenges_in_game, generate_challenge_image

challenges = find_challenges_in_game(745678)
challenge = challenges[0]
generate_challenge_image(challenge, save_path="/tmp/challenge.png")
result = post_challenge(challenge, "/tmp/challenge.png")

# Complete workflow
python3 src/bots/post_challenge_workflow.py --game-id 745678 --dry-run


Dry Run Mode
------------

Set TWITTER_DRY_RUN=1 in .env or environment to test without posting.
All post functions will print what they would post instead of actually posting.


Error Handling
--------------

- Returns None if credentials not set (logs warning)
- Returns None if image file not found
- Returns None if API call fails
- Check return value before assuming success


Tweet Text Builders
-------------------

Tweet text is built by functions in abs_challenge_bot.py:
- build_challenge_tweet(challenge_dict)
- build_daily_tweet(challenges, target_date)

These format the challenge data into Twitter-friendly text with hashtags.

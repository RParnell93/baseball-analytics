# Twitter/X Content Automation Pipeline Design

**Project:** Baseball Analytics (@sabrmagician)
**Author:** Research for Robert Parnell
**Date:** March 2026
**Status:** Design phase - no implementation yet

---

## Executive Summary

Design for a fully automated Twitter content pipeline modeled after @UmpScorecards. Daily ABS challenge reports posted to @roboumpstats (or @sabrmagician), with consistent visual branding, scheduled GitHub Actions execution, and a content queue system for variety.

**Key insight:** The market opportunity is speed + consistency + visual quality. Nobody is doing automated daily ABS visual content. Spring training 2026 is the proving ground.

---

## 1. Daily Posting Pipeline

### Architecture: GitHub Actions + Scheduled Workflow

**Why GitHub Actions:**
- Free for public repos (2,000 minutes/month)
- Native cron scheduling
- Built-in secrets management
- Can run Python scripts with matplotlib
- Commit/push output back to repo
- No server to maintain

**Workflow Structure:**

```yaml
name: Daily ABS Bot

on:
  schedule:
    - cron: '0 13 * * *'  # 1pm UTC = 8am ET (after games finish ~3am ET)
  workflow_dispatch:  # Manual trigger for testing

jobs:
  post-abs-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run ABS bot
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
          TWITTER_DRY_RUN: 0
        run: |
          python scripts/run_abs_bot.py --post --date $(date -d "yesterday" +%Y-%m-%d)

      - name: Commit generated images
        run: |
          git config user.name "ABS Bot"
          git config user.email "bot@sabrmagician.com"
          git add output/abs/
          git commit -m "ABS bot: daily run $(date +%Y-%m-%d)" || true
          git push || true
```

**Timing considerations:**
- MLB games end 11pm-2am ET
- Run bot 8am ET next morning (after all Final scores posted)
- Default to "yesterday" in `run_abs_bot.py` (already implemented)

**Secrets required (set in GitHub repo settings):**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`

### Error Handling & Retry Logic

**Current state:** `run_abs_bot.py` has basic error handling. No retries.

**Recommended enhancements:**

```python
# In twitter_poster.py
import time
from functools import wraps

def retry_on_rate_limit(max_retries=3, backoff_seconds=60):
    """Decorator to retry Twitter API calls on rate limit errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except tweepy.errors.TooManyRequests as e:
                    if attempt < max_retries - 1:
                        wait_time = backoff_seconds * (2 ** attempt)
                        logger.warning(f"Rate limited. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error("Max retries exceeded")
                        raise
                except tweepy.errors.Forbidden as e:
                    logger.error(f"Auth error: {e}")
                    return None  # Don't retry auth failures
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(backoff_seconds)
                    else:
                        raise
            return None
        return wrapper
    return decorator

@retry_on_rate_limit(max_retries=3)
def post_tweet(text, image_path=None, reply_to_id=None):
    # ... existing implementation
```

**Failure modes to handle:**
1. **No games found:** Log and exit gracefully (no challenges = no post)
2. **MLB API timeout:** Retry with exponential backoff
3. **Image generation failure:** Skip that image, continue with others
4. **Twitter rate limit:** Wait and retry (15-minute rate limit windows)
5. **Twitter auth failure:** Log error, notify via GitHub Actions email
6. **Duplicate tweet:** Twitter rejects exact duplicates - add timestamp or challenge ID to text

**Notification strategy:**
- GitHub Actions emails on workflow failure
- Optional: Post error summary to Discord webhook (for real-time alerts)

### Dry-Run vs Live Posting Modes

**Already implemented:** `TWITTER_DRY_RUN=1` in `.env` (checked in `twitter_poster.py`)

**Usage patterns:**
- Local dev: Always dry-run (`TWITTER_DRY_RUN=1` in `.env`)
- GitHub Actions: Set `TWITTER_DRY_RUN: 0` in workflow env vars
- Testing: Manual trigger with `workflow_dispatch` event

**Enhancement: Separate test account:**
- Create `@sabrmagician_dev` test account
- Use different credentials in GitHub Actions for testing
- Add `--test-account` flag to `run_abs_bot.py`

---

## 2. Image Template System

### Design Philosophy

**Twitter card specs:**
- **Optimal size:** 1200x675 (16:9 aspect ratio)
- **Maximum file size:** 5MB
- **Formats:** PNG (current), JPEG (smaller for photos)

**Current state:**
- ABS challenge images are 6x8 (portrait, ~1200x1600 px at 200 DPI)
- Daily summary images are 12x10+ (landscape, variable height)
- Team leaderboards are 10x8 (portrait)

**Problem:** Current images are too tall for Twitter cards. Need standardized 16:9 templates.

### Standardized Twitter Card Template

**Layout structure:**

```
┌────────────────────────────────────────────────────────┐
│  HEADER BAR (150px)                                    │
│  Title                          @sabrmagician          │
├────────────────────────────────────────────────────────┤
│                                                        │
│                                                        │
│         CHART/FIGURE CONTENT (475px)                   │
│         (matplotlib fig embedded here)                 │
│                                                        │
│                                                        │
├────────────────────────────────────────────────────────┤
│  FOOTER BAR (50px)                                     │
│  Date: Mar 20, 2026    Data: MLB Stats API            │
└────────────────────────────────────────────────────────┘
```

**Implementation approach:**

```python
# src/visualization/twitter_card.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Twitter card constants
CARD_WIDTH = 1200  # pixels at 100 DPI
CARD_HEIGHT = 675
CARD_DPI = 100
HEADER_HEIGHT = 150  # pixels
FOOTER_HEIGHT = 50
CONTENT_HEIGHT = CARD_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT  # 475px

# Theme (from stat_cards.py)
DARK_BG = "#0e1117"
CARD_BG = "#1C2331"
ACCENT = "#FF6B35"  # Orange accent for @sabrmagician brand
TEXT_WHITE = "#EAEAEA"
TEXT_DIM = "#8899aa"


def create_twitter_card(title, content_fig=None, date_str=None,
                        data_source="MLB Stats API", save_path=None):
    """Create a standardized 1200x675 Twitter card.

    Args:
        title: Main title text (e.g., "ABS Challenge: OVERTURNED")
        content_fig: matplotlib figure to embed in content area
        date_str: Date string for footer (e.g., "March 20, 2026")
        data_source: Data source credit for footer
        save_path: Path to save PNG

    Returns:
        matplotlib figure
    """
    fig = plt.figure(
        figsize=(CARD_WIDTH/CARD_DPI, CARD_HEIGHT/CARD_DPI),
        facecolor=DARK_BG,
        dpi=CARD_DPI
    )

    # Header bar
    header_ax = fig.add_axes([0, 1 - HEADER_HEIGHT/CARD_HEIGHT, 1, HEADER_HEIGHT/CARD_HEIGHT])
    header_ax.set_facecolor(CARD_BG)
    header_ax.axis('off')

    # Title (left-aligned)
    header_ax.text(0.03, 0.5, title, fontsize=32, fontweight='bold',
                   color=ACCENT, va='center', transform=header_ax.transAxes)

    # Brand (right-aligned)
    header_ax.text(0.97, 0.5, '@sabrmagician', fontsize=18,
                   color=TEXT_DIM, va='center', ha='right',
                   transform=header_ax.transAxes)

    # Content area (embed the provided figure)
    if content_fig:
        # Convert content_fig to image and embed
        # This requires rendering content_fig to buffer first
        from io import BytesIO
        buf = BytesIO()
        content_fig.savefig(buf, format='png', facecolor=DARK_BG,
                           bbox_inches='tight', dpi=150)
        buf.seek(0)

        content_ax = fig.add_axes([0.02, FOOTER_HEIGHT/CARD_HEIGHT + 0.02,
                                   0.96, (CONTENT_HEIGHT - 40)/CARD_HEIGHT])
        content_ax.axis('off')

        from PIL import Image
        img = Image.open(buf)
        content_ax.imshow(img, aspect='auto')

    # Footer bar
    footer_ax = fig.add_axes([0, 0, 1, FOOTER_HEIGHT/CARD_HEIGHT])
    footer_ax.set_facecolor(CARD_BG)
    footer_ax.axis('off')

    # Date (left)
    if date_str:
        footer_ax.text(0.03, 0.5, f"Date: {date_str}", fontsize=10,
                      color=TEXT_DIM, va='center', transform=footer_ax.transAxes)

    # Data source (right)
    footer_ax.text(0.97, 0.5, f"Data: {data_source}", fontsize=10,
                  color=TEXT_DIM, va='center', ha='right',
                  transform=footer_ax.transAxes)

    if save_path:
        fig.savefig(save_path, facecolor=DARK_BG, dpi=CARD_DPI,
                   bbox_inches='tight', pad_inches=0)

    return fig
```

**Alternative simpler approach:** Modify existing `generate_challenge_image()` to accept a `format` parameter:

```python
def generate_challenge_image(challenge, save_path=None, format='portrait'):
    """Generate challenge viz.

    Args:
        format: 'portrait' (current 6x8) or 'twitter' (12x6.75 for 1200x675)
    """
    if format == 'twitter':
        fig, ax = plt.subplots(figsize=(12, 6.75), facecolor=DARK_BG)
        # Layout adjustments for wider aspect ratio
        # Strike zone on left half, text on right half
    else:
        fig, ax = plt.subplots(figsize=(6, 8), facecolor=DARK_BG)
        # Existing portrait layout

    # ... rest of implementation
```

**Recommendation:** Start with the simpler approach (format parameter). Add the full template system later if you need more complex multi-panel cards.

### Color Palette & Branding

**Current theme (from `stat_cards.py`):**
- Background: `#1C2331` (dark blue-gray)
- Accent: `#22D1EE` (cyan)

**Proposed @sabrmagician brand theme:**
- Background: `#0e1117` (darker, matches Streamlit dark theme)
- Accent: `#FF6B35` (vibrant orange - stands out in Twitter feed)
- Text: `#EAEAEA` (off-white)
- Dim text: `#8899aa` (light gray)

**Why orange:**
- High contrast on dark background
- Different from team colors (no confusion)
- Energy/urgency (fits challenge/umpire content)
- Not overused in baseball analytics (most use blue/red)

**Consistency requirements:**
- All images use same background + accent colors
- Same font (Helvetica Neue / Arial fallback)
- Same @sabrmagician watermark placement (header or footer)
- Same footer format: "Data: MLB Stats API | Date: Mar 20, 2026"

---

## 3. Content Queue System

### Queue Design

**Goal:** Post variety. Not just raw data dumps. Mix of challenge images, summaries, leaderboards, strategy insights.

**Content types:**

| Type | Frequency | Priority | Example |
|------|-----------|----------|---------|
| Daily Summary | Every morning | High | "12 challenges yesterday, 7 overturned" |
| Top Challenge of Day | Every morning | High | "Biggest impact challenge: Judge at-bat" |
| Umpire Leaderboard | Weekly (Monday) | Medium | "Week 1 umpire accuracy rankings" |
| Team Strategy | Weekly (Thursday) | Medium | "Which teams challenge most in 2-strike counts?" |
| Individual Umpire Card | As notable | Low | "Angel Hernandez: 0-for-5 on challenges this week" |
| Catcher Framing Impact | Weekly | Low | "Top 5 catchers who get bad calls overturned" |

**Queue implementation:**

```python
# scripts/content_queue.py

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json

@dataclass
class QueuedPost:
    content_type: str  # 'daily_summary', 'challenge', 'leaderboard', etc.
    priority: int  # 1=high, 2=medium, 3=low
    post_date: str  # YYYY-MM-DD
    image_path: str
    tweet_text: str
    posted: bool = False
    tweet_id: str = None
    posted_at: str = None


class ContentQueue:
    """Manages queue of Twitter posts."""

    def __init__(self, queue_file="data/twitter_queue.json"):
        self.queue_file = Path(queue_file)
        self.queue = self.load()

    def load(self):
        if self.queue_file.exists():
            with open(self.queue_file) as f:
                data = json.load(f)
                return [QueuedPost(**item) for item in data]
        return []

    def save(self):
        with open(self.queue_file, 'w') as f:
            data = [vars(item) for item in self.queue]
            json.dump(data, f, indent=2)

    def add(self, content_type, priority, post_date, image_path, tweet_text):
        """Add new post to queue."""
        post = QueuedPost(
            content_type=content_type,
            priority=priority,
            post_date=post_date.strftime("%Y-%m-%d"),
            image_path=str(image_path),
            tweet_text=tweet_text
        )
        self.queue.append(post)
        self.save()

    def get_due_posts(self, target_date=None):
        """Get all unposted items due on or before target_date."""
        if target_date is None:
            target_date = date.today()

        target_str = target_date.strftime("%Y-%m-%d")
        due = [p for p in self.queue
               if not p.posted and p.post_date <= target_str]

        # Sort by priority (high first), then date
        due.sort(key=lambda p: (p.priority, p.post_date))
        return due

    def mark_posted(self, post, tweet_id):
        """Mark a post as successfully posted."""
        post.posted = True
        post.tweet_id = tweet_id
        post.posted_at = date.today().isoformat()
        self.save()
```

**Queue population (in `run_abs_bot.py`):**

```python
# After generating images, add to queue instead of immediate posting
from scripts.content_queue import ContentQueue

queue = ContentQueue()

# Daily summary (high priority)
queue.add(
    content_type='daily_summary',
    priority=1,
    post_date=target_date,
    image_path=summary_path,
    tweet_text=build_daily_tweet(challenges, target_date)
)

# Top 3 challenges (high priority)
for i, challenge in enumerate(top_5[:3]):
    queue.add(
        content_type='challenge',
        priority=1,
        post_date=target_date,
        image_path=output_path / f"challenge_{i+1}.png",
        tweet_text=build_challenge_tweet(challenge)
    )

# Weekly leaderboard (medium priority, only on Mondays)
if target_date.weekday() == 0:  # Monday
    queue.add(
        content_type='leaderboard',
        priority=2,
        post_date=target_date,
        image_path=leaderboard_path,
        tweet_text="Weekly umpire accuracy rankings..."
    )
```

**Queue posting (separate script `scripts/post_from_queue.py`):**

```python
#!/usr/bin/env python3
"""Post scheduled content from the queue."""

from scripts.content_queue import ContentQueue
from src.bots.twitter_poster import post_tweet
from datetime import date

def main():
    queue = ContentQueue()
    due_posts = queue.get_due_posts(date.today())

    if not due_posts:
        print("No posts due today.")
        return

    print(f"Posting {len(due_posts)} items...")

    for post in due_posts:
        print(f"\nPosting {post.content_type}...")
        result = post_tweet(post.tweet_text, post.image_path)

        if result:
            queue.mark_posted(post, result['tweet_id'])
            print(f"  Posted: {result['url']}")
        else:
            print(f"  Failed to post")

    print("\nDone.")

if __name__ == "__main__":
    main()
```

**Scheduling strategy:**
- Generate content + populate queue: 8am ET daily (GitHub Actions)
- Post from queue: 9am, 12pm, 3pm ET (3 GitHub Actions workflows with cron)
- Spread posts throughout the day for better engagement

### Engagement Tracking

**Metrics to track:**

```python
# data/twitter_analytics.json

{
  "posts": [
    {
      "tweet_id": "1234567890",
      "content_type": "daily_summary",
      "posted_at": "2026-03-20T09:00:00",
      "image_path": "output/abs/2026-03-20/daily_summary.png",
      "engagement": {
        "likes": 45,
        "retweets": 12,
        "replies": 3,
        "impressions": 2341,  # Requires Twitter API v2 premium
        "last_updated": "2026-03-20T21:00:00"
      }
    }
  ]
}
```

**Tracking implementation:**
- Fetch engagement stats 12 hours after posting (API v2 endpoint)
- Store in JSON file
- Weekly analysis: which content types perform best?
- Adjust queue priorities based on engagement

---

## 4. Thread Posting

### Twitter API v2 Thread Support

**Current limitation:** `post_tweet()` doesn't support `in_reply_to_tweet_id` parameter.

**Enhancement needed:**

```python
# In twitter_poster.py

def post_tweet(text, image_path=None, reply_to_id=None):
    """Post a tweet with optional image and reply threading.

    Args:
        text: Tweet text (max 280 characters)
        image_path: Optional path to image file
        reply_to_id: Optional tweet ID to reply to (for threads)

    Returns:
        dict with tweet_id and url if successful
    """
    # ... existing auth code ...

    try:
        response = client.create_tweet(
            text=text,
            media_ids=media_ids if media_ids else None,
            in_reply_to_tweet_id=reply_to_id  # NEW
        )
        tweet_id = response.data["id"]
        # ... rest of implementation
```

### Thread Structure Patterns

**Pattern 1: Daily Report Thread**

```
Tweet 1 (parent):
  "ABS Challenge Daily Recap - March 20
   12 challenges, 7 overturned (58% success rate)
   Thread: Top 3 highest-impact challenges 👇"
  [daily_summary.png]

Tweet 2 (reply to 1):
  "#1: OVERTURNED - Impact: 87
   NYY@BOS T8 | Judge vs Sale
   2-2 count, 1 out, tie game"
  [challenge_1.png]

Tweet 3 (reply to 2):
  "#2: UPHELD - Impact: 72
   LAD@SF B9 | Ohtani vs Webb
   3-2 count, 2 out, down 1"
  [challenge_2.png]

Tweet 4 (reply to 3):
  "#3: OVERTURNED - Impact: 68
   HOU@SEA B6 | Rodriguez vs Verlander
   1-2 count, 0 out, bases loaded"
  [challenge_3.png]
```

**Pattern 2: Weekly Leaderboard Thread**

```
Tweet 1 (parent):
  "Week 4 ABS Challenge Leaderboard
   Most accurate umpires, team success rates, and key stats
   Thread 👇"
  [umpire_leaderboard.png]

Tweet 2 (reply to 1):
  "Team challenge strategy: Who's aggressive vs conservative?"
  [team_strategy_heatmap.png]

Tweet 3 (reply to 2):
  "Strike vs ball challenges: Where are umpires missing?"
  [strike_ball_butterfly.png]
```

**Implementation:**

```python
# In run_abs_bot.py or new scripts/post_daily_thread.py

def post_daily_thread(challenges, target_date, image_paths):
    """Post a threaded daily report."""

    # Parent tweet: summary
    summary_text = build_daily_tweet(challenges, target_date)
    summary_text += "\n\nThread: Top 3 challenges 👇"

    parent = post_tweet(summary_text, image_paths['summary'])
    if not parent:
        print("Failed to post parent tweet")
        return

    parent_id = parent['tweet_id']
    print(f"Posted parent: {parent['url']}")

    # Reply with top 3 challenges
    top_3 = rank_challenges_by_impact(challenges)[:3]

    for i, challenge in enumerate(top_3):
        impact = challenge.get('impact', {}).get('impact_score', 0)
        result = "OVERTURNED" if challenge['result'] == 'overturned' else "UPHELD"

        tweet_text = (
            f"#{i+1}: {result} - Impact: {impact:.0f}\n"
            f"{challenge['away']}@{challenge['home']} "
            f"{'T' if challenge['half'] == 'top' else 'B'}{challenge['inning']}\n"
            f"{challenge['batter']} vs {challenge['pitcher']}\n"
            f"{challenge['impact'].get('count_before', '?')} count, "
            f"{challenge['outs']} out"
        )

        reply = post_tweet(tweet_text, image_paths[f'challenge_{i+1}'],
                          reply_to_id=parent_id)

        if reply:
            print(f"  Posted #{i+1}: {reply['url']}")
            parent_id = reply['tweet_id']  # Chain replies
        else:
            print(f"  Failed to post #{i+1}")
            break  # Stop thread if one fails
```

**Thread best practices:**
- Keep parent tweet short + clear hook
- Number replies for easy scanning (#1, #2, #3)
- Each reply should stand alone (assume reader didn't see parent)
- Post entire thread quickly (within 60 seconds) before algo interrupts
- Add 👇 emoji to parent to signal thread

---

## 5. Implementation Roadmap

### Phase 1: GitHub Actions Setup (Week 1)

- [ ] Create `.github/workflows/daily_abs_bot.yml`
- [ ] Add Twitter API secrets to GitHub repo settings
- [ ] Test manual trigger (`workflow_dispatch`)
- [ ] Verify cron schedule runs correctly
- [ ] Set up error notification emails

### Phase 2: Image Template System (Week 1-2)

- [ ] Add `format='twitter'` parameter to `generate_challenge_image()`
- [ ] Modify layout for 12x6.75 (1200x675) aspect ratio
- [ ] Update color scheme to orange accent (`#FF6B35`)
- [ ] Standardize footer format across all image types
- [ ] Test generated images in Twitter's card validator

### Phase 3: Enhanced Error Handling (Week 2)

- [ ] Add `@retry_on_rate_limit` decorator to `post_tweet()`
- [ ] Handle "no games found" gracefully
- [ ] Add duplicate tweet detection (append challenge ID to text)
- [ ] Log all errors to `logs/twitter_bot.log`
- [ ] Set up Discord webhook for critical alerts (optional)

### Phase 4: Thread Posting (Week 2-3)

- [ ] Add `reply_to_id` parameter to `post_tweet()`
- [ ] Create `post_daily_thread()` function
- [ ] Test thread posting with dry-run mode
- [ ] Add thread preview mode (prints URLs without posting)

### Phase 5: Content Queue (Week 3-4)

- [ ] Implement `ContentQueue` class in `scripts/content_queue.py`
- [ ] Modify `run_abs_bot.py` to populate queue instead of direct posting
- [ ] Create `scripts/post_from_queue.py` for scheduled posting
- [ ] Add 3 GitHub Actions workflows (9am, 12pm, 3pm posting times)
- [ ] Test queue workflow end-to-end

### Phase 6: Engagement Tracking (Week 4+)

- [ ] Set up Twitter API v2 analytics endpoint access
- [ ] Create `data/twitter_analytics.json` schema
- [ ] Add `scripts/fetch_engagement_stats.py`
- [ ] Build weekly analysis notebook in marimo
- [ ] Adjust content strategy based on engagement data

### Phase 7: Advanced Content Types (Ongoing)

- [ ] Weekly umpire scorecards (heat maps, percentile sliders)
- [ ] Team strategy deep dives
- [ ] Catcher framing impact analysis
- [ ] Pitch type accuracy breakdowns
- [ ] Pre/post challenge win probability swings

---

## 6. Testing Strategy

### Local Testing

```bash
# 1. Test image generation (no posting)
python scripts/run_abs_bot.py --date 2026-03-17 --dry-run

# 2. Test posting to dev account
export TWITTER_DRY_RUN=0
export TWITTER_ACCESS_TOKEN=<dev_account_token>
python scripts/run_abs_bot.py --date 2026-03-17 --post

# 3. Test thread posting
python scripts/post_daily_thread.py --date 2026-03-17 --test-account

# 4. Test queue workflow
python scripts/run_abs_bot.py --date 2026-03-17 --queue-only
python scripts/post_from_queue.py --dry-run
```

### GitHub Actions Testing

```bash
# 1. Test manual trigger (workflow_dispatch)
# Go to Actions tab > Daily ABS Bot > Run workflow

# 2. Test cron schedule (wait for scheduled run)
# Check Actions tab for automated runs

# 3. Monitor logs
# Actions tab > workflow run > job logs

# 4. Verify output
# Check output/abs/<date>/ directory in repo
```

### Pre-Launch Checklist

- [ ] Generate 7 days of images in dry-run mode
- [ ] Review all images for brand consistency
- [ ] Test posting 10 tweets to dev account
- [ ] Verify thread structure renders correctly
- [ ] Test rate limit handling (post 15 tweets in 15 minutes)
- [ ] Test duplicate tweet rejection (post same text twice)
- [ ] Test error notification emails
- [ ] Document all credentials and secrets
- [ ] Set up monitoring dashboard (GitHub Actions status)

---

## 7. Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Twitter API changes | High | Medium | Monitor API changelog, use versioned endpoints |
| Rate limits exceeded | Medium | Low | Implement backoff, spread posts throughout day |
| Image generation failure | Medium | Low | Generate all images before posting, skip failed ones |
| GitHub Actions downtime | Medium | Very Low | Have manual backup script ready |
| Duplicate content posted | Low | Medium | Check queue before adding, unique tweet IDs |
| MLB API data delayed | Medium | Medium | Run bot 8am (5+ hours after games) |
| Account suspended | High | Very Low | Follow Twitter Automation Rules, no spam |

**Twitter Automation Rules compliance:**
- Do not spam users (posting to own timeline only)
- Do not mislead users (clear data source attribution)
- Do not bypass rate limits (implement proper backoff)
- Do not violate privacy (only use public MLB data)

---

## 8. Success Metrics

### Quantitative

- **Consistency:** 100% of game days posted (0 missed days)
- **Speed:** Posted within 6 hours of final game (8am ET)
- **Engagement rate:** >2% (likes + RTs / impressions)
- **Growth:** 100 followers in first month
- **Uptime:** 99%+ workflow success rate

### Qualitative

- Brand recognition: "@sabrmagician" associated with ABS content
- Community feedback: Positive replies, quote tweets
- Media pickup: Other accounts sharing/referencing your content
- Differentiation: Visual quality clearly better than competitors

### Comparable Benchmarks

- **@UmpScorecards:** 80K followers, posts within 12 hours of game
- **@would_it_dong:** 120K followers, instant posting during games
- **@blandalytics:** 15K followers, weekly posts, high engagement

**Realistic Year 1 target:** 5K followers, 3-5% engagement rate, recognized as #1 source for ABS visuals.

---

## 9. Future Enhancements

### Live Game Mode

Instead of daily batch processing, post challenges in real-time during games:

- Poll MLB game feeds every 30 seconds
- Detect challenges as they happen (check `reviewDetails` field)
- Generate + post image within 60 seconds
- Much higher engagement (timely content)
- Requires long-running process (not GitHub Actions - use cloud VM)

### Multi-Platform

- **Bluesky:** Same API, smaller audience, easier growth
- **Threads:** Instagram-owned, growing fast, baseball community present
- **Discord:** Daily digest posted to baseball analytics servers

### Interactive Content

- **Twitter polls:** "Who had the worst call today?"
- **Reply threads:** "See a bad call? Tag me with game + inning"
- **Custom requests:** "DM me player names for custom challenge cards"

### Monetization (Long-Term)

- **Premium tier:** Exclusive content for Patreon supporters
- **Sponsorships:** Partner with baseball analytics sites
- **Consulting:** Use bot success as portfolio for automation consulting

---

## 10. References

### Documentation

- **Twitter API v2:** https://developer.twitter.com/en/docs/twitter-api
- **tweepy docs:** https://docs.tweepy.org/en/stable/
- **GitHub Actions:** https://docs.github.com/en/actions
- **matplotlib image specs:** https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html

### Existing Code

- `/src/bots/abs_challenge_bot.py` - Challenge detection + image generation
- `/src/bots/twitter_poster.py` - Tweet posting with dry-run mode
- `/scripts/run_abs_bot.py` - Daily CLI runner
- `/src/visualization/stat_cards.py` - Dark theme color constants
- `.github/workflows/deploy-site.yml` - Example GitHub Actions workflow

### Competitor Analysis

- **@UmpScorecards** - Model for consistency + automation
- **@would_it_dong** - Model for timeliness + simplicity
- **@blandalytics** - Model for visual quality
- **@PitcherList** - Model for brand identity

---

## Conclusion

This pipeline transforms a manual daily task into a fully automated brand machine. The key is consistency - posting every single day with the same visual quality creates audience trust and expectation.

**Start simple:** Get GitHub Actions + basic posting working first. Add thread support, queue system, and engagement tracking incrementally.

**The real work is content variety:** Once automation runs smoothly, focus on creating new chart types, storylines, and angles. The automation just gets it in front of people - the content quality determines growth.

**Timeline:** Core pipeline (Phases 1-4) should be live in 2 weeks. Queue system + analytics in 4 weeks. Then shift focus to content creation.

# Social Media Strategy

Content calendar framework, posting schedule, format specs, and engagement tactics for building @sabrmagician as a baseball analytics brand.

---

## Account Structure

### @sabrmagician (Primary Personal Brand)
- **Purpose:** Original analysis, data visualization, Ottoneu strategy, personality-driven content
- **Voice:** Expert but accessible. Data-driven but opinionated. Teaching-focused.
- **Audience:** Serious baseball fans, Ottoneu players, analytics community
- **Posting frequency:** Daily during season, 3-5x/week offseason

### @roboumpstats (Automated Bot)
- **Purpose:** Daily ABS challenge reports, umpire scorecards, automated visual content
- **Voice:** Factual, consistent, zero personality (pure data reporting)
- **Audience:** Umpire accountability community, ABS curious fans, media looking for graphics
- **Posting frequency:** 1-2x daily (automated), April-October

### @windwatchers (Future Weather Bot)
- **Purpose:** Daily ballpark weather impact graphics
- **Voice:** Simple, weather-focused, actionable for daily fantasy/betting
- **Audience:** DFS players, bettors, weather-curious fans
- **Posting frequency:** 1x daily (automated), April-October

---

## Content Pillars

### Pillar 1: ABS Challenge Content (20% of posts)
**Format:** Automated reports, umpire analysis, challenge strategy
**Examples:**
- Daily ABS scorecard (automated)
- "Phillies are challenging 3-2 counts 40% more than league average"
- Umpire accuracy leaderboards (weekly)
- Most impactful challenge of the week

**Why it works:** First-mover advantage. Nobody else owns this space. UmpScorecards model proven.

### Pillar 2: Ottoneu Strategy (30% of posts)
**Format:** Value analysis, SABR Points strategy, tools promotion
**Examples:**
- "Most undervalued hitters in Ottoneu SABR right now" (chart)
- "Why high-K pitchers are worth more in SABR than FGPts" (thread)
- MoLab notebook updates
- Trade analysis breakdowns

**Why it works:** Underserved niche. Dedicated, engaged audience. You play 9 leagues and understand it deeply.

### Pillar 3: Data Visualization (30% of posts)
**Format:** Beautiful charts, stat cards, Statcast breakdowns
**Examples:**
- Pitcher stat cards (Pitcher List style)
- Batted ball by pitch type tables
- "Here's every Aaron Judge home run in 2024" (spray chart)
- Pitch movement comparisons

**Why it works:** Core differentiator. Most analytics content is text or ugly spreadsheets. You make data beautiful.

### Pillar 4: Teaching & Methodology (10% of posts)
**Format:** Explainers, metric definitions, methodology transparency
**Examples:**
- "How run expectancy works" (thread)
- "What does 'stuff+' actually measure?"
- "How I calculate ABS challenge impact scores"
- "Why I use DuckDB instead of Postgres"

**Why it works:** Builds trust. Shows your work. Educates audience. Gets shared by teachers/writers.

### Pillar 5: Hot Takes & Engagement (10% of posts)
**Format:** Reactions, predictions, replies, engagement farming
**Examples:**
- Reply to breaking news with relevant chart
- "Bold prediction: Skubal leads MLB in K% again" (with data)
- Quote tweet Baseball Savant with additional context
- Engage with other analytics creators

**Why it works:** Grows reach. Gets you in timely conversations. Shows personality beyond just data.

---

## Weekly Content Calendar (In-Season)

### Monday
- **Morning:** Ottoneu value finder update (undervalued players from weekend)
- **Afternoon:** ABS weekly recap (if applicable)
- **Evening:** Prospect spotlight or player profile

### Tuesday
- **Morning:** ABS daily scorecard (automated via @roboumpstats)
- **Afternoon:** Data viz post (stat card, spray chart, or heatmap)
- **Evening:** Engage with community (replies, QTs)

### Wednesday
- **Morning:** ABS daily scorecard (automated)
- **Midday:** Weather impact graphic (via @windwatchers, future)
- **Afternoon:** Teaching post (metric explainer or methodology)
- **Evening:** Ottoneu strategy thread

### Thursday
- **Morning:** ABS daily scorecard (automated)
- **Afternoon:** Player comparison (radar chart or stat card)
- **Evening:** Hot take or prediction with data

### Friday
- **Morning:** ABS daily scorecard (automated)
- **Afternoon:** Weekend series matchup preview
- **Evening:** SABR Points strategy content

### Saturday
- **Morning:** Ottoneu trade analysis or roster review
- **Afternoon:** Live game Statcast highlights (if relevant)

### Sunday
- **Morning:** Weekly ABS leaderboard update
- **Afternoon:** "Week in review" data viz thread
- **Evening:** Prep Monday's Ottoneu value finder

---

## Posting Schedule (Daily Template)

### Morning (8:00 AM ET)
- **@roboumpstats:** Daily ABS scorecard (automated)
- **Goal:** Catch people checking Twitter with morning coffee

### Midday (12:00 PM ET)
- **@windwatchers:** Ballpark weather graphic (automated, future)
- **Goal:** Post after lineups are announced, before first pitch

### Afternoon (3:00 PM ET)
- **@sabrmagician:** Main daily content (viz, analysis, or thread)
- **Goal:** Peak Twitter engagement time

### Evening (7:00 PM ET)
- **@sabrmagician:** Engagement post (reply, QT, or hot take)
- **Goal:** Join in-game conversations, react to news

---

## Format Specifications

### Image Specs

| Format | Dimensions | Use Case | File Size |
|--------|------------|----------|-----------|
| Landscape | 1200x675 (16:9) | Standard tweet image | <1MB |
| Square | 1080x1080 | Instagram cross-post | <1MB |
| Tall card | 1080x1920 (9:16) | Player stat cards | <1MB |
| Wide chart | 1400x700 | Detailed leaderboards | <1MB |

### Twitter Best Practices
- Images load better than external links
- 4 images max per tweet (but 1-2 is better for engagement)
- Alt text for accessibility (and SEO)
- First line must hook - people scroll fast
- Threads: number them (1/7, 2/7, etc.)

### Visual Consistency
- **Colors:** Dark background (#0e1117), orange accent (#FF6B35), teal secondary (#4ECDC4)
- **Watermark:** @sabrmagician (or account handle) in bottom right, subtle
- **Font:** Clean sans-serif, readable on mobile
- **Team colors:** Use `src/visualization/team_colors.py` for consistency

---

## Content Types & Formats

### 1. Automated Bot Posts (Daily)
**Accounts:** @roboumpstats, @windwatchers
**Format:** Single image + factual caption
**Example:**
```
Yesterday's ABS Challenges:
- 18 total challenges
- 52% overturned
- Most accurate umpire: John Doe (5/5)
- Highest impact: Dodgers 8th inning (94/100)
```
**Image:** Daily scorecard graphic
**Frequency:** 1x/day per bot
**Automation:** GitHub Actions, 8am ET

### 2. Data Visualization Posts
**Account:** @sabrmagician
**Format:** Image + short insight
**Example:**
```
Aaron Judge vs different pitch types in 2024:

4-seam: .350 xBA, 95 mph avg EV
Slider: .280 xBA, 89 mph avg EV
Changeup: .240 xBA, 85 mph avg EV

He destroys fastballs. Struggles with offspeed.
```
**Image:** Batted ball by pitch table
**Frequency:** 3-4x/week
**Engagement:** Tag player, team account, or use trending hashtags

### 3. Strategy Threads
**Account:** @sabrmagician
**Format:** Multi-tweet thread with charts
**Example:**
```
1/7: Why SABR Points rewards high-K pitchers more than FGPts

SABR ignores hits allowed. FGPts penalizes them.

This creates massive valuation gaps. Let me show you:
```
**Images:** 2-3 charts showing the math
**Frequency:** 1x/week
**Engagement:** Pin to profile if high-performing

### 4. Player Stat Cards
**Account:** @sabrmagician
**Format:** Single tall image
**Example:**
```
Tarik Skubal, SP, Tigers

The best pitcher in baseball right now. Here's why:
```
**Image:** Pitcher List-style stat card
**Frequency:** 2-3x/week
**Engagement:** Tag player, team, beat writers

### 5. Tool/Notebook Promotion
**Account:** @sabrmagician
**Format:** Screenshot + link
**Example:**
```
New tool: Ottoneu Value Finder

Find undervalued players in your league format. Sort by surplus value. Export to CSV.

Try it here: [MoLab link]
```
**Image:** Screenshot of notebook in action
**Frequency:** 1x/week
**Engagement:** Post in Ottoneu subreddit, Discord

### 6. Quick Hits (Engagement Farming)
**Account:** @sabrmagician
**Format:** Text + small image or GIF
**Example:**
```
Hot take: [Player X] finishes top 10 in WAR this year.

Here's the Statcast data that backs it up:
```
**Image:** Percentile bars or small chart
**Frequency:** 2-3x/week
**Engagement:** Reply to trending topics, QT big accounts

---

## Engagement Tactics

### Growing Followers

**1. Reply Strategy**
- Set up TweetDeck columns for:
  - @BaseballSavant tweets (reply with additional viz)
  - @FanGraphs new posts (add context)
  - @PitcherList content (complement with Statcast data)
  - Ottoneu community hashtags (#ottoneu, #sabrpoints)
- Reply within first 30 minutes for max visibility
- Add value, don't just agree
- Include a chart when possible

**2. Quote Tweet Strategy**
- QT breaking news with instant analysis
- QT Baseball Savant data releases with your own viz
- QT bad takes with data corrections (nicely)
- QT other creators' work and build on it

**3. Collaboration**
- Tag complementary creators (not direct competitors)
- Share others' work generously
- Offer to create charts for writers who ask questions
- Join analytics Twitter chats/spaces

**4. Hashtag Strategy**
- #Statcast (when using Savant data)
- #Ottoneu, #SABRPoints (for fantasy content)
- #BaseballAnalytics (for technical posts)
- Team hashtags (#Dodgers, #Yankees, etc.) when team-specific
- Avoid over-hashtagging (2-3 max)

### Increasing Engagement

**1. Ask Questions**
- "Which prospect breakout are you most excited for?"
- "SABR or FGPts format - which do you prefer and why?"
- "What's your favorite Statcast metric?"
- People love giving their opinion

**2. Polls**
- "Who has the best pitch in baseball?" (4 options)
- "Which metric matters most for hitters?" (xBA, Barrel%, xwOBA, K%)
- "Will [Player X] hit 30 HR this year?" (Yes/No)
- Polls boost engagement 3x

**3. "Guess the Player" Games**
- Show percentile bars, hide the name
- Show spray chart, hide the name
- Show pitch movement plot, hide the name
- Reveals in replies after engagement

**4. Hot Button Topics**
- WAR vs other metrics (people argue forever)
- Umpire accuracy (everyone hates umps)
- MVP debates with data
- Hall of Fame cases

### Building Community

**1. Regular Series**
- "Statcast Sunday" - weekly deep dive
- "Ottoneu Wednesday" - fantasy strategy
- "Prospect Friday" - minor league spotlight
- Consistency builds anticipation

**2. Respond to Replies**
- Answer questions in comments
- Thank people who share your content
- Engage with criticism constructively
- Build relationships, not just audience

**3. Create Value for Others**
- Offer free chart generation for writers (credit them)
- Share notebooks openly
- Explain methodology transparently
- Help people learn

---

## Content Creation Workflow

### Daily (15-30 minutes)
1. Check @roboumpstats automated post (8am) - verify it ran
2. Scan Twitter for trending topics (TweetDeck)
3. Engage: reply to 5 tweets, QT 1 relevant post
4. Post main content (3pm) - from weekly prep
5. Evening engagement (7pm) - reply to comments

### Weekly Prep (2 hours Sunday)
1. Generate 3-5 data viz posts for the week
2. Export images, draft captions
3. Schedule or queue in notes app
4. Identify thread topics for the week
5. Prep Ottoneu value finder data

### Monthly Planning (1 hour)
1. Review analytics (Twitter Analytics, MoLab stats)
2. Identify top-performing content types
3. Plan monthly content themes
4. Update automation scripts
5. Refresh datasets

---

## Analytics & Metrics

### Track These Weekly
- Follower growth rate
- Engagement rate (likes + RTs + replies / followers)
- Top-performing posts (by engagement)
- MoLab notebook sessions
- Streamlit app sessions (once deployed)

### Success Milestones
- [ ] 100 followers (@roboumpstats)
- [ ] 250 followers (@sabrmagician)
- [ ] 500 followers (combined)
- [ ] 1,000 followers (combined)
- [ ] First media mention/embed
- [ ] First collaboration with another creator
- [ ] 50 MoLab notebook sessions/month
- [ ] 100 Streamlit app sessions/month

### What to Double Down On
- If automated bot posts get high engagement: add more chart types
- If Ottoneu content performs: increase frequency
- If threads get more engagement than single posts: shift to threads
- If certain viz types go viral: create series

### What to Prune
- If teaching posts get low engagement: reduce to monthly
- If hot takes don't land: focus on data
- If certain chart types flop: kill them

---

## Brand Voice Guidelines

### Do
- Be confident in your analysis (you have the data)
- Show your work (methodology transparency)
- Teach, don't talk down
- Use data to support opinions, not replace them
- Credit others' work generously
- Admit when you're wrong
- Be specific (numbers, examples, not generalizations)

### Don't
- Use inflated language ("comprehensive," "robust," "pivotal")
- Gatekeep analytics knowledge
- Argue for argument's sake
- Subtweet or be snarky
- Oversell your tools ("revolutionary," "game-changing")
- Use chatbot pleasantries ("I hope this helps!")
- Hedge excessively ("it seems like maybe possibly")

### Tone Examples

**Good:**
"Skubal's stuff+ is 127, top 3% of MLB. His location+ is 108. He's not lucky, he's elite."

**Bad:**
"Skubal's metrics are quite impressive across the board and seem to suggest he's performing at a high level."

**Good:**
"Here's why SABR Points makes high-K pitchers more valuable than FGPts. The math is simple:"

**Bad:**
"I think SABR Points might offer a unique perspective on pitcher valuation that could be interesting to explore."

---

## Automation Setup

### GitHub Actions Workflow

**File:** `.github/workflows/daily-abs-bot.yml`

```yaml
name: Daily ABS Bot
on:
  schedule:
    - cron: '0 13 * * *'  # 8am ET (1pm UTC)
  workflow_dispatch:

jobs:
  run-abs-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run ABS bot
        env:
          TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
          TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
          TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
        run: python scripts/run_abs_bot.py --post
```

### Error Handling & Monitoring

**If bot fails:**
1. GitHub Actions sends email notification
2. Check logs in Actions tab
3. Post manually if critical
4. Fix issue for next day

**Weekly health check:**
- Review last 7 days of bot runs
- Verify all images generated correctly
- Check engagement metrics
- Update cached data if needed

---

## Cross-Platform Strategy (Future)

### Twitter First, Always
- Twitter is where baseball analytics community lives
- Optimize everything for Twitter format
- Other platforms are secondary

### Instagram (Optional)
- Repost square (1080x1080) versions of charts
- Use Stories for behind-the-scenes
- Lower priority - only if Twitter content easily adapts

### Reddit (Engagement, Not Posting)
- r/Ottoneu - share tools when relevant
- r/fantasybaseball - answer questions, share viz when asked
- Don't spam - add value in threads

### Bluesky (Not Now)
- User specifically prefers Twitter/X
- Community hasn't migrated there for baseball
- Revisit if Twitter changes dramatically

### YouTube/TikTok (Future)
- Short-form video explainers (how to use tools)
- Chart generation time-lapses
- Tool walkthroughs
- Only pursue after 1,000 Twitter followers

---

## Next Actions

1. Apply for Twitter Developer account (@roboumpstats)
2. Set up GitHub Actions for daily posting
3. Create 1 week of pre-generated content (images + captions)
4. Build TweetDeck with monitoring columns
5. Draft first 5 threads (Ottoneu strategy, ABS insights, methodology)
6. Identify 20 accounts to engage with regularly
7. Schedule first bot run (dry-run mode)
8. Launch automated posting April 1, 2026

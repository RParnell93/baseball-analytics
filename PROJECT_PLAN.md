# Baseball Analytics - Project Plan

**Owner:** Robert Parnell ([@sabrmagician](https://twitter.com/sabrmagician))
**Started:** March 2026
**Repo:** [RParnell93/baseball-analytics](https://github.com/RParnell93/baseball-analytics) (public)

---

## Vision & Goals

Build a personal baseball analytics platform that:
- Powers original analysis, models, and visualizations for Twitter/X
- Feeds interactive notebooks, dashboards, and automated social media
- Makes Robert a better Ottoneu player and a recognized voice in the baseball analytics community
- Serves as a Python learning vehicle (owner knows SQL well, learning Python through this project)

**Brand positioning:** Visual-first, personality-driven analytics. The market has data (Savant), tools (FanGraphs), and writing (BP, Athletic). What's missing is beautiful, shareable, automated visual content. The model to follow is @UmpScorecards: one consistent thing, done better than anyone, automated, every day.

**Primary account:** @sabrmagician - personal brand, original analysis, data viz
**Bot account (planned):** @roboumpstats - automated daily ABS reports

---

## Current Status (as of March 2026)

### Working

| Component | Status | Notes |
|-----------|--------|-------|
| DuckDB database (local) | Done | 7 tables, 800K+ rows total |
| MotherDuck cloud sync | Done | All 7 tables synced |
| Data refresh pipeline | Done | `refresh_all.py` - Statcast, FG, Ottoneu, player IDs |
| MoLab notebooks (2) | Done | Database Explorer + Ottoneu Value Finder, live on MoLab |
| ABS challenge data collection | Done | 1,632 challenges, spring training 2026 |
| ABS team rankings + umpire leaderboards | Done | YTD charts, daily charts, Cactus/Grapefruit splits |
| ABS impact scoring | Done | Run expectancy + count leverage, 0-100 scale |
| ABS bot pipeline | Done | Detection, scoring, image gen, tweet text, dry-run mode |
| Ottoneu lineup API client | Done | Login, roster, lineup read/write, player moves |
| Visualization library | Done | Charts, stat cards, team colors, style/watermark |
| Matchup explorer app | Done | Streamlit, hitter vs pitcher |
| Static landing page | Done | site/index.html, GitHub Pages, dark theme |
| Competitor research | Done | research/competitor_landscape.md |

### Not Yet Started

- Twitter API credentials / automated posting
- Weather bot for outdoor ballparks
- ML models (projection blending, breakout prediction)
- Trade analyzer
- Roster optimizer
- Google Sheets integration

---

## Active Workstreams

### 1. ABS Challenge Bot (highest priority)

This is the first-mover opportunity. Nobody is doing automated daily ABS visual content on social media. Spring training 2026 is the proving ground before ABS expands to the regular season.

**Done:**
- Challenge data pipeline from MLB Stats API
- Team success rate charts (by team, by league)
- Umpire leaderboards (overall, Cactus/Grapefruit split)
- Strike vs ball butterfly and stacked charts
- Impact scoring (run expectancy + count leverage)
- Daily bot runner with image generation and tweet text

**Next:**
- Get Twitter API credentials for @roboumpstats
- Daily umpire scorecard with strike zone heat maps
- Pitch type accuracy breakdown (which pitches get overturned most)
- Team strategy deep dives (are teams targeting umpire weak spots)
- Catcher framing impact analysis
- Full automated daily report pipeline posting to Twitter

**Future ABS ideas (backlog):**
- Umpire percentile sliders (Savant-style)
- Player challenge cards (who benefits most from challenges)
- Pre-ABS vs ABS zone comparison (2025 vs 2026 same umpires)
- Missed challenge opportunities (pitches that should have been challenged)
- Count leverage and inning splits
- Score differential analysis

### 2. Data Visualization & Brand Building

Viz is the core differentiator. Every chart should be clean, branded, professional, shareable on mobile.

**Done:**
- Team colors module (all 30 MLB teams)
- Reusable chart functions (heatmap, pitch movement, exit velo, spray, radar)
- Stat card template (Pitcher List-style, dark theme)
- Batted ball by pitch type tables with conditional formatting
- @sabrmagician watermark on all output

**Next:**
- Create 10 manual Twitter posts with original visualizations
- Swing analytics visualizations (bat speed, blast rate, attack angle)
- Player comparison radar charts
- Rolling performance line charts

**Visualization ideas (backlog):**
- Animated pitch sequences
- Pitch tunneling visualizations
- 3D pitch trajectories
- Defensive positioning / shift charts
- Park factor visualizations with stadium overlays
- Swing decision zone maps
- Contact quality waterfalls

### 3. Ottoneu Fantasy Tools

Playing 9 leagues, all SABR Points. Nobody produces dedicated SABR Points content - this is a niche to own.

**Done:**
- FGPts and SABR scoring calculators
- Ottoneu value data in database (FGPts + SABR avg salaries)
- Value Finder notebook on MoLab
- Authenticated lineup API client (login, roster, lineup changes, player moves)

**Next:**
- Projection blending (Steamer + ZiPS + ATC)
- Surplus value calculator for all players
- Trade analyzer notebook

**Backlog:**
- Roster optimizer (given roster + budget, maximize surplus)
- Arbitration tracking (salary inflation predictions)
- RP usage predictor (likelihood a reliever pitches today)

### 4. MoLab + MotherDuck Infrastructure

Cloud notebooks connected to cloud database. Anyone can explore the data.

**Done:**
- MotherDuck database with all 7 tables
- Database Explorer notebook on MoLab
- Ottoneu Value Finder notebook on MoLab

**Next:**
- Rewire MoLab notebooks to connect to MotherDuck (currently local DuckDB)
- Push ABS challenge data to MotherDuck
- Set up scheduled refresh scripts to keep MotherDuck current

### 5. Weather Bot (future)

Separate Twitter account. Daily visuals showing which parks favor hitters today and why.

**Not started.** Requires:
- Open-Meteo API integration (free)
- Ballpark orientation data (wind direction relative to field)
- Daily graphic generation (wind arrows on field diagrams)
- Twitter API credentials

---

## Backlog (by category)

### Apps & Dashboards
- Player Profile Dashboard (enter name, see full stat profile)
- Pitch Arsenal Analyzer (any pitcher's mix, movement, usage)
- Historical Comp Tool ("who is this player most similar to?")
- Live Game Tracker (real-time Statcast viz during games)
- Deploy Streamlit apps to Streamlit Community Cloud

### Models & ML
- Linear regression: predict HR from barrel rate + avg exit velo
- Player similarity (k-nearest neighbors for comps)
- Projection blending with custom weights
- Pitch classification from trajectory data
- Build own xBA/xwOBA model
- Breakout prediction model
- Stuff+ model
- Aging curves
- DSPy for LLM pipelines (tweet generation, scouting reports, NL-to-SQL)

### Content & Social
- Domain name (sabrmagician.com or similar)
- Ottoneu-specific social content (SABR Points strategy)
- Minor league prospect tracking with Statcast viz
- Defensive metrics visualization
- Park factor weekly updates
- Catcher framing breakdowns

### Infrastructure
- Google Sheets integration
- GitHub Actions for scheduled data refresh
- Automated site image refresh on schedule

---

## Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Database | DuckDB | Columnar, fast analytics on millions of rows, zero config, single file, standard SQL |
| Cloud DB | MotherDuck | Cloud DuckDB, free tier, syncs with local, accessible from MoLab |
| Notebooks | marimo | Reactive, Git-friendly (.py files), native to MoLab for cloud hosting |
| Interactive viz | Plotly | Rich interactivity, good for web, kaleido for PNG export |
| Static viz | matplotlib + seaborn | Industry standard for baseball Twitter, better layout control |
| PNG export | kaleido 0.2.1 | 1.x is broken, must pin to 0.2.1 |
| Web apps | Streamlit | Pure Python, free hosting, fast prototyping |
| Social | Twitter/X via tweepy | Baseball analytics community lives on Twitter |
| Cloud notebooks | MoLab | Free, imports from public GitHub URLs, marimo-native |
| DuckDB version | v1.4.1 | MotherDuck doesn't yet support v1.5.0 |

---

## Roadmap (March - September 2026)

### Phase 1: Launch & Prove It (Now - April 15)
**Goal:** Ship the ABS bot and start posting daily before Opening Day (March 26).

| Week | Target | Deliverable |
|------|--------|-------------|
| Mar 21-26 | mlbumpviz live | Done - mlbumpviz.streamlit.app deployed |
| Mar 22-28 | Twitter API setup | Get @roboumpstats credentials, first test tweets |
| Mar 26-31 | Opening Day week | First automated daily ABS report posted to Twitter |
| Apr 1-7 | Daily cadence | One ABS scorecard graphic after every day's games, posted by 11pm ET |
| Apr 8-15 | Weekly recap | Weekly "ABS Report Card" thread - top/bottom umpires, trends, fun stats |

**Ship list:**
- Twitter API keys for @roboumpstats (or post from @sabrmagician initially)
- Daily cron job: `scripts/run_abs_bot.py --post` (or GitHub Action)
- One consistent visual format for daily reports (strike zone + metrics)
- Weekly recap thread template

### Phase 2: Build the Habit (Apr 15 - May 31)
**Goal:** Consistent daily posting. Grow from 0 to 500 followers. Get first media embed.

| Week | Target | Deliverable |
|------|--------|-------------|
| Apr 15-30 | Daily ABS + 2 original viz/week | Pitch type breakdowns, umpire deep dives |
| May 1-15 | Ottoneu content begins | SABR Points value alerts, waiver wire picks |
| May 16-31 | Weather bot MVP | First daily park weather impact graphic |

**Ship list:**
- 2-3 original data viz posts per week from @sabrmagician (not just bot output)
- Ottoneu Value Finder promoted to Ottoneu community (Reddit, Slack, Discord)
- Weather bot: Open-Meteo API + field orientation data + daily wind/temp graphic
- First "explainer" thread (what ABS is, how challenges work, with your data)

### Phase 3: Expand & Engage (June - July)
**Goal:** Multiple content streams running. 1,000+ followers. Community engagement.

| Target | Deliverable |
|--------|-------------|
| Player comparison cards | Shareable stat cards for any batter/pitcher |
| Pitch arsenal analyzer | Interactive notebook or Streamlit app |
| Quote-tweet analysis | React to big moments with instant data viz |
| Guest content | Pitch a guest post to FanGraphs Community or reach out to a podcast |

**Ship list:**
- Player card template (dark theme, percentile bars, headshot, key stats)
- At least 1 "instant reaction" data viz per week during games
- Engage with 5-10 analytics accounts daily (replies, quote-tweets, not just likes)
- sabrmagician.com domain (optional, redirect to GitHub Pages or Streamlit)

### Phase 4: Differentiate (August - September)
**Goal:** Move beyond daily reporting into original analysis. Establish expertise.

| Target | Deliverable |
|--------|-------------|
| ML models | Breakout prediction, projection blending |
| Original research | 1 deep analysis thread per week |
| Trade analyzer | Ottoneu trade value tool |
| Saber Seminar | Attend Aug 2026 in Chicago (networking) |

---

## Marketing Plan

### The Core Problem
You have good tools and data but no audience yet. The baseball analytics Twitter community is tight-knit but welcoming to people who ship real work. You don't need a marketing budget - you need consistency and engagement.

### Channel Strategy

**Twitter/X (primary - 80% of effort)**

This is where baseball analytics lives. Period. The entire community (media, front offices, fans, content creators) is here.

*Content mix (aim for 5-7 posts/week):*
- 3-4 automated ABS reports (daily bot output, low effort once set up)
- 1-2 original data viz posts (pitch breakdowns, player cards, trend analysis)
- 1 thread or explainer (ABS recap, Ottoneu strategy, metric explainer)
- Engagement: replies and quote-tweets count as content too

*Growth tactics:*
1. **Reply to bigger accounts with data.** When @UmpScorecards posts, reply with your ABS angle. When @mike_petriello shares Statcast data, add context from your analysis. Don't self-promote - add value. This is the #1 growth lever for analytics accounts.
2. **Quote-tweet games in progress.** When a controversial call happens, have a graphic ready within minutes. Timeliness = virality.
3. **Tag umpires by name.** When your bot posts an umpire's daily report, use their name. Fans searching for umpire names will find you.
4. **Use the right hashtags sparingly.** #Statcast, #MLB, #ABS, team-specific tags when relevant. Don't stuff.
5. **Pin your best visual.** The mlbumpviz app or a particularly clean data viz. First impression matters.
6. **Cross-post to Bluesky if you want** but don't split focus. Twitter first.

*Who to engage with (build relationships, not just followers):*
- @UmpScorecards (obvious overlap, they may RT you)
- @would_it_dong (similar automated concept)
- @mike_petriello (MLB's Statcast voice)
- @DSzymborski (FanGraphs, ZiPS)
- @TJStats, @SlangsOnSports (fellow independent data viz)
- @PitcherList (visual brand, potential collab)
- Beat writers who cover ABS/umpire topics

**Your Radio Guy (leverage this)**

You mentioned a radio connection. This is valuable:
- Ask if they'd mention @sabrmagician or mlbumpviz on air when discussing ABS/umpire topics
- Provide them a weekly "stat sheet" they can reference on air (2-3 interesting ABS facts)
- If they tweet, ask them to tag you when using your data
- One on-air mention with a call-to-action ("check out mlbumpviz.streamlit.app") is worth 100 tweets

**Reddit (secondary)**

- r/baseball: Share original analysis posts (not self-promo, genuine contributions). ABS discussion threads are popular.
- r/Sabermetrics: Smaller but engaged. Your deep analysis fits here.
- r/fantasybaseball: Ottoneu content, SABR Points strategy
- r/Ottoneu: Small but dedicated. Your Value Finder notebook is exactly what they want.

**Ottoneu Community (niche but high-value)**

- Ottoneu has its own forums, Slack channels, and Discord
- Share the Value Finder notebook link directly
- Post SABR Points strategy content
- This community is small (~5K active players) but extremely engaged and loyal

### Content Calendar Template (Weekly)

| Day | Content | Channel |
|-----|---------|---------|
| Mon | Weekend ABS recap thread | Twitter |
| Tue | Original data viz (pitch type, player card, etc.) | Twitter |
| Wed | ABS daily report (automated) | Twitter |
| Thu | Ottoneu waiver wire / value alert | Twitter + Ottoneu community |
| Fri | ABS daily report + weekend preview | Twitter |
| Sat | Game reaction viz (during games) | Twitter |
| Sun | "Week in ABS" thread or explainer | Twitter |

*Daily (automated):* ABS challenge report after games end

### Metrics to Track

Don't obsess over follower count. Track:
- **Impressions per post** (are people seeing your stuff?)
- **Engagement rate** (likes + replies + RTs / impressions)
- **Profile visits** (people checking you out)
- **Link clicks** to mlbumpviz.streamlit.app
- **Quote-tweets and embeds** (other accounts using your content)

Milestones:
- 100 followers: you exist
- 500 followers: you're getting noticed
- 1,000 followers: media people start following
- 5,000 followers: you're a recognized voice

### What NOT to Do

- Don't buy followers or use engagement bots
- Don't post low-effort takes or hot takes without data
- Don't spam hashtags or reply-spam big accounts
- Don't cross-post identical content to 5 platforms - focus on Twitter
- Don't wait until everything is perfect to start posting. Ship messy, iterate.

---

## Reference

### Ottoneu Scoring (SABR Points)

**Hitting:** AB (-1.0), H (5.6), 2B (2.9), 3B (5.7), HR (9.4), BB (3.0), HBP (3.0), SB (1.9), CS (-2.8)
**Pitching (SABR):** IP (5.0), K (2.0), BB (-3.0), HBP (-3.0), HR (-13.0), SV (5.0), HLD (4.0)
**Pitching (FGPts):** IP (7.4), K (2.0), H (-2.6), BB (-3.0), HBP (-3.0), HR (-12.3), SV (5.0), HLD (4.0)

Key difference: SABR ignores hits allowed (FIP-style). FGPts rewards contact managers with low BABIP.

**League structure:** 12 teams, 40-man rosters, $400 salary cap, all players via auction.

### Spring Training ABS Data

- 1,632 challenges across 26 days (Feb 20 - Mar 19, 2026)
- 52% overturn rate
- Cactus League (AZ): 15 teams, ~55 umpires
- Grapefruit League (FL): 15 teams, ~53 umpires
- Zero crossover between leagues

### Accounts to Study

| Account | Lesson |
|---------|--------|
| @UmpScorecards | One consistent format, automated, after every game = brand machine |
| @would_it_dong | Simple concept + immediate relevance + automation = viral |
| @blandalytics | Visual consistency, clean design, methodology transparency |
| @PitcherList | Consistent visual brand across every post |
| @TJStats | Timeliness, making stats accessible and surprising |
| @WrigleyWinds | Pick a niche and own it |
| @EnoSarris | Community engagement, elevating other voices |

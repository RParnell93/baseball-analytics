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

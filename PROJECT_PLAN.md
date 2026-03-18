# Baseball Analytics Side Project - Master Plan

**Owner:** Robert Parnell (@rparnell93)
**Started:** March 2026
**Goal:** Learn Python, baseball analytics, AI/ML, and data visualization. Build tools for Ottoneu fantasy baseball. Create a public presence with original analysis and automated content.

---

## Vision

Build a personal baseball analytics platform that:
1. Has a rich local database of historical and live MLB data
2. Powers original analysis, models, and visualizations
3. Feeds dashboards, web apps, and automated social media accounts
4. Makes you a better Ottoneu player and a recognized voice in the baseball analytics community

---

## Project Pillars

### 1. Database & Data Pipeline (Phase 1 - START HERE)
### 2. Data Visualization (Core Identity)
### 3. Fantasy/Ottoneu Tools
### 4. Dashboards & Web Apps
### 5. Social Media Automation
### 6. Models & AI/ML

---

## Phase 1: Database & Data Pipeline

### Database Choice: DuckDB

**Why DuckDB over SQLite or Postgres:**
- Built for analytics (columnar storage) - aggregations on millions of rows are 10-100x faster than SQLite
- Zero config, single file, no server to manage
- Can query CSV, Parquet, and JSON files directly without importing
- First-class Python integration
- You already know SQL - DuckDB uses standard SQL
- Free, open source, growing fast

**Data Scale:**
- Statcast pitch-level: ~700,000 pitches/season (2015-present)
- Player batting/pitching stats: ~150 years of data
- Total storage: single-digit GB range, easily handled

### Data Sources

| Source | What You Get | Access Method | Python Library |
|--------|-------------|---------------|----------------|
| **Statcast / Baseball Savant** | Pitch-level data: velocity, spin, movement, exit velo, launch angle, sprint speed, expected stats | Free CSV search + pybaseball | `pybaseball` |
| **FanGraphs** | Leaderboards, projections (Steamer, ZiPS, ATC), park factors, WAR, advanced stats | CSV export + pybaseball | `pybaseball` |
| **Baseball Reference** | Traditional stats, game logs, splits, awards, transactions | pybaseball wrappers | `pybaseball` |
| **Lahman Database** | Complete historical stats back to 1871 (batting, pitching, fielding, teams, awards) | Direct download (CSV/SQLite) | `pybaseball` or direct download |
| **Retrosheet** | Play-by-play data for every game back to 1921, event files | Free download | `retrosheet` package or manual parsing |
| **MLB Stats API** | Live scores, rosters, schedules, game feeds (official, free, no auth needed) | REST API | `statsapi` package |
| **Ottoneu** | Average player values, salary data, roster ownership % | CSV/XML export from ottoneu.fangraphs.com/averageValues | `requests` + parsing |
| **Chadwick Bureau** | Player ID mapping (cross-reference FanGraphs, Baseball Ref, Retrosheet, MLB IDs) | GitHub CSV download | Direct download |

### pybaseball - Your Main Tool

The `pybaseball` library is the Swiss Army knife. Key functions:
- `statcast(start_dt, end_dt)` - pull Statcast pitch data for date range
- `batting_stats(start_season, end_season)` - FanGraphs batting leaderboard
- `pitching_stats(start_season, end_season)` - FanGraphs pitching leaderboard
- `playerid_lookup(last, first)` - find player IDs
- `statcast_batter(start_dt, end_dt, player_id)` - single batter Statcast data
- `statcast_pitcher(start_dt, end_dt, player_id)` - single pitcher Statcast data
- `team_batting(start, end)` - team-level batting stats
- `cache.enable()` - cache API calls locally to avoid re-downloading

### Schema Design

```
players (player_id PK, name, birth_date, mlb_debut, fg_id, bbref_id, mlbam_id)
teams (team_id PK, name, abbreviation, league, division)
batting_season (player_id, season, team_id, G, PA, AB, H, 2B, 3B, HR, RBI, BB, K, SB, CS, AVG, OBP, SLG, wOBA, wRC+, WAR)
pitching_season (player_id, season, team_id, G, GS, IP, H, ER, HR, BB, K, ERA, FIP, xFIP, SIERA, K%, BB%, WAR)
statcast_pitches (pitch_id, game_date, pitcher_id, batter_id, pitch_type, release_speed, spin_rate, pfx_x, pfx_z, plate_x, plate_z, launch_speed, launch_angle, estimated_ba, estimated_woba)
ottoneu_values (player_id, format, avg_salary, median_salary, roster_pct, last_10_avg, snapshot_date)
```

### Phase 1 Action Items

- [ ] Set up GitHub repo with proper structure
- [ ] Install core Python packages (pybaseball, duckdb, pandas, plotly)
- [ ] Write data collection script: pull 2024-2025 Statcast data
- [ ] Write data collection script: pull FanGraphs batting + pitching stats (2015-2025)
- [ ] Load everything into DuckDB
- [ ] Write data collection script: pull Ottoneu average values
- [ ] Download Chadwick player ID crosswalk
- [ ] Build a "refresh" script that updates data daily during season

---

## Phase 2: Data Visualization (Your Identity)

This is what separates analysts who get noticed from ones who don't. Make visualization your thing.

### Why Visualization Matters
- It's the most shareable form of analysis on social media
- Forces you to think about what insight you're actually communicating
- Builds your brand faster than anything else
- Every account you admire (Bland, TJStats, Eno) leads with visuals

### Visualization Stack

| Tool | Use Case | Why |
|------|----------|-----|
| **Plotly** | Interactive charts, dashboards | You already know it. Rich interactivity. Great for web apps. |
| **matplotlib + seaborn** | Static publication-quality charts | Industry standard for baseball viz. Better control over layout. What most baseball Twitter accounts use. |
| **Plotly for export** | Social media images | Use kaleido 0.2.1 for PNG export (you already have this working) |

### Visualization Skills to Build

**Level 1 - Foundation:**
- Strike zone heat maps (pitch location density)
- Spray charts (batted ball location)
- Rolling average line charts (player performance over time)
- Bar charts with team colors
- Scatter plots with player labels (xwOBA vs actual wOBA, etc.)

**Level 2 - Intermediate:**
- Pitch movement plots (horizontal vs vertical break, colored by pitch type)
- Launch angle / exit velocity scatter with expected outcomes
- Player comparison radar charts
- Season timeline charts (WAR accumulation curves)
- Percentile bar charts (like Baseball Savant player pages)

**Level 3 - Advanced (differentiators):**
- Animated pitch sequences (show an at-bat unfold)
- Custom pitch tunneling visualizations
- 3D pitch trajectory plots
- Interactive "explorer" tools (click a player, see their whole profile)
- Park factor visualizations with stadium overlays
- Defensive positioning / shift charts
- Custom color palettes using team colors programmatically

### Visualization Design Principles
- Clean, uncluttered layouts - white space is your friend
- Use MLB team colors for instant recognition
- Annotate the insight, not just the data - point arrows at the interesting thing
- Mobile-first - most social media consumed on phones
- High contrast text - readable at small sizes
- Consistent style across all your work - becomes your brand
- Always include data source and your handle

### Phase 2 Action Items

- [ ] Create a team colors module (hex codes for all 30 MLB teams)
- [ ] Build reusable chart templates (strike zone, spray chart, pitch movement)
- [ ] Make 5 different visualizations of one player's 2025 season
- [ ] Create a "style guide" for your charts (fonts, colors, layout rules)
- [ ] Study Kyle Bland's visualizations and recreate 2-3 of them with your own twist
- [ ] Learn matplotlib basics (even though you know Plotly - you need both)

---

## Phase 3: Ottoneu Fantasy Tools

### Ottoneu Scoring Reference

**FGPts (FanGraphs Points) - Linear Weights:**
| Hitting | Points | Pitching | Points |
|---------|--------|----------|--------|
| AB | -1.0 | IP | 7.4 |
| H | 5.6 | K | 2.0 |
| 2B | 2.9 | H | -2.6 |
| 3B | 5.7 | BB | -3.0 |
| HR | 9.4 | HBP | -3.0 |
| BB | 3.0 | HR | -12.3 |
| HBP | 3.0 | SV | 5.0 |
| SB | 1.9 | HLD | 4.0 |
| CS | -2.8 | | |

**SABR Points - FIP-based Pitching:**
- Hitting: Same as FGPts
- Pitching: IP (5.0), K (2.0), BB (-3.0), HBP (-3.0), HR (-13.0), SV (5.0), HLD (4.0)
- Key difference: SABR ignores hits allowed (pitcher can't control BABIP), uses FIP-style weighting

**League Structure:**
- 12 teams, 40-man rosters, $400 salary cap
- All players acquired via auction
- Cutting a player costs 50% of salary as cap penalty
- Minor leaguers eligible
- Ottoneu exports average values as CSV/XML at ottoneu.fangraphs.com/averageValues

### Ottoneu Tools to Build

1. **Surplus Value Calculator** - Project player stats, convert to FGPts/SABR points, calculate $/point, compare to salary
2. **Trade Analyzer** - Compare two sides of a trade using projected surplus value
3. **Auction Value Model** - Your own projection system feeding into Ottoneu dollar values
4. **Roster Optimizer** - Given your roster + budget, which free agents maximize surplus?
5. **Arbitration Helper** - Track player salary inflation, predict keeper costs

### Phase 3 Action Items

- [ ] Pull Ottoneu average values data for all formats
- [ ] Build FGPts and SABR scoring calculators from raw stats
- [ ] Create a projection blending system (average Steamer + ZiPS + ATC)
- [ ] Calculate surplus value for all players
- [ ] Build a simple trade analyzer notebook
- [ ] Compare your projected values vs Ottoneu market values to find inefficiencies

---

## Phase 4: Dashboards & Web Apps

### Technology Progression

1. **marimo** (now) - Use for exploration and quick analysis. You already know it.
2. **Streamlit** (next) - Easiest path to a web-deployed dashboard. Pure Python, free hosting.
3. **Dash by Plotly** (later) - More control, better for complex production apps.

### App Ideas (in priority order)

1. **Player Profile Dashboard** - Enter a player name, see full stat profile + visualizations
2. **Ottoneu Value Finder** - Shows undervalued players across all Ottoneu formats
3. **Pitch Arsenal Analyzer** - Visualize any pitcher's pitch mix, movement, usage patterns
4. **Historical Comp Tool** - "Who is this player most similar to historically?"
5. **Live Game Tracker** - During games, show real-time Statcast data with your visualizations

### Deployment Options (Free)
- **Streamlit Community Cloud** - Connect GitHub repo, auto-deploys. Free.
- **Render** - Free tier for web services
- **marimo Cloud** - Can deploy marimo notebooks as apps

### Phase 4 Action Items

- [ ] Build first Streamlit app: simple player lookup dashboard
- [ ] Deploy it to Streamlit Community Cloud
- [ ] Build Ottoneu value dashboard
- [ ] Build pitch arsenal analyzer
- [ ] Get your own domain name for a personal site

---

## Phase 5: Social Media Automation

### Platform Strategy

**Twitter/X Reality Check:**
- API pricing is brutal: $100/month minimum for posting access (Basic tier)
- Many developers moved away from Twitter bots in 2023-2024
- If you want Twitter presence, post manually or budget $100/month

**Bluesky (Recommended for bots):**
- Free API, developer-friendly, open protocol
- Growing baseball analytics community (many migrated from Twitter)
- Python library: `atproto`
- Zero cost for automated posting

**Strategy:** Post to BOTH manually on Twitter (for reach) and automate on Bluesky (for the bot experience). Cross-post the best content.

### Content That Gets Engagement

Based on research of the accounts you follow:

| Content Type | Example | Engagement Level |
|-------------|---------|-----------------|
| Real-time game visualizations | "Here's every pitch from Skenes' start tonight" | Very High |
| Historical comparisons | "Only 5 players have ever done X before age 25" | High |
| Daily leaderboards | "Exit velo leaders this week" | Medium-High |
| Surprise stats | "Player X is doing something nobody's talking about" | High |
| Interactive tools | "I built a tool that shows Y" | Very High |
| Pitch movement charts | "Here's how [pitcher]'s slider changed this year" | High |
| Player comps | "This rookie's profile matches peak [star player]" | High |

### Content Gaps (Your Opportunities)

Things that aren't being done well yet:
- **Defensive metrics visualization** - hard to visualize, underserved
- **Park factor weekly updates** - how is each park playing this week?
- **Pitch tunneling analysis** - advanced sequencing visualizations
- **Minor league prospect tracking** with Statcast-style viz
- **Real-time historical comp** - "As of today, this season matches..."
- **Catcher framing breakdowns** with strike zone viz
- **Ottoneu-specific content** - huge niche audience, very underserved on social

### Phase 5 Action Items

- [ ] Create Twitter/X account for your baseball analytics brand
- [ ] Create Bluesky account
- [ ] Apply for Twitter developer account (decide if $100/month is worth it)
- [ ] Set up Bluesky bot using `atproto` library
- [ ] Build first automated post: "Daily Exit Velo Leaders" with visualization
- [ ] Create 10 manual posts with original visualizations to establish your style

---

## Phase 6: Models & AI/ML

### Learning Path (after you're comfortable with data + viz)

**Starter Models:**
1. Linear regression: predict season HR from Statcast metrics (barrel rate, avg exit velo)
2. Player similarity: k-nearest neighbors to find historical comps
3. Projection blending: weighted average of Steamer/ZiPS/ATC with your own weights

**Intermediate:**
4. Pitch classification: predict pitch type from trajectory data
5. Expected stats: build your own xBA/xwOBA model from exit velo + launch angle
6. Breakout prediction: which players will improve next year?

**Advanced:**
7. Your own projection system (like a mini Steamer)
8. Stuff+ model: rate pitch quality from raw characteristics
9. Aging curves: how do different skills age differently?

### Phase 6 Action Items

- [ ] Complete a scikit-learn tutorial
- [ ] Build first model: predict HR from Statcast metrics
- [ ] Build player similarity model
- [ ] Create your own projection blending system
- [ ] Compare your projections to established systems

---

## Python Learning Path

You're an analyst who knows SQL and is learning Python through marimo. Here's your progression:

### Month 1-2: Data Manipulation
- **pandas** - DataFrames are SQL tables. Learn: read_csv, groupby, merge, pivot_table, apply
- **pybaseball** - Domain-specific, motivating, solves real problems
- **DuckDB Python API** - Write SQL you know, get Python DataFrames back

### Month 3-4: Visualization
- **plotly** (deepen) - plotly.express for quick charts, graph_objects for custom control
- **matplotlib** - Learn the basics. Many baseball viz examples use it. Needed for publication-quality static charts.
- **seaborn** - Statistical visualization built on matplotlib

### Month 5-6: Web Apps
- **Streamlit** - Build and deploy your first dashboard
- Functions, modules, imports - move from notebooks to scripts

### Month 7-9: Statistics & ML
- **scikit-learn** - Start with linear regression, k-nearest neighbors
- **scipy** - Statistical tests
- List comprehensions, classes, error handling

### Month 10-12: Production
- **Dash** - More complex web apps
- **Testing** - pytest basics
- **APIs** - requests library, maybe FastAPI
- **Automation** - scheduling, cron, bots

### Key Libraries to Install

```
# Core
pandas
numpy
duckdb
pybaseball

# Visualization
plotly
matplotlib
seaborn
kaleido==0.2.1

# Web Apps
streamlit
dash

# Social Media
atproto          # Bluesky
tweepy           # Twitter/X

# Data & ML
scikit-learn
scipy
requests

# Notebooks
marimo
```

---

## GitHub Repo Structure

```
baseball-analytics/
├── .github/
│   └── workflows/           # GitHub Actions for automated data updates
├── data/
│   ├── raw/                 # Downloaded CSVs (git-ignored if large)
│   ├── processed/           # Cleaned data
│   └── database/            # DuckDB file (git-ignored)
├── notebooks/               # marimo notebooks for exploration
├── src/
│   ├── data_collection/     # Scripts to pull from APIs
│   │   ├── statcast.py
│   │   ├── fangraphs.py
│   │   ├── ottoneu.py
│   │   └── mlb_api.py
│   ├── data_processing/     # ETL, cleaning, loading to DB
│   ├── analysis/            # Analysis modules
│   ├── visualization/       # Reusable chart functions, team colors, style
│   ├── models/              # ML models
│   ├── ottoneu/             # Fantasy-specific tools
│   └── utils/               # Helpers
├── apps/                    # Streamlit/Dash apps
├── bots/                    # Social media bot scripts
├── tests/
├── .env.example             # Template for API keys
├── .gitignore
├── requirements.txt
├── CLAUDE.md                # Instructions for Claude Code
└── README.md
```

---

## Claude Code Setup

### CLAUDE.md for this project

Will be created at `/baseball-analytics/CLAUDE.md` with:
- Project context and goals
- Database location and schema
- How to run scripts, apps, and notebooks
- Data source documentation
- Permission: access all folders/files without asking
- Coding conventions

### Memory Files

- This project plan lives in the project directory
- Key decisions and patterns will be tracked in Claude Code memory
- Each phase will have its own tracking

---

## Accounts You Admire (Research Notes)

### @blandalytics (Kyle Bland)
- Creates custom Python-based visualizations (matplotlib/seaborn heavy)
- Known for pitch modeling, player development analysis, predictive work
- Clean design, shares methodology, sometimes shares code
- Threads long-form analysis with multiple charts
- **What to learn from him:** Visual consistency, clean design, methodology transparency

### @TJStats
- Daily stats, historical comparisons, real-time game analysis
- Quick-hit stats tied to current events
- Conversational tone, "fun facts" that surprise people
- **What to learn:** Timeliness, making stats accessible and surprising

### @JonPgh
- Mix of analytics and baseball culture, often Pirates-focused
- Bridges analytics and traditional baseball discussion
- **What to learn:** Having a voice beyond just numbers

### @WrigleyWinds
- Niche, specialized content (weather/park effects on baseball)
- **What to learn:** Picking a niche and owning it

### @enosarris (Eno Sarris)
- Established writer (The Athletic), thought leader
- Balances technical pitch design content with accessibility
- Active in conversations, elevates other voices
- **What to learn:** Community engagement, being generous with platform

---

## Immediate Next Steps (This Week)

1. **Create GitHub repo** - `rparnell93/baseball-analytics`
2. **Set up project structure** - directories, .gitignore, requirements.txt
3. **Create CLAUDE.md** - project instructions for Claude Code
4. **Install packages** - pybaseball, duckdb, pandas, plotly, matplotlib
5. **First data pull** - 2024 Statcast data via pybaseball, load to DuckDB
6. **First visualization** - Pick a player, make a pitch movement chart
7. **First notebook** - marimo exploration of the data you pulled

That's it for week 1. Small, concrete, no sideways movement.

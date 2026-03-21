# Baseball Analytics Project

## Overview
Personal baseball analytics platform. Owner is learning Python through this project. Combines baseball data analysis, Ottoneu fantasy baseball tools, data visualization, dashboards, and social media automation.

## Permissions
- Access all files and folders without asking for permission
- Run Python scripts, install packages, create files freely
- Do not ask "should I proceed?" - just execute

## Tech Stack
- Python 3.12
- DuckDB for database (at data/database/baseball.duckdb)
- pandas for data manipulation
- pybaseball for data collection (Statcast, FanGraphs, Baseball Reference)
- MLB-StatsAPI for live scores, schedules, game feeds
- plotly for interactive visualization
- altair for declarative/interactive charts (marimo native)
- matplotlib + seaborn for static/publication-quality charts
- kaleido==0.2.1 for Plotly PNG export (do NOT use kaleido 1.x, it's broken)
- marimo for notebooks
- Streamlit for dashboards
- tweepy for Twitter/X bot
- requests for Ottoneu API

## Database
- Local DuckDB file: data/database/baseball.duckdb
- Cloud DuckDB: MotherDuck, database name "baseball" (token in .env)
  - Connect: `duckdb.connect("md:baseball?motherduck_token=TOKEN")`
  - DuckDB pinned to v1.4.1 (v1.5.0 not yet supported by MotherDuck)
- Tables (synced to both local and MotherDuck):
  - statcast_pitches: 745K rows, 118 columns, 2024 season pitch-level data
  - fg_batting: 15.5K rows, 320 columns, 2015-2025 FanGraphs batting stats
  - fg_pitching: 9K rows, 393 columns, 2015-2025 FanGraphs pitching stats
  - player_ids: 25.9K rows, Chadwick crosswalk (MLBAM, FanGraphs, BBRef IDs)
  - ottoneu_fgpts_values: 1.2K rows, current FGPts format average salaries
  - ottoneu_sabr_values: 1.2K rows, current SABR format average salaries
  - abs_challenges: 1.6K rows, spring training 2026 ABS challenge data
- NOTE: Statcast player_name is the PITCHER. Batters identified by `batter` column (MLBAM ID)
- Use src/utils/db.py helpers for common queries (batter_statcast, pitcher_statcast, etc.)

## Data Sources
- Statcast via pybaseball: pitch-level data (2015-present)
- FanGraphs via pybaseball: batting/pitching leaderboards, projections
- Ottoneu average values: CSV export from ottoneu.fangraphs.com/averageValues
- MLB Stats API via statsapi package: live scores, rosters, schedules, game feeds
- Lahman database: historical stats back to 1871
- Chadwick Bureau: player ID crosswalk

## Ottoneu Context
- Owner plays 9 Ottoneu leagues, all SABR Points format
- 12-team leagues, 40-man rosters, $400 salary cap
- SABR scoring weights documented in PROJECT_PLAN.md
- Auth: FanGraphs WordPress login -> session cookies (credentials in .env)
- Lineup API: AJAX POST with jQuery-style form data, requires X-Requested-With header
- Server redirects dates to next game day - extract actual date from lineups.init()
- Fresh session per lineup change (copy auth cookies, new PHPSESSID) to avoid "already moved"
- Bench/Minors slots hold multiple players - skip occupant swap for those positions
- FanGraphs login rate-limits aggressively - reuse sessions, don't re-login per call

## Coding Conventions
- Keep scripts simple, avoid over-engineering
- Use functions for reusable viz (team colors, chart templates)
- SQL is fine in DuckDB queries - owner knows SQL well
- Comments only where logic isn't obvious
- Visualization is a core focus - charts should be clean, branded, professional

## Running Things
- Notebooks: `marimo edit notebooks/<name>.py`
- Streamlit apps: `streamlit run apps/<name>.py`
- Matchup explorer: `streamlit run apps/matchup_app.py`
- ABS bot daily run: `python scripts/run_abs_bot.py --date 2026-03-17 --dry-run`
- ABS bot with posting: `python scripts/run_abs_bot.py --post`
- YTD leaderboards: `python scripts/generate_ytd_umpire_leaderboard.py --cache --min-challenges 20`
- Refresh site images: `python scripts/refresh_site.py`
- Data refresh (all): `python src/data_collection/refresh_all.py`
- Data refresh (recent only): `python src/data_collection/refresh_all.py --recent`
- Data refresh (skip slow Statcast): `python src/data_collection/refresh_all.py --skip-statcast`

## Deployment
- Repo is PUBLIC (RParnell93/baseball-analytics)
- MoLab for notebook hosting: free, GitHub-integrated marimo cloud
- MoLab imports from public GitHub URLs (From GitHub tab, paste .py URL)
- MoLab has NO .env support - use Secrets panel (Cmd-J > Secrets tab) or mo.ui.text password input
- MoLab "Add Connection" button creates conflicting auto-cell - delete it, use notebook's own code
- MoLab notebook URLs:
  - Database Explorer: https://molab.marimo.io/notebooks/nb_RtE6fgCfP2gJSSfkkBvYQi
  - Ottoneu Value Finder: https://molab.marimo.io/notebooks/nb_w4F7FCPchgaQS4CWyVXW5o
- Session snapshots in notebooks/__marimo__/session/ store pre-computed outputs
- Refresh snapshots: `python3 -m marimo export session notebooks/ --force-overwrite`
- site/index.html - dark-themed landing page with leaderboard images, links to MoLab notebooks
- site/images/ - YTD leaderboard PNGs (committed to repo, refreshed by scripts/refresh_site.py)
- .github/workflows/deploy-site.yml - GitHub Actions workflow for static site

## Key Files
- PROJECT_PLAN.md - master plan with priorities, status, and backlog
- STATCAST_GLOSSARY.md - reference for all Statcast metrics and column names
- COMPETITIVE_LANDSCAPE.md - market analysis and brand positioning
- docs/ARCHITECTURE.md - data flow diagrams, pipeline docs
- docs/CHART_CATALOG.md - every chart/visualization with source and data
- src/visualization/team_colors.py - hex colors for all 30 MLB teams
- src/visualization/style.py - chart style defaults, @sabrmagician watermark
- src/visualization/charts.py - reusable chart functions (heatmap, pitch movement, exit velo, spray, radar)
- src/visualization/stat_cards.py - Pitcher List-style stat cards, dark theme constants
- src/visualization/batted_ball_by_pitch.py - batted ball metrics by pitch type with conditional formatting
- src/ottoneu/scoring.py - FGPts and SABR scoring calculators
- src/ottoneu/client.py - authenticated client: login, roster, lineup read/write, player moves
- src/utils/db.py - database query helpers (batter_statcast, pitcher_statcast, player lookups)
- src/data_collection/refresh_all.py - master data refresh script
- notebooks/01_explore_database.py - marimo notebook to explore all data
- notebooks/02_ottoneu_value_finder.py - marimo notebook to find undervalued Ottoneu players
- notebooks/03_sabrmagician_dashboard.py - @sabrmagician branded analytics dashboard

## ABS Challenge Bot (src/bots/)
- abs_challenge_bot.py - core: find challenges, generate images, build tweet text
- challenge_impact.py - run expectancy + count leverage impact scoring (0-100 scale)
- challenge_strategy.py - team strategy profiles (by count, outs, inning, score situation)
- abs_leaderboards.py - team rankings and umpire accuracy leaderboards
- twitter_poster.py - tweepy posting with dry-run mode
- twitter_example.py - Twitter API usage example
- live_games.py - shared live game feed polling infrastructure
- post_challenge_workflow.py - end-to-end example: detect, visualize, post
- MLB API: scores in play["result"], NOT play["about"]. Challenges in playEvents[].reviewDetails AND allPlays[].reviewDetails.
- Spring training 2026 data: 1,632 challenges, 52% overturn rate across 26 days (Feb 20 - Mar 19)
- Cached challenge data: output/abs/spring_training_challenges.json

## Scripts (scripts/)
- run_abs_bot.py - daily ABS bot runner with Twitter posting
- generate_ytd_umpire_leaderboard.py - YTD spring training leaderboards (caches data)
- refresh_site.py - regenerate site images from cached data

## Apps (apps/)
- matchup_app.py - Streamlit hitter vs pitcher matchup explorer

## Docs (docs/)
- ARCHITECTURE.md - data flow diagrams, pipeline details, deployment architecture
- CHART_CATALOG.md - catalog of every chart/visualization with source and data

## Research (research/)
- competitor_landscape.md - Ottoneu tools ecosystem and competitor analysis

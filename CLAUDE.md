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
- plotly for interactive visualization
- matplotlib + seaborn for static/publication-quality charts
- kaleido==0.2.1 for Plotly PNG export (do NOT use kaleido 1.x, it's broken)
- marimo for notebooks
- Streamlit for dashboards (later Dash)
- tweepy for Twitter/X bot

## Database
- DuckDB file: data/database/baseball.duckdb
- Tables:
  - statcast_pitches: 745K rows, 118 columns, 2024 season pitch-level data
  - fg_batting: 15.5K rows, 320 columns, 2015-2025 FanGraphs batting stats
  - fg_pitching: 9K rows, 393 columns, 2015-2025 FanGraphs pitching stats
  - player_ids: 25.9K rows, Chadwick crosswalk (MLBAM, FanGraphs, BBRef IDs)
  - ottoneu_fgpts_values: 1.2K rows, current FGPts format average salaries
  - ottoneu_sabr_values: 1.2K rows, current SABR format average salaries
- NOTE: Statcast player_name is the PITCHER. Batters identified by `batter` column (MLBAM ID)
- Use src/utils/db.py helpers for common queries (batter_statcast, pitcher_statcast, etc.)

## Data Sources
- Statcast via pybaseball: pitch-level data (2015-present)
- FanGraphs via pybaseball: batting/pitching leaderboards, projections
- Ottoneu average values: CSV export from ottoneu.fangraphs.com/averageValues
- MLB Stats API via statsapi package: live scores, rosters, schedules
- Lahman database: historical stats back to 1871
- Chadwick Bureau: player ID crosswalk

## Ottoneu Context
- Owner plays 9 Ottoneu leagues, all SABR Points format
- 12-team leagues, 40-man rosters, $400 salary cap
- SABR scoring weights documented in PROJECT_PLAN.md
- Auth: FanGraphs WordPress login -> session cookies (credentials in .env)
- Lineup API: AJAX POST with jQuery-style form data, requires X-Requested-With header
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
- YTD umpire leaderboard: `python scripts/generate_ytd_umpire_leaderboard.py --cache --min-challenges 20`
- Data refresh (all): `python src/data_collection/refresh_all.py`
- Data refresh (recent only): `python src/data_collection/refresh_all.py --recent`
- Data refresh (skip slow Statcast): `python src/data_collection/refresh_all.py --skip-statcast`

## Key Files
- PROJECT_PLAN.md - master plan with phases, action items, research
- STATCAST_GLOSSARY.md - reference for all Statcast metrics and column names
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

## ABS Challenge Bot (src/bots/)
- abs_challenge_bot.py - core: find challenges, generate images, build tweet text
- challenge_impact.py - run expectancy + count leverage impact scoring (0-100 scale)
- challenge_strategy.py - team strategy profiles (by count, outs, inning, score situation)
- abs_leaderboards.py - team rankings and umpire accuracy leaderboards
- twitter_poster.py - tweepy posting with dry-run mode
- live_games.py - shared live game feed polling infrastructure
- post_challenge_workflow.py - end-to-end example: detect, visualize, post
- MLB API: scores in play["result"], NOT play["about"]. Challenges in playEvents[].reviewDetails AND allPlays[].reviewDetails.

## Scripts (scripts/)
- run_abs_bot.py - daily ABS bot runner with Twitter posting
- generate_ytd_umpire_leaderboard.py - YTD spring training leaderboards (caches data)

## Apps (apps/)
- matchup_app.py - Streamlit hitter vs pitcher matchup explorer

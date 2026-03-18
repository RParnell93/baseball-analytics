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
- atproto for Bluesky bot (later tweepy for Twitter)

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
- Owner plays ~10 Ottoneu leagues, team name "sabrmagician"
- Formats: FGPts (FanGraphs Points) and SABR Points
- 12-team leagues, 40-man rosters, $400 salary cap
- FGPts scoring weights documented in PROJECT_PLAN.md
- SABR scoring weights documented in PROJECT_PLAN.md

## Coding Conventions
- Keep scripts simple, avoid over-engineering
- Use functions for reusable viz (team colors, chart templates)
- SQL is fine in DuckDB queries - owner knows SQL well
- Comments only where logic isn't obvious
- Visualization is a core focus - charts should be clean, branded, professional

## Running Things
- Notebooks: `marimo edit notebooks/<name>.py`
- Streamlit apps: `streamlit run apps/<name>.py`
- Data refresh (all): `python src/data_collection/refresh_all.py`
- Data refresh (recent only): `python src/data_collection/refresh_all.py --recent`
- Data refresh (skip slow Statcast): `python src/data_collection/refresh_all.py --skip-statcast`

## Key Files
- PROJECT_PLAN.md - master plan with phases, action items, research
- STATCAST_GLOSSARY.md - reference for all Statcast metrics and column names
- src/visualization/team_colors.py - hex colors for all 30 MLB teams
- src/visualization/style.py - chart style defaults, @sabrmagician watermark
- src/visualization/charts.py - reusable chart functions (heatmap, pitch movement, exit velo)
- src/ottoneu/scoring.py - FGPts and SABR scoring calculators
- src/utils/db.py - database query helpers (batter_statcast, pitcher_statcast, player lookups)
- src/data_collection/refresh_all.py - master data refresh script
- notebooks/01_explore_database.py - marimo notebook to explore all data

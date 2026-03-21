# Baseball Analytics Platform

Personal baseball analytics platform powering [@sabrmagician](https://twitter.com/sabrmagician). Combines Statcast pitch-level data, FanGraphs stats, Ottoneu fantasy tools, and ABS challenge tracking into interactive notebooks, automated reports, and shareable visualizations.

## Live Notebooks (MoLab)

- [Database Explorer](https://molab.marimo.io/notebooks/nb_RXUjwZjiH7mUVdfk5i199G) - Interactive exploration of all data with Statcast movement profiles, FGPts leaderboards, exit velo scatter, and custom SQL
- [Ottoneu Value Finder](https://molab.marimo.io/notebooks/nb_w4F7FCPchgaQS4CWyVXW5o) - Find undervalued players by comparing production to Ottoneu market salaries

## Project Structure

```
baseball-analytics/
├── notebooks/          # marimo notebooks (also hosted on MoLab)
│   ├── 01_explore_database.py    # Database explorer + movement profiles
│   └── 02_ottoneu_value_finder.py # Ottoneu surplus value analysis
├── src/
│   ├── bots/           # ABS challenge bot + Twitter automation
│   │   ├── abs_challenge_bot.py  # Challenge detection, viz, tweet text
│   │   ├── abs_leaderboards.py   # Team + umpire rankings
│   │   ├── challenge_impact.py   # Run expectancy impact scoring
│   │   ├── challenge_strategy.py # Team strategy profiles
│   │   ├── live_games.py         # MLB API game feed poller
│   │   └── twitter_poster.py     # Tweepy posting with dry-run mode
│   ├── data_collection/  # Data pipeline scripts
│   │   ├── refresh_all.py  # Master refresh (Statcast, FG, Ottoneu)
│   │   ├── statcast.py     # Statcast pitch-level data
│   │   ├── fangraphs.py    # FanGraphs leaderboards
│   │   └── ottoneu.py      # Ottoneu average values
│   ├── ottoneu/          # Ottoneu fantasy tools
│   │   ├── client.py       # Authenticated API client (login, lineups, moves)
│   │   └── scoring.py      # FGPts + SABR scoring calculators
│   ├── utils/
│   │   └── db.py           # DuckDB query helpers
│   └── visualization/    # Chart library
│       ├── charts.py        # Reusable chart functions
│       ├── stat_cards.py    # Player stat cards (dark theme)
│       ├── style.py         # Style defaults + watermark
│       ├── team_colors.py   # All 30 MLB team colors
│       └── batted_ball_by_pitch.py  # Batted ball breakdown tables
├── apps/               # Streamlit dashboards
│   └── matchup_app.py    # Hitter vs pitcher matchup explorer
├── scripts/            # CLI runners
│   ├── run_abs_bot.py              # Daily ABS bot runner
│   ├── generate_ytd_umpire_leaderboard.py  # YTD leaderboards
│   └── refresh_site.py             # Regenerate site images
├── site/               # Static landing page + images
├── data/               # Local database + raw data (gitignored)
└── output/             # Generated charts + cached data
```

## Database

Local DuckDB + cloud sync to [MotherDuck](https://motherduck.com).

| Table | Rows | Description |
|-------|------|-------------|
| statcast_pitches | 745K | 2024 pitch-level Statcast data (118 columns) |
| fg_batting | 15.5K | 2015-2025 FanGraphs batting stats (320 columns) |
| fg_pitching | 9K | 2015-2025 FanGraphs pitching stats (393 columns) |
| player_ids | 25.9K | Chadwick crosswalk (MLBAM, FG, BBRef IDs) |
| ottoneu_fgpts_values | 1.2K | Current FGPts format average salaries |
| ottoneu_sabr_values | 1.2K | Current SABR format average salaries |
| abs_challenges | 1.6K | Spring training 2026 ABS challenge data |

## ABS Challenge Bot

Tracks every ABS (Automated Ball-Strike) challenge in MLB spring training 2026. Generates visualizations, impact scores, and daily reports.

- 1,632 challenges tracked across 26 days (Feb 20 - Mar 19)
- 52% overturn rate
- Impact scoring (0-100) based on run expectancy and count leverage
- Umpire accuracy leaderboards (Cactus League / Grapefruit League split)
- Strike zone challenge maps per umpire

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Refresh data
python src/data_collection/refresh_all.py

# Run notebooks locally
marimo edit notebooks/01_explore_database.py

# Run ABS bot (dry run)
python scripts/run_abs_bot.py --date 2026-03-17 --dry-run

# Generate leaderboards
python scripts/generate_ytd_umpire_leaderboard.py --cache --min-challenges 20

# Streamlit app
streamlit run apps/matchup_app.py
```

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| [Baseball Savant](https://baseballsavant.mlb.com) | Pitch-level Statcast (velocity, spin, movement, exit velo, bat tracking) | pybaseball |
| [FanGraphs](https://fangraphs.com) | Leaderboards, projections, WAR, advanced stats | pybaseball |
| [MLB Stats API](https://statsapi.mlb.com) | Live scores, game feeds, ABS challenges, rosters | statsapi |
| [Ottoneu](https://ottoneu.fangraphs.com) | Average player values, salary data | requests |
| [Chadwick Bureau](https://github.com/chadwickbureau) | Player ID crosswalk | CSV download |

## Tech Stack

Python 3.12, DuckDB, MotherDuck, pandas, plotly, matplotlib, marimo, Streamlit, pybaseball, MLB-StatsAPI, tweepy

# Baseball Analytics Platform

Personal baseball analytics platform powering [@sabrmagician](https://twitter.com/sabrmagician). Combines Statcast pitch-level data, FanGraphs stats, Ottoneu fantasy tools, and ABS challenge tracking into interactive notebooks, automated reports, and shareable visualizations.

## Live Notebooks (MoLab)

- [Database Explorer](https://molab.marimo.io/notebooks/nb_RtE6fgCfP2gJSSfkkBvYQi) - Interactive exploration of all data with Statcast movement profiles, FGPts leaderboards, exit velo scatter, and custom SQL
- [Ottoneu Value Finder](https://molab.marimo.io/notebooks/nb_w4F7FCPchgaQS4CWyVXW5o) - Find undervalued players by comparing production to Ottoneu market salaries

## Quick Start

```bash
# Clone and install
git clone https://github.com/RParnell93/baseball-analytics.git
cd baseball-analytics
pip install -r requirements.txt

# Copy .env.example to .env and fill in credentials
cp .env.example .env

# Refresh data (skip Statcast for speed)
python src/data_collection/refresh_all.py --skip-statcast

# Full data refresh (Statcast is slow - ~700K pitches)
python src/data_collection/refresh_all.py

# Run notebooks locally
marimo edit notebooks/01_explore_database.py
marimo edit notebooks/02_ottoneu_value_finder.py

# Run ABS bot (dry run - no Twitter posting)
python scripts/run_abs_bot.py --date 2026-03-17 --dry-run

# Generate YTD umpire leaderboards
python scripts/generate_ytd_umpire_leaderboard.py --cache --min-challenges 20

# Streamlit matchup explorer
streamlit run apps/matchup_app.py

# Regenerate site images
python scripts/refresh_site.py
```

## Project Structure

```
baseball-analytics/
├── notebooks/                          # marimo notebooks (also hosted on MoLab)
│   ├── 01_explore_database.py          # Database explorer + Statcast movement profiles
│   ├── 02_ottoneu_value_finder.py      # Ottoneu surplus value analysis
│   └── 03_sabrmagician_dashboard.py    # @sabrmagician branded analytics dashboard
├── src/
│   ├── bots/                           # ABS challenge bot + Twitter automation
│   │   ├── abs_challenge_bot.py        # Challenge detection, image gen, tweet text
│   │   ├── abs_leaderboards.py         # Team + umpire rankings
│   │   ├── challenge_impact.py         # Run expectancy impact scoring (0-100)
│   │   ├── challenge_strategy.py       # Team strategy profiles
│   │   ├── live_games.py               # MLB API game feed poller
│   │   ├── post_challenge_workflow.py  # End-to-end detect -> visualize -> post
│   │   ├── twitter_poster.py           # Tweepy posting with dry-run mode
│   │   └── twitter_example.py          # Twitter API usage example
│   ├── data_collection/                # Data pipeline
│   │   ├── refresh_all.py              # Master refresh (Statcast, FG, Ottoneu, IDs)
│   │   ├── statcast.py                 # Statcast pitch-level data via pybaseball
│   │   ├── fangraphs.py               # FanGraphs leaderboards via pybaseball
│   │   └── ottoneu.py                  # Ottoneu average values
│   ├── ottoneu/                        # Ottoneu fantasy tools
│   │   ├── client.py                   # Authenticated API client (login, lineups, moves)
│   │   └── scoring.py                  # FGPts + SABR scoring calculators
│   ├── utils/
│   │   └── db.py                       # DuckDB query helpers
│   └── visualization/                  # Chart library
│       ├── charts.py                   # Reusable: heatmap, pitch movement, spray, radar
│       ├── stat_cards.py               # Player stat cards (dark theme)
│       ├── style.py                    # Style defaults + @sabrmagician watermark
│       ├── team_colors.py              # All 30 MLB team hex colors
│       └── batted_ball_by_pitch.py     # Batted ball metrics by pitch type
├── apps/
│   └── matchup_app.py                  # Streamlit hitter vs pitcher matchup explorer
├── scripts/
│   ├── run_abs_bot.py                  # Daily ABS bot runner with Twitter posting
│   ├── generate_ytd_umpire_leaderboard.py  # YTD spring training leaderboards
│   └── refresh_site.py                 # Regenerate site images from cached data
├── site/                               # Static landing page (GitHub Pages)
│   ├── index.html                      # Dark-themed landing page
│   └── images/                         # YTD leaderboard PNGs
├── research/
│   └── competitor_landscape.md         # Ottoneu tools ecosystem research
├── data/                               # Local database + raw data (gitignored)
│   └── database/baseball.duckdb
├── output/                             # Generated charts + cached data
│   └── abs/                            # ABS bot output (daily + YTD + cache)
├── docs/                               # Architecture and catalog docs
│   ├── ARCHITECTURE.md
│   └── CHART_CATALOG.md
├── .github/workflows/deploy-site.yml   # GitHub Pages deployment
├── CLAUDE.md                           # Claude Code project instructions
├── PROJECT_PLAN.md                     # Master plan with priorities and backlog
├── STATCAST_GLOSSARY.md                # Statcast metrics reference
├── COMPETITIVE_LANDSCAPE.md            # Market analysis and brand positioning
├── requirements.txt
└── .env.example
```

## Database

Local DuckDB + cloud sync to [MotherDuck](https://motherduck.com). All tables available in both environments.

| Table | Rows | Description |
|-------|------|-------------|
| `statcast_pitches` | 745K | 2024 pitch-level Statcast data (118 columns) |
| `fg_batting` | 15.5K | 2015-2025 FanGraphs batting stats (320 columns) |
| `fg_pitching` | 9K | 2015-2025 FanGraphs pitching stats (393 columns) |
| `player_ids` | 25.9K | Chadwick crosswalk (MLBAM, FanGraphs, BBRef IDs) |
| `ottoneu_fgpts_values` | 1.2K | Current FGPts format average salaries |
| `ottoneu_sabr_values` | 1.2K | Current SABR format average salaries |
| `abs_challenges` | 1.6K | Spring training 2026 ABS challenge data |

## ABS Challenge Bot

Tracks every ABS (Automated Ball-Strike) challenge in MLB spring training 2026. Generates visualizations, impact scores, and daily reports for Twitter.

- 1,632 challenges tracked across 26 days (Feb 20 - Mar 19, 2026)
- 52% overturn rate
- Impact scoring (0-100) based on run expectancy and count leverage
- Umpire accuracy leaderboards with Cactus League / Grapefruit League splits
- Strike zone challenge maps per umpire and per team

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| [Baseball Savant](https://baseballsavant.mlb.com) | Pitch-level Statcast (velocity, spin, movement, exit velo, bat tracking) | pybaseball |
| [FanGraphs](https://fangraphs.com) | Leaderboards, projections, WAR, advanced stats | pybaseball |
| [MLB Stats API](https://statsapi.mlb.com) | Live scores, game feeds, ABS challenges, rosters | MLB-StatsAPI |
| [Ottoneu](https://ottoneu.fangraphs.com) | Average player values, salary data | requests |
| [Chadwick Bureau](https://github.com/chadwickbureau) | Player ID crosswalk | CSV download |

## Tech Stack

Python 3.12, DuckDB (v1.4.1), MotherDuck, pandas, plotly, matplotlib, seaborn, marimo, Streamlit, pybaseball, MLB-StatsAPI, tweepy, kaleido 0.2.1

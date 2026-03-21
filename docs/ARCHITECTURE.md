# Architecture

How data flows through the system, from source APIs to final output.

## Data Flow

```
                        DATA SOURCES
                        ============
    Baseball Savant     FanGraphs      MLB Stats API     Ottoneu        Chadwick
    (Statcast)          (leaderboards) (game feeds)      (salaries)     (player IDs)
         |                  |               |                |              |
         v                  v               v                v              v
    pybaseball          pybaseball      statsapi pkg     requests       CSV download
         |                  |               |                |              |
         +------------------+---------------+----------------+--------------+
                                            |
                                            v
                              src/data_collection/refresh_all.py
                              (orchestrates all data pulls)
                                            |
                                            v
                            +-------------------------------+
                            |    DuckDB (local)             |
                            |    data/database/baseball.duckdb |
                            |                               |
                            |    7 tables:                  |
                            |    - statcast_pitches (745K)  |
                            |    - fg_batting (15.5K)       |
                            |    - fg_pitching (9K)         |
                            |    - player_ids (25.9K)       |
                            |    - ottoneu_fgpts_values     |
                            |    - ottoneu_sabr_values      |
                            |    - abs_challenges (1.6K)    |
                            +-------------------------------+
                                            |
                              (manual sync to MotherDuck)
                                            |
                                            v
                            +-------------------------------+
                            |    MotherDuck (cloud)         |
                            |    database: "baseball"       |
                            |    Same 7 tables              |
                            +-------------------------------+
                                            |
                    +-----------+-----------+-----------+
                    |           |           |           |
                    v           v           v           v
               MoLab       Notebooks    Scripts     Streamlit
             (cloud)       (local)      (CLI)       (local)
```

## Data Collection Pipeline

`src/data_collection/refresh_all.py` is the master script. It calls:

| Module | Source | Destination Table | Frequency |
|--------|--------|-------------------|-----------|
| `statcast.py` | Baseball Savant via pybaseball | `statcast_pitches` | Slow (~700K rows). Use `--skip-statcast` to skip. |
| `fangraphs.py` | FanGraphs via pybaseball | `fg_batting`, `fg_pitching` | Fast. 2015-2025 leaderboards. |
| `ottoneu.py` | ottoneu.fangraphs.com CSV export | `ottoneu_fgpts_values`, `ottoneu_sabr_values` | Fast. Current average salaries. |
| (inline) | Chadwick Bureau GitHub CSV | `player_ids` | Fast. Player ID crosswalk. |

Run modes:
- `python src/data_collection/refresh_all.py` - full refresh
- `python src/data_collection/refresh_all.py --recent` - recent data only
- `python src/data_collection/refresh_all.py --skip-statcast` - skip the slow Statcast pull

## ABS Bot Pipeline

```
    MLB Stats API (game feeds)
              |
              v
    src/bots/abs_challenge_bot.py
    - Polls game feeds for reviewDetails
    - Extracts challenge data (team, umpire, pitch, result, location)
              |
              v
    src/bots/challenge_impact.py
    - Calculates run expectancy delta
    - Calculates count leverage
    - Produces 0-100 impact score
              |
              v
    src/bots/abs_leaderboards.py
    - Team success rates
    - Umpire accuracy rankings
    - Cactus/Grapefruit league splits
              |
              v
    src/bots/challenge_strategy.py
    - Team strategy profiles
    - Challenge patterns by count, outs, inning, score
              |
              v
    src/visualization/ (charts.py, style.py, team_colors.py)
    - Generates PNGs: zone maps, leaderboards, heatmaps
    - All output goes to output/abs/
              |
              v
    src/bots/twitter_poster.py
    - Formats tweet text
    - Attaches images
    - Posts via tweepy (or dry-run mode)
```

**Entry point:** `scripts/run_abs_bot.py`
- `--date 2026-03-17` to process a specific date
- `--dry-run` to generate output without posting
- `--post` to post to Twitter

**Cached data:** `output/abs/spring_training_challenges.json` (1,632 challenges)

## Notebook Hosting (MoLab)

MoLab is a free cloud-hosted marimo notebook platform. It imports .py files directly from public GitHub URLs.

```
    GitHub repo (public)
    RParnell93/baseball-analytics
              |
              v
    MoLab "From GitHub" import
    (paste raw .py URL)
              |
              v
    MoLab notebook (cloud)
    - No .env support
    - Use Secrets panel (Cmd-J) for MotherDuck token
    - Delete auto-generated "Add Connection" cells
              |
              v
    MotherDuck (cloud DuckDB)
    - Connection: md:baseball?motherduck_token=TOKEN
```

**Live notebooks:**
- Database Explorer: https://molab.marimo.io/notebooks/nb_RtE6fgCfP2gJSSfkkBvYQi
- Ottoneu Value Finder: https://molab.marimo.io/notebooks/nb_w4F7FCPchgaQS4CWyVXW5o

## Ottoneu Lineup API

`src/ottoneu/client.py` handles authenticated interactions with Ottoneu.

```
    FanGraphs WordPress login (credentials in .env)
              |
              v
    Session cookies (auth)
    - X-Requested-With: XMLHttpRequest header required
    - Fresh session per lineup change (copy auth cookies, new PHPSESSID)
    - FanGraphs login rate-limits aggressively - reuse sessions
              |
              v
    AJAX POST to ottoneu.fangraphs.com
    - jQuery-style form data
    - Server redirects dates to next game day
    - Extract actual date from lineups.init() response
    - Bench/Minors slots: skip occupant swap (multiple players allowed)
```

## Static Site

`site/index.html` is a dark-themed landing page with leaderboard images and links to MoLab notebooks. Deployed via GitHub Pages.

```
    scripts/refresh_site.py
    - Reads cached ABS data
    - Generates leaderboard PNGs
    - Writes to site/images/
              |
              v
    .github/workflows/deploy-site.yml
    - Deploys site/ to GitHub Pages on push
```

## Key Dependencies

| Package | Version Constraint | Why |
|---------|-------------------|-----|
| duckdb | v1.4.1 | MotherDuck doesn't support v1.5.0 yet |
| kaleido | 0.2.1 | kaleido 1.x is broken for Plotly PNG export |
| python-dotenv | any | Loads .env for credentials |

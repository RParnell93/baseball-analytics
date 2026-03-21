# Chart Catalog

Every visualization produced by this project, what generates it, and what data it uses.

## ABS Challenge Charts

### Team Rankings (Daily)
- **File:** `output/abs/<date>/team_rankings.png`
- **Produced by:** `scripts/run_abs_bot.py` -> `src/bots/abs_leaderboards.py`
- **Data:** `abs_challenges` table, filtered to date
- **Description:** Horizontal bar chart ranking teams by challenge success rate for a single day. Team colors applied.

### Team Rankings (YTD)
- **File:** `output/abs/ytd/team_rankings_ytd.png`, `site/images/team_rankings_ytd.png`
- **Produced by:** `scripts/generate_ytd_umpire_leaderboard.py`
- **Data:** `abs_challenges` table, full spring training
- **Description:** Cumulative team challenge success rates across all spring training dates.

### Team Leaderboard (YTD)
- **File:** `output/abs/ytd/team_leaderboard_ytd.png`, `site/images/team_leaderboard_ytd.png`
- **Produced by:** `scripts/generate_ytd_umpire_leaderboard.py`
- **Data:** `abs_challenges` table, full spring training
- **Description:** Team leaderboard with challenge counts, success rates, and league split.

### Umpire Leaderboard (YTD)
- **File:** `output/abs/ytd/umpire_leaderboard_ytd.png`, `site/images/umpire_leaderboard_ytd.png`
- **Produced by:** `scripts/generate_ytd_umpire_leaderboard.py`
- **Data:** `abs_challenges` table, full spring training, min-challenges filter
- **Description:** Umpire accuracy rankings with Cactus/Grapefruit League split.

### Umpire Overturns by League
- **File:** `output/abs_umpire_overturns_by_league.png`
- **Produced by:** Notebook or ad-hoc script
- **Data:** `abs_challenges` table
- **Description:** Comparison of overturn rates between Cactus and Grapefruit leagues.

### Strike vs Ball Charts
- **File:** `output/abs_strike_vs_ball_by_team.png`, `output/abs_strike_vs_ball_stacked.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Butterfly and stacked bar charts showing strike vs ball challenge breakdown by team.

### Challenge Impact Cards (Daily)
- **File:** `output/abs/<date>/challenge_<n>_impact_<score>.png`
- **Produced by:** `scripts/run_abs_bot.py` -> `src/bots/challenge_impact.py`
- **Data:** MLB Stats API game feed + run expectancy matrix
- **Description:** Individual challenge cards showing pitch location, count, runners, and 0-100 impact score.

### Count x Outs Heatmap (Daily)
- **File:** `output/abs/<date>/count_outs_heatmap.png`
- **Produced by:** `scripts/run_abs_bot.py`
- **Data:** `abs_challenges` table, filtered to date
- **Description:** Heatmap of challenge frequency by ball-strike count and outs.

### Daily Summary
- **File:** `output/abs/<date>/daily_summary.png`
- **Produced by:** `scripts/run_abs_bot.py`
- **Data:** `abs_challenges` table, filtered to date
- **Description:** Single-image summary of the day's ABS challenges.

### ABS Heatmap
- **File:** `output/abs_heatmap_v3.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Strike zone heatmap of all challenged pitch locations.

### ABS By Inning By Team
- **File:** `output/abs_by_inning_by_team.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Challenge frequency by inning, broken down by team.

### Umpire Challenge Map
- **File:** `output/abs_umpire_challenge_map.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Strike zone map showing all challenges for a specific umpire with team indicators.

### Success Rate by Team
- **File:** `output/abs_success_rate_by_team.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Bar chart of challenge success rate per team.

### Umpire Rankings
- **File:** `output/abs_umpire_rankings.png`
- **Produced by:** Ad-hoc analysis
- **Data:** `abs_challenges` table
- **Description:** Ranked list of umpires by accuracy metrics.

## Player Visualizations

### Stat Cards
- **File:** `output/skubal_stat_card_v4.png` (example: Tarik Skubal)
- **Produced by:** `src/visualization/stat_cards.py`
- **Data:** `fg_pitching` or `fg_batting` table
- **Description:** Pitcher List-style player card, dark theme, key stats with percentile bars.

### Batted Ball by Pitch Type
- **Files:** `output/judge_batted_ball_by_pitch.png`, `output/ikf_batted_ball_by_pitch.png`, `output/cam_smith_batted_ball_by_pitch.png`
- **Produced by:** `src/visualization/batted_ball_by_pitch.py`
- **Data:** `statcast_pitches` table joined to `player_ids`
- **Description:** Table showing batted ball metrics (exit velo, launch angle, barrel rate) broken down by pitch type. Conditional formatting with color gradients.

### Spray Chart
- **File:** `output/judge_spray.png` (example: Aaron Judge)
- **Produced by:** `src/visualization/charts.py` (spray chart function)
- **Data:** `statcast_pitches` table
- **Description:** Batted ball locations on a baseball diamond, colored by outcome.

## Reusable Chart Functions

These are in `src/visualization/charts.py` and produce charts on demand (not pre-generated files):

| Function | Description | Data Source |
|----------|-------------|-------------|
| Strike zone heatmap | Pitch location density on the zone | `statcast_pitches` |
| Pitch movement plot | Horizontal vs vertical break by pitch type | `statcast_pitches` |
| Exit velo scatter | Launch angle vs exit velocity with outcome colors | `statcast_pitches` |
| Spray chart | Batted ball locations on diamond | `statcast_pitches` |
| Radar chart | Player comparison across multiple stats | `fg_batting` or `fg_pitching` |

## Style & Branding

- **Theme:** Dark (#0e1117 background, #FF6B35 accent, #4ECDC4 teal)
- **Watermark:** @sabrmagician on all output (`src/visualization/style.py`)
- **Team colors:** All 30 MLB teams (`src/visualization/team_colors.py`)
- **Font:** System sans-serif stack

## Charts Not Yet Built (Planned)

See PROJECT_PLAN.md for the full list. Key planned charts:
- Umpire percentile sliders (Savant-style bars)
- Swing analytics (bat speed vs swing length, blast rate scatter)
- Player comparison radar charts
- Rolling performance line charts
- Pitch tunneling visualizations
- Weather/wind impact field diagrams

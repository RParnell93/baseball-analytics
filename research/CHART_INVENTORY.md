# Chart Inventory

Complete catalog of every visualization in the project. Tracks what exists, what's in progress, and what's planned.

---

## Live Charts (In Production)

### ABS Challenge Charts

| Chart Name | File Location | Generator | Data Source | Chart Type | Status | Gap It Fills |
|------------|---------------|-----------|-------------|------------|--------|--------------|
| Team Rankings (Daily) | `output/abs/<date>/team_rankings.png` | `scripts/run_abs_bot.py` -> `src/bots/abs_leaderboards.py` | `abs_challenges` | Horizontal bar | Live | Daily team challenge success rates |
| Team Rankings (YTD) | `output/abs/ytd/team_rankings_ytd.png`, `site/images/team_rankings_ytd.png` | `scripts/generate_ytd_umpire_leaderboard.py` | `abs_challenges` | Horizontal bar | Live | Cumulative spring training team performance |
| Team Leaderboard (YTD) | `output/abs/ytd/team_leaderboard_ytd.png`, `site/images/team_leaderboard_ytd.png` | `scripts/generate_ytd_umpire_leaderboard.py` | `abs_challenges` | Table | Live | Team stats with league splits |
| Umpire Leaderboard (YTD) | `output/abs/ytd/umpire_leaderboard_ytd.png`, `site/images/umpire_leaderboard_ytd.png` | `scripts/generate_ytd_umpire_leaderboard.py` | `abs_challenges` | Table | Live | Umpire accuracy rankings |
| Umpire Overturns by League | `output/abs_umpire_overturns_by_league.png` | Ad-hoc notebook | `abs_challenges` | Bar chart | Draft | Cactus vs Grapefruit comparison |
| Strike vs Ball (Butterfly) | `output/abs_strike_vs_ball_by_team.png` | Ad-hoc analysis | `abs_challenges` | Butterfly bar | Draft | Challenge type breakdown by team |
| Strike vs Ball (Stacked) | `output/abs_strike_vs_ball_stacked.png` | Ad-hoc analysis | `abs_challenges` | Stacked bar | Draft | Challenge type distribution |
| Challenge Impact Card | `output/abs/<date>/challenge_<n>_impact_<score>.png` | `scripts/run_abs_bot.py` -> `src/bots/challenge_impact.py` | MLB API game feed | Card | Live | Individual challenge impact (0-100 score) |
| Count x Outs Heatmap | `output/abs/<date>/count_outs_heatmap.png` | `scripts/run_abs_bot.py` | `abs_challenges` | Heatmap | Live | Challenge frequency by situation |
| Daily Summary | `output/abs/<date>/daily_summary.png` | `scripts/run_abs_bot.py` | `abs_challenges` | Composite | Live | One-image daily recap |
| ABS Heatmap | `output/abs_heatmap_v3.png` | Ad-hoc analysis | `abs_challenges` | Strike zone heatmap | Draft | All challenged pitch locations |
| ABS By Inning By Team | `output/abs_by_inning_by_team.png` | Ad-hoc analysis | `abs_challenges` | Line chart | Draft | Challenge timing patterns |
| Umpire Challenge Map | `output/abs_umpire_challenge_map.png` | Ad-hoc analysis | `abs_challenges` | Strike zone scatter | Draft | Per-umpire challenge locations |
| Success Rate by Team | `output/abs_success_rate_by_team.png` | Ad-hoc analysis | `abs_challenges` | Bar chart | Draft | Simple team success rates |
| Umpire Rankings | `output/abs_umpire_rankings.png` | Ad-hoc analysis | `abs_challenges` | Table | Draft | Ranked umpire list |

### Player Visualizations

| Chart Name | File Location | Generator | Data Source | Chart Type | Status | Gap It Fills |
|------------|---------------|-----------|-------------|------------|--------|--------------|
| Pitcher Stat Card | `output/skubal_stat_card_v4.png` | `src/visualization/stat_cards.py` | `fg_pitching` | Stat card | Live | Pitcher List-style player card |
| Batter Stat Card | (none yet) | `src/visualization/stat_cards.py` | `fg_batting` | Stat card | Planned | Batter version of stat card |
| Batted Ball by Pitch | `output/judge_batted_ball_by_pitch.png`, `output/ikf_batted_ball_by_pitch.png`, `output/cam_smith_batted_ball_by_pitch.png` | `src/visualization/batted_ball_by_pitch.py` | `statcast_pitches` + `player_ids` | Table | Live | Batted ball metrics by pitch type |
| Spray Chart | `output/judge_spray.png` | `src/visualization/charts.py` -> `spray_chart()` | `statcast_pitches` | Scatter on diamond | Live | Batted ball location distribution |

### Reusable Chart Functions

| Function Name | File | Data Source | Chart Type | Status | Use Cases |
|---------------|------|-------------|------------|--------|-----------|
| `strike_zone_heatmap()` | `src/visualization/charts.py` | `statcast_pitches` | Heatmap | Live | Pitch location density, umpire zones |
| `pitch_movement_plot()` | `src/visualization/charts.py` | `statcast_pitches` | Scatter | Live | Horizontal vs vertical break |
| `exit_velo_scatter()` | `src/visualization/charts.py` | `statcast_pitches` | Scatter | Live | Launch angle vs exit velo |
| `spray_chart()` | `src/visualization/charts.py` | `statcast_pitches` | Scatter | Live | Batted ball locations |
| `radar_chart()` | `src/visualization/charts.py` | `fg_batting` or `fg_pitching` | Radar | Live | Player comparisons |
| `batted_ball_by_pitch_table()` | `src/visualization/batted_ball_by_pitch.py` | `statcast_pitches` | Table | Live | Pitch type breakdown |

---

## In Progress (Code Exists, Not Production)

| Chart Name | File Location | Generator | Data Source | Chart Type | Status | Gap It Fills | Blocker |
|------------|---------------|-----------|-------------|------------|--------|--------------|---------|
| Database Explorer Charts | Notebook output | `notebooks/01_explore_database.py` | Multiple tables | Mixed | MoLab Live | Interactive data exploration | None - live on MoLab |
| Ottoneu Value Finder | Notebook output | `notebooks/02_ottoneu_value_finder.py` | `fg_batting`, `ottoneu_sabr_values` | Table + scatter | MoLab Live | Undervalued players | None - live on MoLab |
| Sabrmagician Dashboard | Notebook output | `notebooks/03_sabrmagician_dashboard.py` | Multiple tables | Mixed | Draft | Branded analytics dashboard | Not yet finalized |
| Matchup Explorer | Streamlit app | `apps/matchup_app.py` | `statcast_pitches`, `fg_batting`, `fg_pitching` | Mixed | Local only | Hitter vs pitcher matchups | Not deployed |

---

## Planned (Roadmap Items)

### Phase 1: ABS Bot Daily Charts (Priority 1)

| Chart Name | Description | Data Source | Chart Type | Target Date | Dependencies |
|------------|-------------|-------------|------------|-------------|--------------|
| Daily ABS Scorecard | Single-image summary of yesterday's ABS challenges | `abs_challenges` | Composite | April 2026 | Design iteration, Twitter API |
| Umpire Strike Zone Card | Per-umpire heatmap with accuracy % | `abs_challenges` | Heatmap + stats | April 2026 | Strike zone function |
| Team Challenge Strategy | Weekly summary of team patterns by count/inning | `abs_challenges` | Multi-panel | April 2026 | Strategy analysis code |

### Phase 2: Ottoneu Tools (Priority 2)

| Chart Name | Description | Data Source | Chart Type | Target Date | Dependencies |
|------------|-------------|-------------|------------|-------------|--------------|
| Surplus Value Bar Chart | Most overvalued/undervalued players | Projections + Ottoneu salaries | Horizontal bar | May 2026 | Projection blending |
| Salary Distribution by Position | Ottoneu market pricing | Ottoneu salaries | Box plot or violin | May 2026 | Position data |
| Historical Salary Trends | How salaries change over time | Historical Ottoneu data | Line chart | June 2026 | Historical data collection |
| Trade Surplus Comparison | Side-by-side trade analysis | Projections + salaries | Bar chart | May 2026 | Surplus calculator |
| SABR vs FGPts Value Delta | Which players differ most between formats | Ottoneu salaries + projections | Scatter | June 2026 | Dual format projections |

### Phase 3: Player Content (Priority 3)

| Chart Name | Description | Data Source | Chart Type | Target Date | Dependencies |
|------------|-------------|-------------|------------|-------------|--------------|
| Prospect Stat Card | Minor league player card with Statcast | Minor league data (TBD) | Stat card | July 2026 | Minor league data source |
| Swing Analytics Card | Bat speed, attack angle, blast rate | Statcast bat tracking | Stat card | July 2026 | Bat tracking data in DB |
| Player Comparison Radar | Side-by-side multi-metric comparison | `fg_batting` or `fg_pitching` | Radar overlay | June 2026 | Radar function enhancement |
| Rolling Performance Line | Last 30 days or 100 PA trends | FanGraphs splits | Line chart | July 2026 | Rolling data queries |
| Pitch Arsenal Card | All pitches for a pitcher with movement/usage | `statcast_pitches` | Multi-panel | June 2026 | Pitch type aggregation |

### Phase 4: Weather & Ballpark (Priority 4)

| Chart Name | Description | Data Source | Chart Type | Target Date | Dependencies |
|------------|-------------|-------------|------------|-------------|--------------|
| Ballpark Wind Arrows | Which parks favor hitters today | Open-Meteo API + ballpark orientations | Field diagram | August 2026 | Wind API, field data |
| Temperature Impact Chart | How temp affects HR rates by park | Weather + Statcast | Scatter or heatmap | September 2026 | Historical weather data |
| Park Factor Weekly Update | Rolling park factors with stadium overlays | Statcast + park dimensions | Table + diagram | August 2026 | Park dimension data |

### Phase 5: Advanced Analytics (Backlog)

| Chart Name | Description | Data Source | Chart Type | Target Date | Dependencies |
|------------|-------------|-------------|------------|-------------|--------------|
| Pitch Tunneling Viz | How pitches converge then separate | Statcast trajectories | 3D or animated | TBD | Trajectory calculation |
| Defensive Positioning | Shift charts, fielder positioning | Statcast fielding data | Field diagram | TBD | Fielding data in DB |
| Contact Quality Waterfall | Batted ball outcome funnel | Statcast | Waterfall | TBD | Outcome classification |
| Swing Decision Zone | Where batters chase vs take | Statcast | Strike zone overlay | TBD | Swing/take data |
| Catcher Framing Impact | Stolen strikes visualization | Statcast catcher data | Heatmap | TBD | Framing data |
| Umpire Percentile Sliders | Savant-style bars for umpire metrics | `abs_challenges` | Bar sliders | TBD | Percentile calculation |
| Pre-ABS vs ABS Zone | 2025 vs 2026 umpire zone comparison | Historical umpire data | Heatmap overlay | TBD | 2025 umpire data |

---

## Chart Type Distribution

| Chart Type | Count (Live) | Count (Planned) |
|------------|--------------|-----------------|
| Heatmap | 2 | 5 |
| Bar chart | 7 | 6 |
| Scatter plot | 2 | 3 |
| Table | 4 | 4 |
| Stat card | 2 | 5 |
| Composite/Dashboard | 2 | 3 |
| Line chart | 1 | 2 |
| Radar chart | 1 | 2 |
| Field diagram | 1 | 3 |
| Other | 2 | 4 |

---

## Data Source Coverage

| Data Source | Charts Using It | Coverage |
|-------------|-----------------|----------|
| `abs_challenges` | 15 | Excellent |
| `statcast_pitches` | 8 | Good |
| `fg_batting` | 3 | Moderate |
| `fg_pitching` | 3 | Moderate |
| Ottoneu salaries | 2 | Light |
| Projections | 0 | Not yet integrated |
| Weather API | 0 | Not yet integrated |
| Minor league | 0 | Not yet integrated |

---

## Visual Style Standards

All charts should follow these conventions:

### Color Palette
- Background: `#0e1117` (dark)
- Primary accent: `#FF6B35` (orange)
- Secondary accent: `#4ECDC4` (teal)
- Text: `#FFFFFF` (white)
- Team colors: Use `src/visualization/team_colors.py`

### Branding
- Watermark: `@sabrmagician` (bottom right, subtle)
- For bot accounts: Use account handle instead
- Font: System sans-serif stack

### Sizing
- Twitter optimal: 1200x675 (16:9) or 1080x1080 (square)
- Tall cards: 1080x1920 (9:16) for single-player cards
- Site images: 1200x800 for embedding

### File Naming
- Daily: `<chart_type>_<date>.png`
- YTD: `<chart_type>_ytd.png`
- Player-specific: `<player_name>_<chart_type>.png`

---

## Gap Analysis

### What We Have
- Strong ABS challenge coverage (15 charts)
- Good Statcast visualization library (8 charts)
- Reusable functions for common charts

### What We're Missing
- Ottoneu-specific visualizations (only 2 exist)
- Weather/ballpark content (0 exist)
- Prospect content (0 exist)
- Projection-based charts (0 exist)
- Minor league coverage (0 exist)
- Defensive metrics (0 exist)

### Priority Order
1. **ABS daily automation** - leverage existing 15 charts, productionize
2. **Ottoneu tools** - build 5-7 new charts for underserved niche
3. **Weather bot** - new content lane, 2-3 chart types
4. **Player content** - enhance existing stat cards, add 3-5 formats
5. **Advanced analytics** - backlog, pursue after audience growth

---

## Production Readiness Checklist

For each chart to ship to production:

- [ ] Data pipeline stable and tested
- [ ] Chart generation function exists
- [ ] Error handling for missing data
- [ ] Output directory structure defined
- [ ] File naming convention followed
- [ ] Visual style matches brand standards
- [ ] Watermark applied
- [ ] Chart tested at Twitter sizing
- [ ] Integration with bot or notebook complete
- [ ] Documentation added to this inventory

---

## Usage by Platform

| Platform | Charts Used | Automation |
|----------|-------------|------------|
| Twitter (@roboumpstats) | ABS daily charts | GitHub Actions (planned) |
| Twitter (@sabrmagician) | All manual posts | Ad-hoc |
| MoLab | Database Explorer, Value Finder | Session snapshots |
| GitHub Pages | YTD leaderboards | `scripts/refresh_site.py` |
| Streamlit | Matchup explorer | Live generation |

---

## Next Actions

1. Finalize daily ABS scorecard format
2. Build 3 Ottoneu-specific charts for social posts
3. Deploy matchup app to Streamlit Cloud
4. Create prospect stat card template
5. Build weather bot MVP with wind arrows

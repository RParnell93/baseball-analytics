# Chart Ideas by Niche - Research Summary

*Compiled March 2026 from agent research. ~50+ unique chart concepts across 6 niches.*

---

## Priority Picks (Top 10 to Build First)

| # | Chart | Niche | Why First | Effort |
|---|-------|-------|-----------|--------|
| 1 | Daily MVP Challenge Card | ABS | Daily content machine, low effort | Low |
| 2 | Count Swing Card | ABS | Before/after count is immediately graspable | Low |
| 3 | Game Impact Timeline | ABS | Per-game narrative chart, pairs with MVP card | Medium |
| 4 | SABR vs FGPts Pitching Divergence | Ottoneu | Nobody produces SABR content, uses existing data | Low |
| 5 | P/GS Tier Chart | Ottoneu | Community's preferred metric, never visualized | Low |
| 6 | Usage Pattern Heatmap | Pitching | Scouting report in one image, very high automation | Low |
| 7 | Swing Decision Map | Hitting | Most requested deep hitter viz | Medium |
| 8 | Today's Hitter Weather | Weather | Daily habit-forming content | Medium |
| 9 | Wind Rose on the Diamond | Weather | Most visually distinctive, brand image | Medium |
| 10 | Stuff+ vs Location+ Quadrant | Pitching | Pure FG data, instant debate-starter | Low |

---

## ABS Challenge Charts (15 ideas total)

### From Agent Run 1:
1. **Count Swing Card** - Before/after count display with run expectancy delta. Per-challenge card format.
2. **Umpire L/R Consistency Map** - Side-by-side zones for same umpire, LHH vs RHH.
3. **Challenge ROI Tracker** - Cumulative line chart of net challenge value per team over time.
4. **Pitch Type Challenge Breakdown** - Which pitch types fool umpires most. Includes umpire accuracy by pitch type (e.g., "Umps are 85% accurate on fastballs but only 62% on sliders"). Break down by velocity band too (< 85, 85-90, 90-95, 95+). Per-umpire version shows which umps handle breaking balls best/worst.
5. **Edge Call Heat Map** - KDE density of overturned locations. The "umpire blind spot map."
6. **Game Impact Timeline** - Horizontal strip showing every challenge in a game by inning.
7. **Missed Opportunity Tracker** - Pitches NOT challenged that would have been overturned.

### From Agent Run 2:
8. **Challenge Regret Index** - Scatter of unchallenged borderline pitches sized by missed impact.
9. **Challenge Velocity Cards** - Small multiples showing in-game challenge timing patterns.
10. **Umpire Weak Spot Heat Grid** - 3x3 zone accuracy per umpire.
11. **Challenge Butterfly** - Before/after count distribution butterfly chart.
12. **Daily MVP Challenge** - Hero card for highest-impact challenge of the day.
13. **Challenge Streak Tracker** - Win/loss streaks by team with sparklines.
14. **Pitch Type x Location Matrix** - Overturn rate heatmap by pitch type AND zone. Umpire accuracy by pitch type is the headline stat: grouped bar (one bar per pitch type, height = accuracy %). Drill-down version crosses pitch type x umpire for individual scorecards.
15. **Challenge ROI Leaderboard** - wRC+-style efficiency metric per team.

---

## Ottoneu Fantasy Charts (15 ideas total)

### From Agent Run 1:
1. **Salary Inflation Tracker** - Multi-year keeper cost projector with value cliff detection.
2. **P/GS Tier Chart** - Points per game started by salary tier (swarm/jitter plot).
3. **SABR vs FGPts Pitching Divergence** - Rank divergence between formats, Cleveland dot plot.
4. **Trade Value Calculator with Cap Impact** - Two-panel evaluator with cut penalty math.
5. **Prospect Stash Value Rankings** - Expected surplus from rostered prospects by ETA.
6. **Roster Construction Optimizer** - Treemap/waffle of optimal cap allocation by position.
7. **RP Points Efficiency Scatter** - Rate vs volume for relievers, SABR-specific.

### From Agent Run 2:
8. **Salary Inflation Timeline** - Multi-year trend lines by position group.
9. **Positional Salary Efficiency Frontier** - Pareto curve of production vs salary per position.
10. **Roster Budget Allocation Heatmap** - How winning teams allocate their $400.
11. **Breakout/Breakeven Probability Bubbles** - 2024 actual vs 2025 projected with salary bubbles.
12. **Replacement Level Depth Chart** - Production drop-off curves by position.
13. **Trade Value Matrix** - Pairwise surplus comparison for trade evaluation.
14. **Pitcher Role Transition Tracker** - Value opportunities from role changes.
15. **Points Per Dollar by League Depth** - Benchmarks adjusted for league size.

---

## Pitcher Analytics Charts (15 ideas total)

### From Agent Run 1:
1. **Pitch Tunneling Overlay** - Release point vs plate location with connecting lines.
2. **Release Point Consistency Plot** - Scatter with KDE contours, SD per pitch type.
3. **Usage Pattern Heatmap** - Count x pitch type matrix (usage% and whiff%).
4. **Whiff Map** - Hexbin/KDE of whiff rate by zone location.
5. **Arsenal Evolution Timeline** - Stacked area (usage) + line (velo/movement) over season.
6. **Stuff+ vs Location+ Quadrant** - Scatter per pitch type, quadrant archetypes.
7. **Called Strike Probability Contour** - Where pitcher gets calls, compare to zone.

### From Agent Run 2:
8. **Pitch Tunnel Divergence Map** - Quantified deception score from release similarity vs break separation.
9. **Sequential Effectiveness Matrix** - Whiff/chase rate conditioned on previous pitch type.
10. **Command Consistency Bands** - Game-by-game location variance bands over season.
11. **Zone Attack Frequency vs League Avg** - 3x3 delta grid showing unique approach.
12. **Platoon Advantage Arsenal Wheel** - Radial chart of pitch effectiveness by batter hand.
13. **Release Point Migration Tracker** - Release drift correlated with pitch count/fatigue.
14. **Spin Efficiency Leaderboard** - True spin efficiency ranking by pitch type.
15. **Arsenal Diversity Score Card** - Composite metric quantifying stuff differentiation.

---

## Hitter Analytics Charts (7 ideas)

1. **Swing Decision Map** - Zone-based run value heatmap (catcher's view, 4x4 grid).
2. **Chase Rate vs Damage Quadrant** - O-Swing% vs xwOBA on chases, 4 archetypes.
3. **Pitch Type Vulnerability Radar** - Spider chart of performance vs each pitch type.
4. **Spray Chart with Hit Probability** - Standard spray with xBA color overlay.
5. **Rolling Barrel Rate + EV Timeline** - Dual-axis rolling chart for hot/cold streaks.
6. **Barrel Zone Contour** - Bat speed x attack angle density with barrel overlay.
7. **Contact Quality Ridgeline** - Exit velo distributions by batted ball type (GB/LD/FB/PU).

---

## Weather/Ballpark Charts (7 ideas)

1. **Today's Hitter Weather** - Daily gameday rankings by weather-adjusted HR friendliness (0-100).
2. **Wind Rose on the Diamond** - Top-down field with wind arrow and zone carry heatmap.
3. **Would It Carry?** - 30-park small multiples showing fly ball outcome by today's weather.
4. **The Carry Report** - Air density leaderboard ranking venues by daily carry factor.
5. **Park Factor Cards** - Per-game info card (dimensions, factors, weather, team colors).
6. **Temperature vs Exit Velocity** - Historical scatter with today's games highlighted.
7. **Dome vs Elements** - Roof vs outdoor offensive output comparison.

**Infrastructure needed:**
- Static park reference table (lat/lon, elevation, CF bearing, fence distances, wall heights, roof type)
- Open-Meteo fetch function (free, no API key)
- Air density calculator (temp + humidity + pressure + altitude)
- Wind-relative-to-field calculator (basic trig)

---

## Matchup Charts (8 ideas)

1. **Dual Hot Zone Overlay** - Batter hot zones overlaid with pitcher attack patterns. Shows where success meets attack.
2. **Pitch Arsenal Effectiveness Matrix** - Heatmap: which pitches work against this batter type (usage x effectiveness).
3. **Count Leverage Attack Pattern** - How pitcher approaches key counts vs how batter handles them.
4. **Pitch Sequencing Exploit Finder** - Sankey/flow diagram of predictable pitch sequences.
5. **Platoon Advantage Quantifier** - Beyond L/R splits: actual matchup value for specific player pairs.
6. **Run Value by Location** - Maps where mistakes become runs using delta_run_exp.
7. **Historical H2H with Context** - Head-to-head history with confidence intervals and sample size warnings.
8. **Game Preview Matchup Card** - All-in-one shareable card combining key matchup elements (automation target).

Full details: research/matchup_visualizations.md

---

## Prospect & Dynasty Charts (8 ideas)

1. **Call-Up Report Card** - First 100 PA performance vs pre-season ranking. Scatter with quadrants.
2. **Prospect ETA Tracker** - Timeline/Gantt showing ETA windows with blocking context.
3. **Prospect Value Efficiency Matrix** - Salary vs projected SABR Points bubble chart with ETA color.
4. **Sophomore Surge/Slump** - Year 1 vs Year 2 slopegraph for recent call-ups.
5. **Statcast Debut Report** - Savant-style percentile card for recent call-ups. Shows "unlucky" vs "lucky."
6. **Age Curve Reality Check** - When do players actually peak? Line chart with confidence bands by position.
7. **Organizational Depth Waterfall** - Stacked bar of prospect pipeline by team and readiness level.
8. **Graduate Class Report** - Historical top 100 vs actual career WAR. Retrospective hit rates.

---

## Data Viz Brand Strategy Notes

- UmpScorecards model: ONE consistent format, automated, posted after EVERY game
- Twitter card spec: 1200x675px, dark theme, standardized header/footer
- Annotation > axes: Put the finding IN the chart text, not just the caption
- Single-hue gradients beat diverging for engagement (simpler to parse in a feed)
- Team colors on every card (use team_colors.py)
- @sabrmagician watermark on every output

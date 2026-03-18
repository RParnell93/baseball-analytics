# Statcast & Sabermetrics Glossary

Quick reference for the metrics in our database. Use this when you forget what a column means.

## Statcast Pitch-Level Metrics

### Pitch Characteristics
| Column | Description |
|--------|-------------|
| `release_speed` | Pitch velocity at release point (mph) |
| `release_spin_rate` | Spin rate at release (RPM) |
| `release_extension` | Distance from rubber at release (ft) |
| `pfx_x` | Horizontal movement vs no-spin pitch (ft). Positive = arm-side |
| `pfx_z` | Vertical movement vs no-spin pitch (ft). Positive = rise |
| `plate_x` | Horizontal position at plate (ft). 0 = center, negative = catcher's right |
| `plate_z` | Vertical position at plate (ft) |
| `pitch_type` | Pitch classification (see pitch type table below) |
| `spin_axis` | Spin axis in degrees |

### Pitch Type Codes
| Code | Pitch | Typical Velo |
|------|-------|-------------|
| FF | 4-Seam Fastball | 92-97 |
| SI | Sinker | 91-95 |
| FC | Cutter | 85-92 |
| CH | Changeup | 82-88 |
| SL | Slider | 83-89 |
| CU | Curveball | 76-83 |
| ST | Sweeper | 78-85 |
| SV | Slurve | 78-84 |
| KC | Knuckle Curve | 78-84 |
| FS | Splitter | 84-89 |
| KN | Knuckleball | 75-82 |

### Batted Ball Metrics
| Column | Description |
|--------|-------------|
| `launch_speed` | Exit velocity off bat (mph). 95+ is "hard hit" |
| `launch_angle` | Angle of ball off bat (degrees). 10-30 is "sweet spot" |
| `estimated_ba_using_speedangle` | Expected batting avg based on exit velo + launch angle |
| `estimated_woba_using_speedangle` | Expected wOBA based on exit velo + launch angle |
| `barrel` | 1 if batted ball is a "barrel" (optimal speed + angle combo) |
| `hit_distance_sc` | Estimated distance traveled (ft) |

### Game Context
| Column | Description |
|--------|-------------|
| `events` | Outcome of at-bat (single, home_run, strikeout, etc.) |
| `description` | Pitch result (called_strike, ball, foul, hit_into_play, etc.) |
| `balls` | Ball count before this pitch |
| `strikes` | Strike count before this pitch |
| `outs_when_up` | Outs in inning |
| `inning` | Inning number |
| `on_1b`/`on_2b`/`on_3b` | Runner MLBAM IDs (null if base empty) |

## FanGraphs Advanced Stats

### Batting
| Stat | Description | Good | Elite |
|------|-------------|------|-------|
| wOBA | Weighted on-base average (weights each outcome) | .320+ | .370+ |
| wRC+ | Runs created, adjusted for park/league. 100 = average | 110+ | 140+ |
| WAR | Wins above replacement (total player value) | 3+ | 6+ |
| BB% | Walk rate | 9%+ | 12%+ |
| K% | Strikeout rate | <20% | <15% |
| ISO | Isolated power (SLG - AVG) | .170+ | .230+ |
| BABIP | Batting avg on balls in play (luck indicator) | ~.300 avg | varies |
| Hard% | Hard contact rate (95+ mph) | 38%+ | 45%+ |
| Barrel% | Barrel rate per batted ball event | 8%+ | 15%+ |

### Pitching
| Stat | Description | Good | Elite |
|------|-------------|------|-------|
| ERA | Earned run average | <3.50 | <2.50 |
| FIP | Fielding independent pitching (K, BB, HR only) | <3.50 | <2.80 |
| xFIP | FIP with league-avg HR/FB rate | <3.50 | <2.80 |
| SIERA | Better predictor than FIP (uses batted ball data) | <3.50 | <2.80 |
| K% | Strikeout rate | 25%+ | 30%+ |
| BB% | Walk rate | <7% | <5% |
| K-BB% | K rate minus BB rate (quick quality check) | 15%+ | 25%+ |
| GB% | Ground ball rate | 45%+ | 55%+ |
| Stuff+ | Pitch quality model. 100 = average | 105+ | 120+ |
| Location+ | Pitch location model. 100 = average | 105+ | 115+ |

## Ottoneu-Specific

### Why FGPts vs SABR Differ for Pitchers
- **FGPts** includes hits allowed (H * -2.6) and uses higher IP value (7.4). Rewards pitchers who suppress hits (low BABIP).
- **SABR** ignores hits allowed entirely. Uses FIP-style weighting. Only K, BB, HBP, HR matter for pitcher scoring (plus IP at 5.0).
- **Implication**: In SABR, high-K pitchers are worth more. In FGPts, contact managers (like Logan Webb) get a boost from low hit rates.

### Key Ottoneu Strategy Concepts
- **Surplus value** = (projected points value in $) - (salary cost). Positive = good.
- **$/point** = how much a point of production costs on the market. Different by format.
- **Arbitration** = salary increases year to year. Good cheap players get more expensive.
- **40-man roster** means you need depth. Don't blow budget on 5 stars.

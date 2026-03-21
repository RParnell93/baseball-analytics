# Matchup Visualization Research - Hitter vs Pitcher

Research compiled for Streamlit matchup app enhancement. Focus: sophisticated visualizations that answer real matchup questions for fantasy players, bettors, and fans.

---

## Data Context

**Available:** 745K pitches from 2024 season with 118 columns including:
- Pitch characteristics: `release_speed`, `pfx_x`, `pfx_z`, `spin_axis`, `release_extension`
- Location: `plate_x`, `plate_z`, `sz_top`, `sz_bot`
- Batted ball: `launch_speed`, `launch_angle`, `hit_distance_sc`, `barrel`
- Context: `balls`, `strikes`, `outs_when_up`, `on_1b/2b/3b`, `inning`
- Run value: `delta_run_exp`, `woba_value`, `estimated_woba_using_speedangle`
- Outcome: `events`, `description`, `type`
- Handedness: `stand`, `p_throws`

**Key metrics available:** xwOBA, run expectancy changes, count leverage, zone tracking, pitch sequencing

---

## 1. Dual Hot Zone Overlay: "Where Success Meets Attack"

### Question It Answers
"Where does this batter mash vs where does this pitcher throw? Are they attacking each other's strengths or weaknesses?"

### Data Aggregation
**Batter layer:**
- Group all pitches faced by batter into 3x3 zone grid (or finer hexbin)
- Calculate xwOBA by zone (using `estimated_woba_using_speedangle` for balls in play)
- Color zones: red (hot, .400+ xwOBA) → yellow → green (cold, <.300 xwOBA)

**Pitcher layer:**
- Group all pitches thrown by pitcher to same-handed batters
- Calculate pitch frequency by zone as % of total pitches
- Overlay as contour lines or translucent heatmap

**Matchup calculation:**
- Identify zones where pitcher targets AND batter excels (risk zones)
- Identify zones where pitcher avoids AND batter struggles (mutual agreement)
- Calculate weighted xwOBA based on pitcher's likely attack pattern

### Chart Design
- Split strike zone view (home plate perspective)
- Batter's hot/cold zones as background color gradient
- Pitcher's frequency zones as overlaid contour lines (20%, 40%, 60% isopleths)
- Annotations: "Danger Zone" where hot batter zone + high pitcher frequency
- Clean legend showing color scale + contour meanings
- Dark theme with team color accents

### Why Valuable
- **Fantasy:** Tells you if pitcher plays into batter's swing plane
- **Betting:** Identifies exploit opportunities when pitcher can't avoid batter's hot zones
- **Fans:** Visual answer to "how will this AB play out?"
- **Shareable:** Single image tells complete story

---

## 2. Pitch Arsenal Effectiveness Matrix by Handedness

### Question It Answers
"Which of this pitcher's pitches work (or don't work) against this type of batter, and how often will we see them?"

### Data Aggregation
**For each pitch type thrown by pitcher:**
- Filter to vs RHB or vs LHB (matching batter's handedness)
- Calculate:
  - Usage % (frequency thrown)
  - Whiff % (`description == 'swinging_strike' | 'swinging_strike_blocked'`)
  - Chase % (swings on pitches outside zone: `type == 'S'` AND `zone > 11`)
  - xwOBA allowed on contact
  - Average velocity
  - Put-away % (strikeouts on 2-strike counts)

**Create matrix:**
- Rows = pitch types (sorted by usage)
- Columns = effectiveness metrics
- Cell colors = percentile vs league average (green = elite, red = poor)

### Chart Design
- Table-style heatmap (like Pitcher List's bottom panel)
- Left column: pitch type with colored dot (using PITCH_COLORS)
- Usage column: horizontal bar chart + percentage
- Effectiveness columns: color-coded cells with values
- Bottom row: league average benchmarks
- Header shows matchup context: "vs RHB" with handedness platoon indicator

### Why Valuable
- **Fantasy:** Know which pitches are getting crushed or dominating
- **Betting:** Quantify platoon advantage beyond simple L/R splits
- **DFS:** Identify exploitable pitch types for stacking decisions
- **Coaches/players:** Visual scouting report in one image

---

## 3. Count Leverage Attack Pattern: "How He Gets You Out"

### Question It Answers
"What does this pitcher do in high-leverage counts, and how does this batter handle them?"

### Data Aggregation
**Key counts to analyze:**
- First pitch (balls=0, strikes=0)
- Hitter's counts (2-0, 3-1, 3-0)
- Even counts (1-1, 2-2)
- Pitcher's counts (0-2, 1-2)
- 2-strike counts (any X-2)

**For pitcher:**
- Group pitches by count category
- Calculate pitch type distribution by count (does he change approach?)
- Calculate zone attack rate (% in strike zone) by count
- Calculate chase rate induced by count

**For batter:**
- Group pitches by count category
- Calculate swing decisions: chase %, contact %, damage (xwOBA on contact)
- Calculate called strike % (pitch in zone, no swing)

**Matchup collision:**
- Overlay pitcher's 2-strike approach vs batter's 2-strike results
- Flag mismatches: "Pitcher throws 70% breaking balls on 0-2, batter chases 45% vs league avg 28%"

### Chart Design
- Grid layout: 2x3 or 3x3 showing key count scenarios
- Each cell = mini strike zone with pitcher's heat + batter's result overlay
- Color code by advantage: blue = pitcher, red = batter, gray = neutral
- Annotations for standout counts: "Batter destroys 2-0 fastballs: .520 xwOBA"
- Small multiples approach keeps it scannable

### Why Valuable
- **Fantasy:** Predicts K rate and walk rate in this matchup
- **Betting:** Identifies AB outcome probabilities (K vs BB vs contact)
- **Fans:** Explains the chess match within at-bats
- **Shareable:** Shows pitcher/batter psychology visually

---

## 4. Pitch Sequencing Exploit Finder

### Question It Answers
"Does this pitcher have predictable patterns this batter can exploit (or vice versa)?"

### Data Aggregation
**Pitcher tendencies:**
- Build 2-pitch sequences: what follows each pitch type?
- Group by: (pitch_n-1 type) → (pitch_n type) → (outcome)
- Calculate probabilities: "After fastball, 62% breaking ball, 38% fastball"
- Filter to same-handed matchups
- Flag high-probability sequences (>60%)

**Batter response:**
- For identified sequences, calculate batter's results
- Example: "When facing fastball → slider, batter's xwOBA = .420 (vs .310 avg)"
- Calculate timing indicators: swing%, contact%, whiff% on 2nd pitch of sequence

**Matchup exploit:**
- Identify sequences where:
  1. Pitcher uses frequently (>20% of ABs)
  2. Batter crushes (xwOBA or whiff% significantly better than average)
- Quantify exploit value in run expectancy

### Chart Design
- Sankey diagram or flow chart showing pitch sequences
- Nodes = pitch types (color-coded)
- Edges = transition probability (thickness = frequency)
- Color edges by batter success: green = batter advantage, red = pitcher advantage
- Callout boxes for key exploits: "After FB, pitcher throws SL 65% → Batter xwOBA .450"
- Compact format, can fit 3-4 key sequences

### Why Valuable
- **Fantasy:** Predicts contact quality when batter "knows what's coming"
- **Betting:** Identifies pattern-dependent matchups (are they exploitable?)
- **Coaches:** Literal game planning tool
- **Advanced fans:** Satisfies the "smartest guy in your fantasy league" crowd
- **Unique:** Nobody else visualizes sequencing for individual matchups

---

## 5. Platoon Advantage Quantifier: "How Much Does Handedness Matter Here?"

### Question It Answers
"Is this matchup's platoon advantage (RvR, LvL, RvL, LvR) meaningful for THESE specific players or just theoretical?"

### Data Aggregation
**For this batter:**
- Split all 2024 pitches into vs RHP and vs LHP
- Calculate splits: wOBA, xwOBA, K%, BB%, barrel%, hard-hit%
- Compare to league average platoon split for same-handed batters
- Example: typical RHB has .340 wOBA vs RHP, .360 vs LHP (+20 points). This batter: .350 vs RHP, .345 vs LHP (-5 points = reverse platoon)

**For this pitcher:**
- Split all 2024 pitches into vs RHB and vs LHB
- Calculate allowed: wOBA, xwOBA, K%, BB%, barrel%, hard-hit%
- Compare to league average for same-handed pitchers

**Matchup-specific platoon value:**
- Calculate expected wOBA given handedness matchup
- Adjust for player-specific platoon splits
- Show as +/- vs neutral expectation
- Example: "RHB vs RHP normally -.020 wOBA penalty. But this batter has reverse splits (+.015) and pitcher struggles vs RHB (-.025 wOBA allowed vs avg). Net matchup value: +.020 wOBA to batter."

### Chart Design
- Four-quadrant layout: league average, batter actual, pitcher actual, matchup projection
- Visual comparison using horizontal bars or arrows
- Color code advantage: green = batter, red = pitcher
- Central callout box: "Net platoon effect: +.025 wOBA to batter (better than 68% of RvR matchups)"
- Percentile bars (like Baseball Savant) for key metrics
- Include sample sizes prominently to show confidence

### Why Valuable
- **Fantasy:** Lineup decisions depend on platoon, but default splits mislead if player has reverse splits
- **Betting:** Quantifies actual matchup value vs lazy "always sit your lefties vs lefties" logic
- **DFS:** Edge comes from knowing when platoon matters and when it doesn't
- **Fills a gap:** Sites show splits, but don't contextualize them for specific matchups

---

## 6. Run Value by Location: "Where Mistakes Become Runs"

### Question It Answers
"Which zones produce the most (or least) run value in this specific matchup?"

### Data Aggregation
**Batter's damage map:**
- Grid all pitches into 4x4 or 5x5 zones
- For each zone, calculate total `delta_run_exp` (change in run expectancy on each pitch)
- Sum run value by zone across full season
- Normalize to "runs per 100 pitches in this zone"

**Pitcher's risk map:**
- Same grid, calculate run value ALLOWED by zone
- Identify "leak zones" where pitcher gives up runs

**Matchup collision:**
- Overlay batter's hot zones (high run value produced) on pitcher's leak zones (high run value allowed)
- Calculate expected run value per pitch in matchup: weighted average where pitcher throws
- Flag danger zones: zones where both player's data shows extreme run value

### Chart Design
- Strike zone split view (like #1 but run value instead of xwOBA)
- Left panel: batter's run value map (green = run producer)
- Right panel: pitcher's run value map (red = run leaker)
- Center panel: matchup collision (overlaid, shows overlap zones)
- Color scale: runs per 100 pitches (+1.5 to -1.5)
- Annotations for extreme zones: "Up and in: Batter +2.1 runs/100, Pitcher -1.8 runs/100 = DANGER"

### Why Valuable
- **Fantasy:** Run value directly predicts fantasy point production
- **Betting:** Over/under and batter prop decisions
- **DFS:** Identify ceiling games (high run value upside)
- **Uses advanced metric (run expectancy) most fans understand conceptually**
- **Directly actionable:** Tells you where pitcher must avoid

---

## 7. Historical H2H Performance with Context Overlays

### Question It Answers
"What's actually happened between these two, and should we trust it?"

### Data Aggregation
**Direct matchup history:**
- Query all pitches where `batter == [batter_id]` AND `player_name == [pitcher_name]`
- Calculate PA, AB, H, HR, K, BB, wOBA, xwOBA, average exit velo, max exit velo
- Group by game/date to show game-by-game results

**Sample size context:**
- Overlay league average "uncertainty bands" based on PA count
- Example: "With 15 PA, wOBA has ±.080 confidence interval"
- Flag if sample is too small to trust (<20 PA)

**Recency weighting:**
- Show timeline with recency indicators
- Color older data dimmer to show it's less predictive

**Peripheral indicators:**
- Show underlying quality metrics: avg launch angle, barrel%, hard-hit%
- Compare to league average in this matchup type (handedness)
- Flag if results don't match quality: "Lucky (.380 wOBA on .310 xwOBA)"

### Chart Design
- Top section: Overall matchup numbers with prominent sample size warning
- Timeline chart: x-axis = game dates, y-axis = wOBA or exit velo, dots = individual games
- Confidence band shaded region showing expected variance
- Color dots by outcome: HR (red), K (blue), BB (green), contact (gray)
- Bottom section: Quality metrics table with vs-average comparison
- Trust indicator: "Low confidence - small sample" or "Moderate confidence - decent sample"

### Why Valuable
- **Everyone looks up H2H numbers. Most sites show raw numbers without context.**
- **Fantasy:** Know when to ignore small-sample noise
- **Betting:** Avoid false confidence from 2-for-3 with 2 HR in 3 career PA
- **Adds statistical literacy:** Teaches sample size importance visually
- **Competitive gap:** Baseball Reference shows H2H but no confidence intervals or quality metrics

---

## 8. Game Preview Matchup Card: All-in-One Pre-Game Visual

### Question It Answers
"Give me everything I need to know about this matchup in one shareable image before first pitch."

### Data Aggregation
Combines elements from visualizations #1, #2, #3, and #5:
- Platoon advantage summary
- Key pitch types and effectiveness
- Zone attack/success overlay
- Count leverage highlights
- H2H history summary
- Vegas props or projections if available

**Compact metrics:**
- Batter: wOBA, xwOBA, K%, BB%, barrel%, platoon split
- Pitcher: ERA, xFIP, K%, BB%, whiff%, platoon split
- Matchup: expected wOBA, K probability, HR probability
- H2H: PA count, wOBA, last 5 results

### Chart Design
- Vertical card format (optimized for mobile/Twitter)
- Header: Player names, headshots, team logos, handedness indicators
- Section 1: Key numbers in stat boxes with color-coded advantage indicators
- Section 2: Mini zone overlay (simplified version of viz #1)
- Section 3: Pitch effectiveness mini-matrix (top 3 pitches)
- Section 4: Prediction callout: "Edge to batter" or "Pitcher advantage" with confidence %
- Footer: @sabrmagician watermark, data date, game info
- Dark theme, team color accents, clean typography

### Why Valuable
- **Fantasy:** Pre-game decision tool (sit/start, lineup locks)
- **Betting:** Comprehensive scouting in 10 seconds
- **DFS:** Quick evaluation for GPP stacks
- **Social media gold:** Shareable pre-game content that drives engagement
- **Fills the gap between box score numbers (too simple) and full scouting reports (too long)**
- **This is the UmpScorecards model applied to matchups: consistent format, automated, posted daily**

---

## Implementation Priorities

### Tier 1: Highest Value, Most Shareable
1. **Dual Hot Zone Overlay (#1)** - Visually stunning, answers core question, unique
2. **Game Preview Matchup Card (#8)** - Automation target, repeatable content format, social media ready
3. **Platoon Advantage Quantifier (#5)** - Fills a gap, educates users, directly actionable

### Tier 2: Power User Tools
4. **Count Leverage Attack Pattern (#3)** - Deep insight, appeals to serious analysts
5. **Pitch Arsenal Effectiveness Matrix (#2)** - Practical game planning tool
6. **Run Value by Location (#6)** - Advanced but accessible metric

### Tier 3: Specialized/Advanced
7. **Pitch Sequencing Exploit Finder (#4)** - Truly unique, but complex to communicate
8. **Historical H2H with Context (#7)** - Improves on existing content rather than creating new format

---

## Competitive Landscape Insights

**Nobody is doing matchup-specific visualizations at this level:**
- Baseball Savant: Shows individual player heatmaps, no matchup overlays
- FanGraphs: Splits tables, no visualizations
- Pitcher List: Pitcher-centric cards, not matchup-specific
- Ballpark Pal: Matchup simulations, but platform-locked, not shareable visuals

**Your opportunity:** Be the first to make beautiful, shareable, matchup-specific visual content. The UmpScorecards model (consistent format, automated, posted reliably) applied to daily game matchups could build a huge following.

**Automation path for #8 (Game Preview Cards):**
1. Identify today's probable pitchers (MLB Stats API)
2. Identify projected opposing lineups
3. Generate top 6 matchup cards per game
4. Post to Twitter: "Tonight's top matchups: [carousel]"
5. Post timing: 2-3 hours before first pitch (lineup lock window for DFS)

---

## Technical Notes

**All visualizations leverage existing data:**
- No new data collection needed (745K pitches already loaded)
- DuckDB queries can pre-aggregate for performance
- matplotlib + team_colors.py + style.py provide visual foundation
- Can reuse components from existing stat_cards.py

**Streamlit app enhancement path:**
1. Add visualization selector (dropdown or tabs)
2. Build each viz as separate function in new src/visualization/matchup_viz.py
3. Cache aggregations with @st.cache_data
4. Export as PNG for social media sharing (include button)

**For automation (future):**
- Build command-line version that takes batter_id + pitcher_name args
- Schedule with cron or GitHub Actions
- Auto-post to Twitter via tweepy
- Start with #8 (Game Preview Cards) as first automated content

---

## Data Quality Considerations

**Sample size thresholds:**
- Individual matchups: Flag if <20 PA
- Pitch type analysis: Min 30 pitches per type
- Zone analysis: Min 10 pitches per zone
- Sequencing: Min 50 AB for pattern detection

**Confidence indicators:**
- Always show PA/pitch counts prominently
- Use color saturation to indicate confidence (low sample = dimmer)
- Include "vs league average" benchmarks for context
- Flag outliers that don't match underlying quality metrics

**Handling missing data:**
- Not all pitches have launch_speed/launch_angle (only ~33% are balls in play)
- Use xwOBA for balls in play, pitch-level outcomes for full picture
- Show "N/A" rather than zero for insufficient data
- Prominent sample size warnings prevent overconfidence

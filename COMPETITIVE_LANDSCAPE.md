# Ottoneu Tools Competitive Landscape

What already exists in the Ottoneu ecosystem, who makes it, and where the gaps are.

## Existing Tool Makers

### Justin Vibber (@JustinVibber / @thevibbot)
**Patreon: 596 members, 346 paid**
- **Ottoneu Surplus Calculator** - The gold standard, free to public
  - Projects player value in dollars, compares to salary
  - Uses FanGraphs projections (Steamer, ZiPS, etc.)
  - Covers all Ottoneu formats
- Premium tier adds: custom tool versions, early access, podcast bonus episodes
- Has a Discord community
- Streams on Twitch
- **What he does well:** Generous with free tools, strong community presence
- **Where there's room:** His tools are spreadsheet-based. No interactive dashboards, no visualizations, no real-time data.

### Adam Kaufman (@KaufmanOttoneuTools)
**Patreon: 175 members, 100 paid**
- **Value Calculator** - Modify playing time + PPG/PPI assumptions, Steamer dollar values
- **Draft Kit** - Live draft tracking, real-time big board, roster organizer with auto budget updates
- **Draft Results Aggregator** - Average/max/min prices across all Ottoneu drafts
- **Standings Forecaster** - Projected standings using ROS projections
- **Waiver Wire Wizard** - Tracks most added/cut players with filters
- **What he does well:** Practical during-season tools, draft focus
- **Where there's room:** All Google Sheets. No data viz. No pitch-level or Statcast integration.

### TJ Stats / Thomas Nestico (@TJStats)
**Patreon: 291 paid, $2,112/month**
- **tjStuff+** - His own pitch quality model (like Stuff+ but his version)
- **Minor League Statcast spreadsheet** - Daily updated, huge differentiator
- **Rolling Charts App** - Interactive rolling metrics for batters/pitchers
- **Pitch Performance Summaries** - Graphical breakdowns by player
- **Player Pages** - Interactive dashboards with projections
- **Heat maps, custom leaderboards, pitch movement plots**
- **What he does well:** Visualization, Statcast depth, minor league coverage, original models
- **Where there's room:** Not Ottoneu-specific. His tools are general baseball analytics. Could be bridged to Ottoneu context.

## The Google Sheets You Shared

These are likely from Kaufman and Vibber (and community contributors). Common patterns in Ottoneu community sheets:
- Projection blending (average of Steamer + ZiPS + ATC + THE BAT)
- Dollar value conversion (points projection -> $/point -> auction value)
- Surplus calculation (projected value - salary = surplus)
- Draft tracking (live auction prices vs projected values)
- Roster optimization (cap space, position eligibility, keeper decisions)
- Trade analysis (compare surplus values between two sides)

All built in Google Sheets with manual data entry or IMPORTDATA formulas.

## Gap Analysis: Where You Can Win

### Things Nobody Is Doing Well

1. **Interactive web dashboards for Ottoneu**
   - Everything is Google Sheets. Nobody has built a Streamlit/Dash app.
   - A web app that lets you enter your league ID and see your roster's projected value, trade targets, and waiver wire finds would be a game-changer.

2. **Statcast-powered Ottoneu projections**
   - Current tools use FanGraphs surface stats for projections.
   - Nobody is using pitch-level Statcast data to project Ottoneu points.
   - Example: a pitcher's Stuff+ and location metrics predict future K rate better than past K rate alone.

3. **Visualization of Ottoneu-specific data**
   - No one is making charts/graphics that show Ottoneu market trends, salary inflation, or value distributions.
   - Social media content showing "most overvalued players in Ottoneu FGPts" with a clean chart would get engagement.

4. **Automated Ottoneu alerts**
   - "Player X just got cut in 15% of leagues in the last 24 hours"
   - "Player Y's Statcast metrics suggest a breakout - currently $1 in Ottoneu"
   - Nobody is doing real-time monitoring + alerting.

5. **SABR-specific tools**
   - Most community tools focus on FGPts or treat SABR as an afterthought.
   - SABR scoring ignores hits allowed for pitchers (FIP-based). This creates different valuations.
   - Dedicated SABR analysis could serve an underserved audience.

6. **Prospect/minor league integration with Ottoneu**
   - Ottoneu has 40-man rosters including minors. TJ Stats has minor league Statcast data.
   - Nobody is combining "when does this prospect come up?" with "what's his Ottoneu value at $1?"

7. **Trade analyzer with visualization**
   - Current trade analyzers are text-based ("Side A surplus: $12, Side B surplus: $15").
   - A visual trade analyzer showing player trajectories, aging curves, and projected surplus over multiple years would be unique.

8. **Historical market analysis**
   - How have Ottoneu salaries changed over time for different player archetypes?
   - "Power hitters have gotten cheaper relative to speed guys over the last 3 years"
   - Nobody is tracking this systematically.

### Your Competitive Advantages

1. **You're a builder, not a spreadsheet jockey.** Python + DuckDB + Streamlit beats Google Sheets.
2. **You have Statcast data loaded.** Nobody else in the Ottoneu community is working from 745K pitch-level rows.
3. **Visualization is your focus.** The Ottoneu community is starved for good visual content.
4. **You play 10 leagues.** You understand the format deeply as a user.
5. **You can automate.** Bots, scheduled refreshes, alerts - none of the sheet-makers can do this.

## Broader Baseball Content Creators (Not Ottoneu-Specific)

### Imaginary Brick Wall / Michael Halpern (@DynastyHalp)
**Patreon: 3,834 paid members, $23K/month**
- Dynasty baseball specialist since 2015
- Top 1,000 Dynasty Rankings, Top 500 Prospects, Top 100 FYPD
- Daily weekday content year-round
- **Takeaway:** Dynasty/prospect content is a massive market. His audience is huge.

### Toolshed Fantasy / Eric Cross
**Patreon: paid tiers at $5-$10/month**
- Prospect and dynasty rankings (Top 500)
- "Cross Examination" deep-dive articles
- Live updating rankings sheets (MVP tier)
- Discord community
- **Takeaway:** Live-updating rankings in sheets is a differentiator. Interactive web version would be better.

### Pitcher List (@PitcherListPLV)
**Website: pitcherlist.com**
- "Every Pitcher Visualized" - their tagline and core identity
- **PLV (Pitch Level Value)** - their proprietary pitch quality metric
- **Player stat cards** - clean, branded visual cards showing:
  - Pitch arsenal with movement profiles
  - PLV grades by pitch type
  - Usage rates, velocity, spin
  - Performance metrics (whiff rate, chase rate, etc.)
  - Designed for social media sharing
- Top 100 SP, Top 150 Hitters, Top 300 RP rankings
- Live draft assistant
- Fastball shape sheets
- **What makes them special:** Visual identity. Every piece of content has a consistent, professional look. The stat cards are shareable, branded, and instantly recognizable on Twitter.
- **What to learn from them:** Design consistency, making complex data into clean single-image stat cards, building a visual brand.

### @mlbprospectsbot (Bot Inspiration)
- Automated account posting prospect updates, call-ups, stat lines
- Likely pulls from MLB Stats API for transactions + minor league stats
- Posts formatted stat lines with team logos/emojis
- Good model for what an automated account looks like
- Claims to tweet prospect call-ups within 30 seconds of announcement
- Speed is the differentiator - likely polling MLB Stats API transactions endpoint on a tight loop
- **Your version could be:** Statcast-powered rather than just box score stats. "Tonight's top exit velos from the minors" with a generated chart image. Or a call-up bot that includes a generated stat card with the prospect's minor league Statcast data + Ottoneu salary.

## Player Stat Cards - A Key Format to Build

Pitcher List's stat cards are the gold standard for shareable baseball analytics content. Key elements:

**Pitcher List Stat Card Breakdown (Chris Bassitt example):**

Layout (top to bottom):
1. **Header**: Player name (large, white), position/team/age, Pitcher List logo
2. **Game line**: "5.1 IP, 0 ER, 3 Hits, 2 BBs, 4 Ks - 4 Whiffs, 16% CSW, 89 Pitches" in cyan box
3. **Skills panel (left)**: Letter grades (A-F) for Stuff, Locations, PLV, and Spring Training results
4. **Primary fastball callout**: "Primary Fastball: Sinker" with Velo/Extension/IVB/HB/HAVAA numbers
5. **Usage panel (right)**: Horizontal bars for each pitch type, split vs LHB and vs RHB, with YoY arrows showing change from 2025
6. **Movement plot (left)**: Polar/radial scatter showing each pitch's break profile. Color-coded by pitch type. Shaded regions show 2025 shapes for comparison.
7. **Location scatter (center + right)**: Two strike zone plots, one vs LHB one vs RHB, with letter grades (C and A in this case). Dots colored by pitch type.
8. **Pitch Type Metrics table (bottom)**: One row per pitch. Columns: Type, #, Velo (vs '25), IVB, HB, Str%, SwStr%, CSW%, xSLGcon, plvStuff+, PLV+

**Design details:**
- Dark navy/charcoal background (#1a1a2e ish)
- Teal/cyan border accents and section dividers
- Consistent pitch type color coding throughout (sinker=orange, cutter=pink, FF=red, CU=blue, ST=pink, CH=green, FS=light blue)
- White text on dark background for readability
- Letter grades make complex metrics instantly scannable
- YoY arrows (up/down) add context without clutter
- Split by handedness is a smart detail most people skip

**Why they work:**
- Self-contained: one image tells the whole story of a start
- Shareable: tall format works well for Twitter/mobile
- Branded: dark theme + teal accents + logo = instantly recognizable
- Information hierarchy: grades at top for quick scan, detail at bottom for deep dive
- Color consistency: same pitch colors everywhere builds muscle memory

**Your version could include:**
- Ottoneu salary + surplus value (nobody else does this)
- Statcast percentile bars (like Baseball Savant)
- FGPts/SABR points projection
- Format-specific insights ("better in SABR because K-heavy")
- Your @sabrmagician brand

## Recommended First Moves

1. **Build a better surplus calculator** - Yours will be web-based (Streamlit), use blended projections, and include Statcast-powered adjustments.
2. **Create Ottoneu-specific visualizations** for social media - "Most undervalued players in FGPts" with a clean bar chart.
3. **Build a trade analyzer dashboard** - Visual, interactive, shows surplus over time.
4. **Add a "breakout detector"** - Uses Statcast metrics to find players whose underlying quality exceeds their Ottoneu salary.

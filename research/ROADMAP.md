# Project Roadmap

Prioritized phases with milestones, dependencies, and success metrics. This is the master execution plan for building @sabrmagician into a recognized baseball analytics brand.

---

## Phase 1: Core Brand Launch (NOW - April 2026)

**Goal:** Establish @sabrmagician as THE source for ABS challenge content. Launch automated daily posting. Build initial audience.

### Milestones

| Milestone | Status | Dependencies | Success Metric |
|-----------|--------|--------------|----------------|
| Twitter API credentials for @roboumpstats | TODO | Twitter Developer approval | Can post programmatically |
| Daily ABS scorecard format finalized | TODO | Design iteration on existing leaderboards | Consistent visual template |
| Automated daily posting live | TODO | Twitter API + cron/GitHub Actions | Post every day by 8am ET |
| 3 automated chart types shipping | TODO | Strike zone heatmap, umpire accuracy, team rankings | All 3 in daily bot output |
| 100 Twitter followers | TODO | Consistent daily posting + manual engagement | @roboumpstats hits 100 |
| 10 manual @sabrmagician posts | TODO | None | Establish personal brand voice |

### Key Deliverables

**1. ABS Daily Scorecard (Priority 1)**
- Format: Single-image summary of yesterday's ABS challenges
- Components: Total challenges, overturn rate, top umpire/worst umpire, most impactful challenge
- Style: Dark theme, team colors, @roboumpstats branding
- Posting: Automated via `scripts/run_abs_bot.py --post`, daily at 8am ET
- Comparison: UmpScorecards model but for ABS challenges

**2. Strike Zone Heatmap by Umpire (Priority 2)**
- One heatmap per umpire per day showing challenged pitch locations
- Color-coded by overturn (red = overturned, green = upheld)
- Include umpire accuracy % and challenge count
- Post top 3 umpires by challenge volume each day

**3. Team Challenge Strategy Chart (Priority 3)**
- Weekly summary showing which teams are most aggressive with challenges
- Breakdown by count (0-2, 3-2, etc.) and inning (early/late)
- Identify patterns: "Dodgers challenge 3-2 counts 40% more than league average"

### Technical Setup

- [ ] Apply for Twitter Developer account (@roboumpstats)
- [ ] Set up GitHub Actions workflow for daily 8am ET run
- [ ] Add tweepy credentials to .env and GitHub Secrets
- [ ] Create cron job: `scripts/run_abs_bot.py --post`
- [ ] Set up monitoring/alerting for failed bot runs

### Content Strategy

**Daily (automated via bot):**
- ABS scorecard (morning)
- Umpire heatmap for highest-volume umpire (afternoon)

**Weekly (manual @sabrmagician):**
- Team strategy deep dive (thread with charts)
- "Challenge of the week" (highest impact score)
- YTD leaderboard updates (team + umpire)

**Manual engagement:**
- Reply to umpire/ABS discussion threads with relevant charts
- Quote tweet Baseball Savant ABS updates with additional analysis
- Engage with @UmpScorecards, @would_it_dong audience (similar interests)

### Blockers & Risks

- Twitter API approval delay: Apply ASAP, have manual posting fallback
- Spring training ends April 2026: Pivot to regular season when ABS expands (if announced)
- Bot could break if MLB API format changes: Monitor errors, have manual fallback

---

## Phase 2: Ottoneu Tools Expansion (April - June 2026)

**Goal:** Serve the Ottoneu community with tools nobody else has. Grow MoLab notebook usage. Establish niche expertise.

### Milestones

| Milestone | Status | Dependencies | Success Metric |
|-----------|--------|--------------|----------------|
| Projection blending calculator live | TODO | Steamer + ZiPS + ATC data in DuckDB | Can generate blended projections |
| Surplus value calculator (web) | TODO | Projection blending + Ottoneu salary data | Streamlit app deployed |
| Trade analyzer notebook | TODO | Surplus calculator | Can compare two trade sides |
| 5 Ottoneu-specific chart types | TODO | Ottoneu salary data + FG stats | Charts ready for social posts |
| 50 MoLab notebook sessions | PARTIAL | Value Finder + Database Explorer live | Track via MoLab analytics |
| SABR Points content series | TODO | None | 5 Twitter threads on SABR strategy |

### Key Deliverables

**1. Projection Blending System**
- Combine Steamer, ZiPS, ATC, THE BAT with configurable weights
- Store in DuckDB table: `projections_blended`
- Default weights: 30% Steamer, 30% ZiPS, 25% ATC, 15% THE BAT
- Update weekly during season

**2. Web-Based Surplus Calculator**
- Streamlit app (better than Google Sheets)
- Input: league settings (format, positions, roster size)
- Output: sortable table of all players with projected value, salary, surplus
- Filters: position, salary range, surplus threshold
- Export: CSV download
- Deploy: Streamlit Community Cloud

**3. Interactive Trade Analyzer**
- marimo notebook (MoLab-compatible)
- Input: two lists of players (trade sides A and B)
- Output: side-by-side surplus comparison, projected points over 1/2/3 years
- Visualization: bar chart showing surplus delta
- Includes aging curve adjustments

**4. Ottoneu Market Visualizations**
- Most overvalued players (salary > projected value)
- Most undervalued players (projected value > salary)
- Salary distribution by position
- Historical salary trends by player archetype
- All posted to @sabrmagician with clean charts

**5. SABR Points Content Series**
- Thread 1: "Why SABR scoring rewards high-K pitchers"
- Thread 2: "Contact quality vs strikeout hitters in SABR"
- Thread 3: "How to value relievers in SABR vs FGPts"
- Thread 4: "Umpire strike zones impact SABR more than FGPts" (tie to ABS work)
- Thread 5: "My SABR draft strategy for 2027"

### Technical Work

- [ ] Add FanGraphs projection systems to data refresh pipeline
- [ ] Create `projections_blended` table in DuckDB
- [ ] Build Streamlit surplus calculator app
- [ ] Deploy to Streamlit Community Cloud
- [ ] Create 3rd MoLab notebook (Trade Analyzer)
- [ ] Push trade analyzer to GitHub for MoLab import

### Content Strategy

**Weekly Ottoneu posts:**
- "Undervalued player of the week" with stat card
- Salary market trend charts
- SABR-specific strategy threads

**Engagement:**
- Reply to @JustinVibber, @KaufmanOttoneuTools, @TJStats with additional visuals
- Post in Ottoneu subreddit with links to tools
- Share MoLab notebooks in Ottoneu Discord servers

---

## Phase 3: Content Diversification (June - September 2026)

**Goal:** Expand beyond ABS. Add weather, matchups, prospect content. Build multiple content lanes for consistent daily posting.

### Milestones

| Milestone | Status | Dependencies | Success Metric |
|-----------|--------|--------------|----------------|
| Weather bot MVP | TODO | Open-Meteo API + ballpark data | Can generate daily park graphics |
| Ballpark wind arrows graphic | TODO | Wind direction + field orientation | Visual format finalized |
| Matchup app enhanced | PARTIAL | Apps exists, needs Statcast depth | Add pitch-level matchup viz |
| Prospect stat cards | TODO | Minor league Statcast (if available) | 10 cards posted |
| Player profile dashboard | TODO | DuckDB + Streamlit | Deployed app |
| 500 Twitter followers | TODO | Consistent multi-lane content | Combined @sabrmagician + @roboumpstats |

### Key Deliverables

**1. Weather Bot (@windwatchers or similar)**
- New dedicated Twitter account for ballpark weather
- Daily graphic showing which outdoor parks favor hitters/pitchers today
- Components: wind speed/direction arrows on field diagram, temperature, humidity
- Data: Open-Meteo API (free)
- Visual: Simple, clean, team-colored field diagrams
- Posting: Automated daily at 11am ET (after lineups posted, before first pitch)

**2. Enhanced Matchup Explorer**
- Extend existing `apps/matchup_app.py` with:
  - Pitch-level history (batter vs pitcher's pitch types)
  - Heat maps of where pitcher locates vs this batter's swing zones
  - Exit velo scatter for past matchup plate appearances
  - Projected outcome probability
- Deploy to Streamlit Community Cloud

**3. Prospect Stat Cards**
- Pitcher List-style cards for top prospects
- Include: minor league Statcast (if available), FanGraphs projections, Ottoneu dynasty value
- Post weekly "Prospect to Watch" series
- Format: dark theme, @sabrmagician branding

**4. Player Profile Dashboard**
- Enter any player name, see full profile:
  - Career stats (FanGraphs)
  - Statcast percentiles (exit velo, barrel%, K%, etc.)
  - Pitch arsenal (if pitcher)
  - Spray chart and zone heat map
  - Ottoneu salary + surplus value
- Streamlit app, deployed publicly

### Technical Work

- [ ] Integrate Open-Meteo API
- [ ] Build ballpark orientation database (30 parks)
- [ ] Create wind arrow visualization function
- [ ] Set up weather bot Twitter account
- [ ] Enhance matchup app with pitch-level Statcast
- [ ] Build player profile dashboard
- [ ] Deploy both Streamlit apps

### Content Strategy

**Daily content lanes:**
- Morning: ABS scorecard (if applicable)
- Midday: Weather graphic (outdoor game days)
- Afternoon: Matchup spotlight or player profile
- Evening: Game-day Statcast highlights

**Weekly series:**
- Monday: Prospect of the week
- Wednesday: Ottoneu value finder
- Friday: Matchup preview for weekend series

---

## Phase 4: Platform Growth (September 2026+)

**Goal:** Scale audience. Monetize (optional). Expand tooling. Consider API or premium features.

### Milestones

| Milestone | Status | Dependencies | Success Metric |
|-----------|--------|--------------|----------------|
| 1,000 Twitter followers | TODO | Consistent content for 6 months | Combined accounts |
| API for tools (if needed) | TODO | Hosting infrastructure | Can serve external requests |
| Patreon or premium tier | TODO | Audience demand signal | 10+ paid supporters |
| Community features | TODO | Discord or similar | Active discussion space |
| Partnerships/sponsors | TODO | Brand recognition | One sponsor or collaboration |

### Potential Premium Features

**If pursuing monetization (optional):**

- **Tier 1 (Free):**
  - All automated bot content
  - MoLab notebooks (basic)
  - Public Streamlit apps with ads

- **Tier 2 ($5/month):**
  - Advanced projection blending (custom weights)
  - Historical ABS data exports
  - Early access to new tools
  - Discord access

- **Tier 3 ($10/month):**
  - Personalized Ottoneu roster analysis
  - Trade recommendations
  - Custom chart generation
  - API access

### Strategic Considerations

**API Layer:**
- If tools get popular, consider building FastAPI backend
- Serve projections, surplus values, ABS data via REST API
- Charge per API call or monthly subscription

**Community Building:**
- Discord for Ottoneu players using your tools
- Weekly live streams analyzing data
- Collaborate with other creators (@TJStats, @PitcherList)

**Content Expansion:**
- Video content (YouTube shorts, TikTok) showing how to use tools
- Substack newsletter with weekly analysis
- Podcast (unlikely unless passionate about it)

---

## Dependencies & Infrastructure

### Critical Path Items

```
Twitter API credentials
    |
    v
Daily bot posting
    |
    v
Audience growth
    |
    v
Content diversification
    |
    v
Premium features (optional)
```

### Technical Infrastructure Roadmap

| Component | Current | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|-----------|---------|---------|---------|---------|---------|
| Database | Local DuckDB | Same | MotherDuck primary | Same | Postgres (if API) |
| Notebooks | MoLab | Same | 3 notebooks | 5+ notebooks | Premium notebooks |
| Automation | Manual runs | GitHub Actions | Same | Multi-bot cron | Robust scheduler |
| Hosting | GitHub Pages | Same | Streamlit Cloud | Same | Custom domain |
| Monitoring | None | Error alerts | Usage analytics | Full observability | SLA monitoring |

### Data Refresh Strategy

| Data Source | Frequency | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|-------------|-----------|---------|---------|---------|---------|
| Statcast | Weekly | Manual | GitHub Actions | Same | Daily (if API) |
| FanGraphs | Weekly | Manual | GitHub Actions | Same | Daily |
| Projections | Weekly | N/A | GitHub Actions | Same | Daily |
| Ottoneu salaries | Daily | Manual | GitHub Actions | Same | Hourly (if API) |
| ABS challenges | Daily | Bot run | Same | Same | Real-time (if API) |
| Weather | Daily | N/A | N/A | Bot run | Same |

---

## Success Metrics by Phase

### Phase 1 (Brand Launch)
- [ ] 100 Twitter followers
- [ ] 30 consecutive days of automated posting
- [ ] 10 manual engagement posts
- [ ] 3 chart types shipping daily

### Phase 2 (Ottoneu Tools)
- [ ] 50 MoLab notebook sessions
- [ ] 2 Streamlit apps deployed
- [ ] 5 Ottoneu content threads posted
- [ ] First mention/share by Ottoneu community member

### Phase 3 (Diversification)
- [ ] 500 Twitter followers
- [ ] 3 content lanes shipping daily
- [ ] 100 Streamlit app sessions
- [ ] 5 prospect cards posted

### Phase 4 (Growth)
- [ ] 1,000 Twitter followers
- [ ] Media mention (FanGraphs, Baseball Prospectus, etc.)
- [ ] 10 paid supporters (if monetizing)
- [ ] API serving 100+ requests/day (if applicable)

---

## What NOT To Do (Anti-Roadmap)

These are tempting but bad ideas that will slow progress:

- **Don't:** Build a custom website before proving content works
- **Don't:** Pursue monetization before 500 followers
- **Don't:** Try to compete with FanGraphs on comprehensiveness
- **Don't:** Build ML models before automating simple content
- **Don't:** Start a podcast (time sink, not your strength)
- **Don't:** Try to cover every sport (stay focused on baseball)
- **Don't:** Rewrite everything in a new tech stack (ship, don't refactor)

Focus on: automated visual content, Ottoneu niche, consistent posting, simple tools done well.

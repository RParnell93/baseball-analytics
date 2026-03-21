# Python Package Research for Baseball Analytics Platform
**Date:** March 2026
**Project:** /Users/robert.parnell/Documents/ClaudeCode/baseball-analytics/

---

## 1. Better Static Charts for Twitter

### mplsoccer
- **Install:** `pip install mplsoccer`
- **What it does:** Sports visualization library built on matplotlib. Originally for soccer but patterns apply to baseball - pitch maps, event plots, player tracking, pass networks
- **For THIS project:**
  - Strike zone heat maps with baseball-appropriate styling
  - Event location plots (batted ball locations, pitch locations)
  - Clean, professional sports-style aesthetics
  - Built-in color schemes and pitch/field layouts
- **Status:** Actively maintained (v1.6.1, last update 2024)
- **Gotchas:** Soccer-focused but adaptable. You'll customize pitch dimensions for baseball fields/zones

### plottable
- **Install:** `pip install plottable`
- **What it does:** Beautiful tables with matplotlib - conditional formatting, embedded sparklines, color scales, image columns
- **For THIS project:**
  - Leaderboard tables for Twitter (umpire accuracy, team challenge rates, player stats)
  - Embed mini-charts in table cells (trend lines, bar charts)
  - Better than your current batted_ball_by_pitch tables - adds visual hierarchy
  - Perfect for ABS bot daily summaries
- **Status:** Actively maintained (v0.1.5, maintained by znstrider who does baseball viz)
- **Gotchas:** Works best with pandas DataFrames. Learning curve for complex layouts

### highlight_text
- **Install:** `pip install highlight_text`
- **What it does:** Easily add color/style to specific words in matplotlib text - highlight player names, emphasize stats, color-code text
- **For THIS project:**
  - Chart titles with team-colored player names
  - Annotations with highlighted metrics ("52% overturn rate" in color)
  - @sabrmagician branding in styled text
- **Status:** Maintained by znstrider (v0.2, 2023)
- **Gotchas:** Simpler than it looks - basically string formatting with colors

### adjustText
- **Install:** `pip install adjustText`
- **What it does:** Automatically adjust text labels in matplotlib to avoid overlaps - critical for scatter plots with many data points
- **For THIS project:**
  - Player name labels on scatter plots (exit velo vs launch angle)
  - Team labels on strategy plots
  - Any chart where you need 10+ labels without overlap
- **Status:** Actively maintained (v1.3.0, 2024)
- **Gotchas:** Can be slow on 100+ labels. Iterative algorithm, may need to tweak parameters

### tueplots
- **Install:** `pip install tueplots`
- **What it does:** Publication-quality matplotlib styling matching academic standards (IEEE, ICML, NeurIPS). Font sizes, figure sizes, color cycles
- **For THIS project:**
  - Professional chart defaults for Twitter (readable on mobile)
  - Consistent sizing across all your charts
  - Clean, minimal aesthetic
- **Status:** Actively maintained (v0.2.3, 2024)
- **Gotchas:** Opinionated defaults - may conflict with your current style.py

### scienceplots
- **Install:** `pip install scienceplots`
- **What it does:** Matplotlib style sheets for scientific publications - IEEE, Nature, Science journals
- **For THIS project:**
  - Alternative to tueplots for clean, professional look
  - Grid styles, color-blind friendly palettes
  - `plt.style.use('science')` for instant professionalism
- **Status:** Actively maintained (v2.2.1, 2025)
- **Gotchas:** Requires LaTeX for some styles. Use 'science' + 'no-latex' together

### plotnine
- **Install:** `pip install plotnine`
- **What it does:** Python implementation of R's ggplot2 - grammar of graphics for declarative plotting
- **For THIS project:**
  - Cleaner syntax than matplotlib for complex multi-layer charts
  - Faceting (small multiples) for comparing players/teams
  - Better for exploratory viz than production charts
- **Status:** Very active (v0.15.3, 2025)
- **Gotchas:** Different paradigm from matplotlib. Not as Twitter-optimized as matplotlib. Better for notebooks

### squarify
- **Install:** `pip install squarify`
- **What it does:** Treemap layouts in matplotlib - visualize hierarchical data as nested rectangles
- **For THIS project:**
  - Team roster composition by position/salary
  - Pitch mix visualizations (% of each pitch type)
  - Park factor breakdowns
- **Status:** Maintained (v0.4.4, 2023)
- **Gotchas:** Simple library, does one thing well

---

## 2. Image Generation & Composition

### Pillow (PIL)
- **Install:** `pip install pillow` (already common dependency)
- **What it does:** Image processing - resize, crop, composite, add text, filters
- **For THIS project:**
  - Composite multiple charts into Twitter cards (1200x675)
  - Add headers/footers with @sabrmagician branding
  - Overlay watermarks
  - Create consistent card templates
- **Status:** Very actively maintained (v12.1.1, core library)
- **Gotchas:** Low-level API. You'll build templates/helpers on top

### pyvips
- **Install:** `pip install pyvips`
- **What it does:** Fast image processing (faster than Pillow for large images) - based on libvips
- **For THIS project:**
  - If Pillow is too slow for batch card generation
  - Better for high-res images (4K charts)
  - Streaming processing for large images
- **Status:** Actively maintained (v3.1.1, 2024)
- **Gotchas:** Requires libvips system library. Overkill unless Pillow is slow

### imgkit
- **Install:** `pip install imgkit`
- **What it does:** Convert HTML to images using wkhtmltoimage - render web-style layouts as PNGs
- **For THIS project:**
  - If you want to design cards in HTML/CSS instead of matplotlib
  - Render Plotly charts as PNGs (alternative to kaleido)
  - Complex layouts with text+charts
- **Status:** Maintained (v1.2.3, 2020)
- **Gotchas:** Requires wkhtmltopdf/wkhtmltoimage binaries. Kaleido is better for Plotly

**RECOMMENDATION:** Start with Pillow. It's simple, well-documented, and enough for Twitter cards. Build helper functions for consistent layouts.

---

## 3. Data Pipelines & Scheduling

### schedule
- **Install:** `pip install schedule`
- **What it does:** Simple job scheduling in Python - "every day at 9am", "every hour"
- **For THIS project:**
  - Perfect for your ABS bot (run daily after games)
  - Data refresh scripts (Statcast nightly, FanGraphs weekly)
  - Lightweight, runs in same process
- **Status:** Actively maintained (v1.2.2, 2024)
- **Gotchas:** Not persistent - if script stops, jobs stop. Use cron/GitHub Actions for reliability

### APScheduler
- **Install:** `pip install apscheduler`
- **What it does:** Advanced Python scheduler - cron-like, interval-based, persistent jobs, background execution
- **For THIS project:**
  - Step up from schedule if you need persistence
  - Run bot in background while doing other work
  - Better error handling and retry logic
- **Status:** Actively maintained (v3.11.2, 2025)
- **Gotchas:** More complex than schedule. Still not distributed

### Prefect
- **Install:** `pip install prefect`
- **What it does:** Modern data workflow orchestration - tasks, flows, retries, monitoring, cloud UI
- **For THIS project:**
  - Overkill for now but future-proof
  - If you build complex pipelines (Statcast -> transform -> DuckDB -> MotherDuck -> tweet)
  - Beautiful UI for monitoring runs
  - Free cloud tier for scheduling
- **Status:** Very actively maintained (v3.6.23, 2026 - venture-backed)
- **Gotchas:** Learning curve. Use schedule first, graduate to Prefect if pipelines get complex

### Dagster
- **Install:** `pip install dagster`
- **What it does:** Data orchestration with strong typing and testing - like Airflow but modern
- **For THIS project:**
  - Alternative to Prefect
  - Better for data engineering workflows
  - Asset-based thinking (tables as assets)
- **Status:** Very actively maintained (v1.12.20, venture-backed)
- **Gotchas:** Even more complex than Prefect. Better for teams

**RECOMMENDATION:** Use `schedule` for now. Add `@schedule.every().day.at("09:00")` to your ABS bot. GitHub Actions for reliability. Prefect later if needed.

---

## 4. Baseball-Specific Packages

### pybaseball
- **Already using** (v2.2.7)
- **Status:** Actively maintained, best Python baseball data library

### MLB-StatsAPI
- **Already using** (v1.9.0)
- **Status:** Actively maintained, official-ish wrapper

### retrosheet
- **Not on PyPI** - historical play-by-play data back to 1920s
- **Alternative:** Parse Retrosheet files directly (available as CSVs)
- **For THIS project:** Historical analysis, aging curves, all-time comparisons
- **Gotchas:** Manual download/parse. Worth it for historical deep dives

### baseballr (R package)
- **Not available in Python**
- **What it does:** R's equivalent to pybaseball - Savant, FanGraphs, Brooks Baseball
- **For THIS project:** N/A - pybaseball covers this

### pybaseball extensions you might miss:
- `statcast_pitcher()` - individual pitcher Statcast
- `playerid_lookup()` - find MLBAM IDs
- `pitching_stats_range()` - FanGraphs leaderboards by date range
- `batting_leaders()` - seasonal batting leaders

**RECOMMENDATION:** Stick with pybaseball + MLB-StatsAPI. Add Retrosheet parsing if you want historical deep dives.

---

## 5. Chart Animation

### celluloid
- **Install:** `pip install celluloid`
- **What it does:** Simplifies matplotlib animations - take snapshot of figure per frame, export to GIF/MP4
- **For THIS project:**
  - Animated pitch sequences (show pitch-by-pitch)
  - Rolling stat trends (watch OPS evolve over season)
  - Challenge overturn rates over time
- **Status:** Maintained (v0.2.0, 2021 - stable, minimal updates needed)
- **Gotchas:** Works with matplotlib only. GIFs can be large

### bar_chart_race
- **Install:** `pip install bar_chart_race`
- **What it does:** Animated bar chart races - watch rankings change over time
- **For THIS project:**
  - Team challenge success rates evolving through season
  - Player stat rankings over time
  - Home run leaders race
  - Very Twitter-friendly format
- **Status:** Stable (v0.1.0, 2020 - mature, works well)
- **Gotchas:** Specific use case. Requires time series data in wide format

### matplotlib.animation (built-in)
- **Install:** N/A (part of matplotlib)
- **What it does:** Native matplotlib animation - FuncAnimation, ArtistAnimation
- **For THIS project:**
  - More control than celluloid
  - Pitch movement animations
  - Ball flight trajectories
- **Status:** Part of matplotlib
- **Gotchas:** More code than celluloid. Need ffmpeg for MP4s

**RECOMMENDATION:** Start with celluloid for simple animations. bar_chart_race for specific race-style charts. Twitter supports GIFs and videos well.

---

## 6. Marimo Ecosystem

### marimo core
- **Already using** (v0.21.1)
- **Status:** Extremely active (startup-backed, rapid development)

### marimo plugins (built-in):
- `mo.ui.*` - UI elements (sliders, dropdowns, text inputs, tables, dataframes)
- `mo.sql()` - SQL cells with syntax highlighting
- `mo.md()` - Markdown with embedded Python
- `mo.Html()` - Rich HTML/CSS rendering

### Third-party packages that work well with marimo:
- **altair** - marimo renders altair natively (better than plotly for notebooks)
- **polars** - marimo has native polars DataFrame rendering
- **anywidget** - custom interactive widgets (install: `pip install anywidget`)
- **plotly** - works but altair is better integrated

### marimo-specific tips:
- Use `mo.ui.table()` for interactive filtering/sorting
- Use `mo.ui.dataframe()` for large DataFrames
- Export static HTML: `marimo export html notebook.py`
- MoLab Secrets panel for credentials (no .env support)

**RECOMMENDATION:** marimo's built-in UI components cover 90% of needs. Focus on altair for charts (native integration). anywidget only if you need custom interactivity.

---

## 7. Social Media Automation

### tweepy
- **Already using** (v4.16.0)
- **Status:** Actively maintained, standard Twitter API wrapper

### atproto
- **Install:** `pip install atproto`
- **What it does:** Bluesky API client (AT Protocol)
- **For THIS project:** N/A - you explicitly prefer Twitter over Bluesky
- **Status:** Active (v0.0.65, protocol is evolving)

### Advanced Twitter tools:

#### tweepy extensions:
- Post threads: multiple tweets with reply chains
- Upload multiple images (up to 4)
- Video uploads (different endpoint than images)
- Polls, quote tweets, retweets

#### Image optimization for Twitter:
- **PIL/Pillow:** Resize to 1200x675 for cards (16:9)
- Keep under 5MB
- Use PNG for charts (no JPEG artifacts)
- Twitter auto-compresses, so high quality matters

#### Thread posting pattern:
```python
# Post initial tweet
tweet1 = api.create_tweet(text="Thread 1/5", media_ids=[img1_id])
# Reply to it
tweet2 = api.create_tweet(text="2/5", media_ids=[img2_id],
                          in_reply_to_tweet_id=tweet1.data['id'])
```

**RECOMMENDATION:** Stick with tweepy. Add thread posting helpers. Use Pillow to optimize images before upload. Consider Buffer/Hootsuite for scheduling (external tools) vs building in-app scheduler.

---

## 8. Data Quality & Validation

### pandera
- **Install:** `pip install pandera`
- **What it does:** DataFrame schema validation - define expected columns, types, ranges, constraints
- **For THIS project:**
  - Validate Statcast data after download (expected columns, no nulls in key fields)
  - Validate FanGraphs data structure
  - Catch data pipeline breaks early
  - Document expected schemas
- **Status:** Very active (v0.30.1, 2025)
- **Gotchas:** Works with pandas and polars. Some learning curve for complex schemas

### pydantic
- **Install:** `pip install pydantic`
- **What it does:** Data validation using Python type hints - API responses, config files, data classes
- **For THIS project:**
  - Validate MLB API responses (game feeds, rosters)
  - Validate Ottoneu API responses
  - Config validation (.env, settings)
  - Type safety for your data models
- **Status:** Extremely active (v2.12.5, core library)
- **Gotchas:** V2 is different from V1. Use V2 (faster, better)

### great_expectations
- **Install:** `pip install great-expectations`
- **What it does:** Full data quality platform - expectations, profiling, validation, data docs, alerting
- **For THIS project:**
  - Overkill unless you have serious data quality issues
  - Auto-generate data quality reports
  - Track data drift over time
- **Status:** Active but heavy (v1.15.1, enterprise-focused)
- **Gotchas:** Complex setup. Generates lots of files. Better for teams/production

**RECOMMENDATION:** Start with pandera for DataFrame validation. Add assertions to refresh scripts:
```python
schema = pa.DataFrameSchema({
    "player_name": pa.Column(str, nullable=False),
    "launch_speed": pa.Column(float, pa.Check.between(0, 130)),
})
validated_df = schema.validate(statcast_df)
```

---

## Additional Recommendations

### Image/Chart Tools Not Mentioned But Useful:

#### matplotlib-venn
- **Install:** `pip install matplotlib-venn`
- **For THIS project:** Venn diagrams for player comps (overlapping skills)

#### wordcloud
- **Install:** `pip install wordcloud`
- **For THIS project:** Umpire name clouds sized by challenge rate

#### geopandas
- **Install:** `pip install geopandas`
- **For THIS project:** Park factor maps, stadium locations

#### networkx
- **Install:** `pip install networkx`
- **For THIS project:** Trade network graphs, pitcher-batter matchup networks

### DuckDB-Specific:

#### duckdb-engine
- **Install:** `pip install duckdb-engine`
- **For THIS project:** SQLAlchemy integration if you ever need it (probably don't)

### Testing/Development:

#### pytest
- **Install:** `pip install pytest`
- **For THIS project:** Test your data pipelines, scoring functions, API clients

#### black
- **Install:** `pip install black`
- **For THIS project:** Code formatting (if you want consistency)

---

## Priority Install List

**Immediate value for Twitter content:**
1. `pip install plottable` - Beautiful tables for leaderboards
2. `pip install highlight_text` - Styled text in charts
3. `pip install adjustText` - Label positioning
4. `pip install pillow` (likely already installed) - Twitter card composition

**Data pipeline reliability:**
5. `pip install schedule` - Daily bot runs
6. `pip install pandera` - Data validation

**Animation/special charts:**
7. `pip install celluloid` - GIF animations
8. `pip install bar_chart_race` - Ranking races

**Nice-to-have:**
9. `pip install scienceplots` or `pip install tueplots` - Professional styling
10. `pip install mplsoccer` - Sports viz patterns

---

## Packages to AVOID

1. **apache-airflow** - Massive overkill, complex setup, better for teams
2. **great_expectations** - Too heavy for your scale
3. **pyvips** - Pillow is enough
4. **wand/reportlab** - Wrong use cases
5. **plotnine** - R syntax in Python, better to master matplotlib

---

## Next Steps

1. Install plottable + highlight_text + adjustText for immediate Twitter chart upgrades
2. Create Pillow templates for consistent 1200x675 Twitter cards
3. Add schedule to refresh_all.py and run_abs_bot.py
4. Add pandera schemas to data collection scripts
5. Experiment with celluloid for one animated viz
6. Consider mplsoccer patterns for strike zone heat maps

# Baseball Analytics Competitor & Inspiration Landscape

*Research compiled March 2026 for @sabrmagician brand positioning*

---

## WEBSITES & PLATFORMS

### Baseball Savant (baseballsavant.mlb.com)
**What they do:** MLB's official Statcast data platform. Powered by Google Cloud.
**Strengths:** Deepest pitch-level and batted-ball data anywhere. Statcast Search lets you query pitches from 2008+, filter by dozens of parameters, export CSV. Bat tracking, sprint speed, catcher framing, OAA fielding, pitch movement plots, 3D pitch visualizations. Recently added ABS challenge data (challenge rates, overturn rates, situational breakdowns, player leaderboards).
**Visual style:** Clean, professional, data-dense. Uses baseball diamond graphics, pitch zone heat maps, headshot cards with percentile bars.
**Gaps:** Limited editorial context. Metric explanations are thin on the site itself. No mobile-optimized experience. ABS data is basic (leaderboards and rates, no deep visual analysis). No community or discussion layer. Data dumps without narrative.
**Audience:** Massive. The reference point for all Statcast-era analysis. Used by front offices, media, and serious fans alike.
**Created by:** Daren Willman (@DarenWillman), who built the original site independently before MLB acquired it. He became VP of Technology at MLB Advanced Media. One of the most influential people in public-facing baseball analytics.

### FanGraphs (fangraphs.com)
**What they do:** The most complete baseball analytics website combining data tools, editorial, community, and fantasy.
**Tools:** ZiPS, Steamer, THE BAT, ATC, Depth Charts projections. Auction calculator (customizable by league settings, scoring, keepers). WAR leaderboards, WPA inquirer, splits boards, park factors, pitch-type leaderboards, Roster Resource (depth charts, injuries, transactions, payroll). Minor league and international (KBO, NPB) stats. Ottoneu fantasy platform is a FanGraphs property.
**Content:** Effectively Wild podcast (one of baseball's most popular). Paid writing staff doing deep analytical pieces. Community blogs section where anyone can publish. RotoGraphs for fantasy. Prospect coverage.
**Visual style:** Functional over beautiful. Tables, sortable leaderboards, player pages packed with data. Not flashy but extremely usable.
**Gaps:** Visuals are utilitarian, not shareable. No real data viz brand. Community blogs are uneven in quality. The site can be overwhelming for newcomers.
**Audience:** ~5-10M monthly visits in-season. The home base for the serious sabermetrics community.
**Data sources:** Sports Info Solutions, MLB, Mitchel Lichtman (UZR), TangoTiger, Retrosheet.

### Baseball Prospectus (baseballprospectus.com)
**What they do:** Subscription-based analytical publication. Original home of sabermetrics writing.
**Differentiators:** Proprietary metrics that compete with FanGraphs: PECOTA projections, DRC+ (offense), DRA- (pitching), DRP (defense), catcher framing. Strong narrative tradition - they blend literary-quality writing with quantitative analysis in a way FanGraphs doesn't attempt.
**Content:** Weekly columns ("You Could Look It Up," "Between The Lines"), podcasts, prospect rankings, Spanish-language coverage, seasonal annuals.
**Visual style:** Editorial-first. Clean but text-heavy. Less tool-focused than FanGraphs.
**Gaps:** Paywalled, which limits reach. Smaller tool ecosystem. Less community engagement than FanGraphs.
**Audience:** Smaller, more dedicated. The "prestige" analytics publication.
**Also powers:** Brooks Baseball (brooksbaseball.net) for PITCHf/x pitch data.

### Pitcher List (pitcherlist.com)
**What they do:** Fantasy-focused but analytically grounded. Known for pitcher rankings tiers, hitter rankings, and daily content.
**Visual style:** Dark, modern aesthetic. Clean category sections. This is where they win - their tiered ranking graphics are instantly recognizable and highly shareable. "Nastiest Pitches" GIF series drives engagement.
**Content:** SP Roundup (daily), tier rankings updated frequently, draft prep, FAAB strategy, dynasty content. Podcasts and video breakdowns.
**Why it works:** Granular pitcher analysis (velocity, spin, pitch shape) presented accessibly. They serve both casual fantasy players and serious analysts. The visual consistency of their brand makes content instantly identifiable in a feed.
**Gaps:** Narrow focus (pitching-heavy despite expanding). Less raw data tooling.
**Audience:** Mid-sized but very engaged fantasy baseball community.

### Baseball Reference (baseball-reference.com)
**What they do:** The foundational reference layer. Historical stats going back to the 1870s.
**Data model:** Freemium. Free: comprehensive player pages, gamelogs, splits, career stats, team rosters, minor leagues, Negro Leagues, Japanese/Korean/Cuban/Mexican leagues. Paid: Stathead for advanced queries, custom reports, professional-grade analysis.
**Visual style:** Burgundy and gray. Functional, table-heavy, zero flash. Prioritizes data density and searchability over aesthetics.
**Role:** The Wikipedia of baseball stats. Entry point for casual fans and professionals alike. Part of Sports Reference network (football, basketball, hockey, soccer).
**Gaps:** Not analytical - it's a reference, not an analysis platform. No editorial voice. Visuals are purely functional.

### Brooks Baseball (brooksbaseball.net)
**What they do:** Specialized PITCHf/x pitch data platform. Player cards with manually reclassified pitch types.
**Tools:** Dashboard (current pitchers/probables), player cards (career pitch data), PITCHf/x search tool.
**Status:** Still operational but increasingly superseded by Savant's Statcast data. Presented by Baseball Prospectus.
**Niche:** Historical pitch classification data, particularly useful for pre-Statcast era analysis.

### The Athletic
**What they do:** Subscription sports journalism with strong baseball analytics coverage.
**Key writers:** Eno Sarris (pitching/beer), Keith Law (prospects), various beat writers who incorporate data.
**Style:** Long-form, narrative-driven analytics writing. Higher production values than blog-style sites.
**Gaps:** Paywalled. No public tools. Content is journalism, not interactive data.

### Driveline Baseball (drivelinebaseball.com)
**What they do:** Player development company bridging biomechanics data with training. "Training, gear, and software for player development."
**Data angle:** Capture biomechanics data through pitching/hitting analysis tools. Frame analytics within actionable development contexts rather than standalone analysis.
**Visual style:** Bold, modern. Black backgrounds, orange accent (#FFA300). Gotham/Montserrat fonts. Action-oriented.
**Niche:** Analytics for player development, not fan consumption. But their data outputs (pitch design, movement profiles) influence how fans think about pitching.

### Other Notable Sites
- **Prospects Live:** Prospect rankings blending data and scouting. Subscription model. Mock draft simulator, playing time projections. Fantrax integration. Clean modular design with color-coded categories.
- **Baseball Trade Values:** Quantified trade valuations for MLB transactions. Side-by-side deal comparisons. 88% acceptance rate on evaluated trades. Fills a real gap in trade analysis.
- **Smart Fantasy Baseball:** Teaching-focused. Automated SGP ranking tool, projection aggregator, Player ID Map. Emphasizes process over fish.
- **RotoWire:** Full-service fantasy platform. DFS optimizers, lineup tools, weather, injuries. One-stop-shop approach.
- **SABR (sabr.org):** The Society for American Baseball Research. Community hub, not a data platform. Analytics Conference, regional chapters, research committees, Baseball Research Journal. Analytics Certification program.
- **Saber Seminar:** Nonprofit weekend event bringing together coaches, statisticians, scouts, doctors, scientists. Knowledge-sharing and networking. Next event Aug 2026 in Chicago.

---

## TWITTER/SOCIAL ANALYTICS CREATORS

### @UmpScorecards - THE GOLD STANDARD
**What they do:** Grade every MLB umpire's performance after every game. Post a visual scorecard showing accuracy, consistency, missed calls, and which team was favored.
**Creator:** Ethan Singer (BU - statistics, CS, public policy; NYT Upshot fellow). Co-owner Ethan Schwartz (UPenn mechanical engineering).
**History:** Started manually Oct 2019 with Python scripts. Automated Twitter bot by Aug 2020. Grew from 19K followers after Sep 2020 Giants-Padres game to 300K+ by 2022. Now has a proprietary API and ML models.
**Visual format:** Standardized scorecard graphic posted after every game. Clean, consistent, immediately readable. Shows overall accuracy %, consistency %, missed calls plotted on strike zone, favor metric.
**Why it works:** (1) Consistent format people learn to read instantly, (2) posts after EVERY game so it becomes a habit, (3) taps into universal frustration with umpires, (4) clean enough that sports media embeds them constantly, (5) transparent methodology.
**Revenue:** Patreon tiers for exclusive content.
**Media coverage:** NYT, NBC Sports, USA Today, ESPN. Mainstream legitimacy.
**Key lesson for @sabrmagician:** One consistent, automated visual format posted reliably = brand building machine.

### @would_it_dong
**What they do:** Automated bot that checks every home run and shows which other MLB parks it would (or wouldn't) have been a home run in. Posts a graphic showing the batted ball overlaid on all 30 park outlines.
**Why it goes viral:** (1) Answers an immediate question fans have ("was that a cheapie?"), (2) visual is simple and shareable, (3) posts in near-real-time during games, (4) taps into park factor debates that fans love arguing about.
**Visual style:** Simple park overlay graphic. Not fancy but immediately clear.
**Audience:** Large. One of the most-shared baseball bot accounts. Regularly cited by broadcasters and media.
**Key lesson:** Simple concept + immediate relevance + automated consistency = viral content.

### @DarenWillman
**What they do:** Creator of Baseball Savant. Now VP of Technology at MLB Advanced Media. Shares Statcast innovations, new tools, behind-the-scenes data features.
**Influence:** Extremely high within the analytics community. When he tweets a new Savant feature, the whole community pays attention.
**Style:** Technical, insider. Sharing tools and data rather than hot takes.

### @PitcherList
**What they do:** Social extension of pitcherlist.com. Share rankings, analysis, GIFs of nasty pitches.
**Visual brand:** Very consistent. Their tier ranking graphics are immediately identifiable. The "Nastiest Pitching+" content with GIF breakdowns drives high engagement.
**Key lesson:** Visual consistency across every post builds brand recognition fast.

### @CodifyBaseball
**What they do:** Pitch design and player development analytics. Pitcher registration/evaluation services. Focus on pitch movement, spin, and design.
**Visual style:** Dark, professional (black/charcoal backgrounds). More of a services company than a content brand.
**Niche:** The intersection of analytics and player development. Less fan-facing, more industry-facing.
**Social:** Active on both Twitter and Instagram (@getintotheblue).

### @EvolvingWild (Hockey - Cross-Sport Inspiration)
**What they do:** Hockey analytics platform run by twins (Josh and Luke Younggren). Known for clear, accessible data visualizations of complex hockey metrics.
**Why they matter for inspiration:** (1) They made hockey analytics visual and accessible when the space was dominated by spreadsheets, (2) their game score cards and player comparison tools are clean and shareable, (3) they built a brand by being consistent and accessible without dumbing things down.
**Key lesson:** You can build a real analytics brand in a niche sport by being the person who makes data visual and accessible.

### Other Notable Accounts
- **@DSzymborski:** Dan Szymborski, creator of ZiPS projections at FanGraphs. Prolific tweeter, sharp analysis, good engagement.
- **@mike_petriello:** MLB.com's Statcast expert. Explains Statcast data accessibly. Has mainstream reach through MLB platform.
- **@ManGamesLost:** Injury tracking data. Automated, consistent format.
- **@SlangsOnSports:** Baseball data visualizations, prospect analysis.
- **@TJStats:** Baseball data viz and statistical analysis.
- **@SteveThePirate6:** Independent baseball data viz creator.
- **@Chandler_Rome, @Travis_Sawchik, @EnoSarris:** Analytics-forward beat writers/columnists whose Twitter presence drives their brand.
- **@baseikiball:** Japanese baseball analytics content in English - underserved niche.
- **@DingerTracker:** Similar automated concept to Would It Dong, tracking home run distances.

---

## TOOLS & APPS

### Baseball Savant Tools
- **Statcast Search:** Most powerful public baseball query tool. Filter by pitch type, velocity, count, situation, handedness, date range, venue. Data from 2008+. CSV export.
- **Leaderboards:** Exit velocity, launch angle, barrel rate, sprint speed, OAA, catcher framing, arm strength, bat tracking, spin rate, active spin.
- **3D Pitch Visualization:** Interactive pitch movement plots in 3D space.
- **ABS Challenge Dashboard:** Challenge rates, overturn rates, situational breakdowns by inning/count/runners. Player leaderboards.
- **Bat Tracking:** New addition. Bat speed, swing length metrics.
- **Pitch movement comparisons, percentile rankings, player comparison tool.**

### FanGraphs Tools
- **Projection Systems:** ZiPS, Steamer, THE BAT/X, ATC, Depth Charts, OOPSY. Rest-of-season and multi-year variants.
- **Auction Calculator:** Customizable by league size, scoring, keepers, positions. Integrates all projection systems.
- **Leaderboards:** Batting, pitching, fielding. Splits, pitch-type, minor league, international, college.
- **Roster Resource:** Depth charts, injuries, transactions, payroll by team.
- **WAR Graphs, WPA Inquirer, Park Factors, Season Stat Grids.**
- **Ottoneu:** Full fantasy platform owned by FanGraphs.

### Other Tools
- **Brooks Baseball PITCHf/x Tool:** Historical pitch classification and movement data.
- **Stathead (Baseball Reference):** Custom queries against the full historical database. Subscription.
- **Baseball Trade Values:** Trade simulator with quantified player values.
- **Smart Fantasy Baseball tools:** SGP ranking automation, projection aggregator, Player ID Map (cross-platform player matching - this is a real pain point).
- **RotoWire:** DFS optimizers, lineup tools, projected lineups.

### Streamlit/Web Apps in the Space
This is notably thin. Most baseball analytics apps are either:
1. Built by MLB/FanGraphs/BR as part of their platforms
2. One-off hobby projects that don't persist
3. R Shiny apps in academic settings

There's no dominant independent baseball analytics web app ecosystem. This is a gap.

---

## KEY GAPS & OPPORTUNITIES FOR @SABRMAGICIAN

### 1. ABS Challenge Content (Your Current Lane - PROTECT IT)
Baseball Savant has basic ABS data now (rates and leaderboards), but nobody is doing what UmpScorecards did for umpire accuracy but for ABS challenges. No one is posting daily visual scorecards of ABS challenge outcomes. The ABS system is brand new and the content space is wide open. This is your best first-mover opportunity.

**Gap:** No automated, visually consistent, daily ABS challenge content on social media.
**Opportunity:** Be the @UmpScorecards of ABS challenges before someone else does it.

### 2. Ottoneu-Specific Analytics
Ottoneu is a FanGraphs property with a dedicated, high-engagement user base of serious fantasy players. Yet there are almost no third-party Ottoneu analytics tools or content.

**Gap:** No public Ottoneu value finders, salary analysis tools, or league comparison dashboards.
**Opportunity:** MoLab notebooks (Value Finder, Database Explorer) serve this niche directly.

### 3. Interactive Data Viz That's Shareable
FanGraphs' visuals are functional but ugly. Baseball Savant's are locked inside their platform. Pitcher List has the right idea with consistent visual branding but stays narrow.

**Gap:** Nobody is the "go-to" for beautiful, shareable baseball data visualizations that explain complex topics.
**Opportunity:** Plotly + marimo + clean design templates = your differentiator. Think Edward Tufte meets baseball.

### 4. Cross-Platform Data Integration
The Player ID Map from Smart Fantasy Baseball exists because matching players across FanGraphs, Savant, Baseball Reference, and Ottoneu is a real pain point.

**Gap:** No single dashboard that pulls together Statcast + FanGraphs + Ottoneu data.
**Opportunity:** DuckDB + MotherDuck already solves this for you. Your MoLab notebooks can be the integration layer.

### 5. Accessible Explanations of New Metrics
Baseball Savant adds features (bat tracking, ABS data) without much explanation. FanGraphs' glossary is comprehensive but dry.

**Gap:** Visual explainers for new Statcast metrics and rule changes.
**Opportunity:** Short, visual "here's what this means" content that bridges the gap between data dumps and understanding.

### 6. Weather + Ballpark Analytics
Open-Meteo API + ballpark orientation data = wind impact on fly balls. Nobody does this consistently with good visuals.

**Gap:** No reliable, visual, daily weather-impact analysis for baseball.
**Opportunity:** Already on your TODO list. Could be a standalone bot account.

### 7. SABR Points Format Expertise
You play in 9 Ottoneu leagues, all SABR Points. Nobody is producing dedicated SABR Points content.

**Gap:** SABR Points scoring is niche but the players who use it are extremely engaged.
**Opportunity:** Become THE voice for SABR Points strategy, valuations, and analysis.

---

## COMPETITIVE POSITIONING SUMMARY

| Competitor | Strength | Weakness | Your Angle |
|---|---|---|---|
| Baseball Savant | Deepest data | No narrative, no community | Add context and visuals to their data |
| FanGraphs | Tools + editorial + community | Ugly visuals, overwhelming | Beautiful, focused data viz |
| UmpScorecards | Perfect execution of one concept | Only umpires | Apply their model to ABS challenges |
| Would It Dong | Viral simplicity | One-trick | Multiple automated visual concepts |
| Pitcher List | Visual brand consistency | Narrow (pitching/fantasy) | Broader analytics + Ottoneu |
| Baseball Prospectus | Prestige writing | Paywalled, small reach | Free, visual, accessible |
| Baseball Reference | Complete historical data | Zero analysis or personality | Personality + visual storytelling |

### @sabrmagician's Sweet Spot
The market has plenty of data (Savant), plenty of tools (FanGraphs), and plenty of writing (BP, Athletic). What's missing is a **visual-first, personality-driven analytics brand** that:
1. Automates consistent daily content (ABS scorecards, weather, etc.)
2. Makes complex data beautiful and shareable
3. Serves the Ottoneu/serious fantasy niche specifically
4. Bridges multiple data sources into unified views
5. Actually ships interactive tools people can use (MoLab)

The closest model to emulate is UmpScorecards: find ONE thing, do it better than anyone visually, automate it, be consistent, and let the brand grow from there. ABS challenges are that thing right now.

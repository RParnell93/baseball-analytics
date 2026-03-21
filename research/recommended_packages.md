# Recommended Python Packages

*Research compiled March 2026. Prioritized by impact for @sabrmagician.*

## High Priority - Install Now

| Package | Install | Purpose |
|---------|---------|---------|
| sportypy | `pip install sportypy` | Accurate MLB field rendering for spray charts |
| adjustText | `pip install adjustText` | Auto-fix overlapping scatter plot labels |
| plottable | `pip install plottable` | Publication-quality stat tables as PNG images |
| openmeteo-requests | `pip install openmeteo-requests` | Free weather API (no key needed) for ballpark bot |
| Pillow | `pip install Pillow` | Image composition for Twitter cards (charts + logos + borders) |
| schedule | `pip install schedule` | Lightweight job scheduling for daily posting pipeline |

## Medium Priority - Explore When Needed

| Package | Install | Purpose |
|---------|---------|---------|
| highlight-text | `pip install highlight-text` | Multi-colored text annotations in matplotlib |
| pandera | `pip install pandera` | DataFrame validation for data quality checks |
| twikit | `pip install twikit` | Free Twitter posting WITHOUT API key (unofficial) |
| meteostat | `pip install meteostat` | Historical weather data for park factor research |
| APScheduler | `pip install APScheduler` | Cron-style scheduling if `schedule` is too simple |

## Reference Repos to Study

| Repo | Stars | Why |
|------|-------|-----|
| blue-shoes/ottoneu-toolbox | 7 | Ottoneu valuation patterns, projection integration |
| timothyf/baseball-data-lab | 14 | Player stat card image generation for social |
| arios37/statcast-bayesian-pitch-model | new | Bayesian pitch modeling with PyMC |
| etweisberg/mlb-mcp | 18 | MCP server for baseball data (Claude integration) |
| drivelineresearch/openbiomechanics | 288 | Elite biomechanics data |

## Already Using (pybaseball hidden features)

pybaseball has visualization tools you may not be using:
- `pybaseball.plotting.spraychart()` - overlays hit data on stadium backgrounds
- `pybaseball.plotting.plot_strike_zone()` - strike zone rendering
- `pybaseball.plotting.plot_stadium()` - stadium rendering

## Skip

- dagster/prefect/great-expectations (overkill for personal project)
- sportsipy, baseball-scraper (redundant/dead)
- mplsoccer (soccer only)

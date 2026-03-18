# Baseball Analytics

Personal baseball analytics platform for Ottoneu fantasy baseball, data visualization, and original analysis.

## What's Here

- **Database**: DuckDB with 800K+ rows of Statcast, FanGraphs, and Ottoneu data
- **Visualizations**: Pitch movement plots, strike zone heatmaps, exit velo charts
- **Ottoneu Tools**: FGPts and SABR scoring calculators, player valuations
- **Notebooks**: marimo notebooks for data exploration
- **Data Pipeline**: Automated collection from Statcast, FanGraphs, and Ottoneu

## Quick Start

```bash
pip install -r requirements.txt
python src/data_collection/refresh_all.py
marimo edit notebooks/01_explore_database.py
```

## Data Sources

- [Baseball Savant / Statcast](https://baseballsavant.mlb.com) via pybaseball
- [FanGraphs](https://fangraphs.com) via pybaseball
- [Ottoneu](https://ottoneu.fangraphs.com) average values CSV export
- [Chadwick Bureau](https://github.com/chadwickbureau) player ID crosswalk

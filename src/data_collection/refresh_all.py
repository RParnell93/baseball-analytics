"""Master data refresh script. Run this to update all data sources.

Usage:
    python src/data_collection/refresh_all.py          # Full refresh
    python src/data_collection/refresh_all.py --recent  # Last 7 days of Statcast only
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def refresh_statcast(recent_only=False):
    """Pull Statcast data."""
    from src.data_collection.statcast import pull_statcast_season, load_to_duckdb
    import pandas as pd

    if recent_only:
        from pybaseball import statcast, cache
        cache.enable()
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        print(f"Pulling recent Statcast data ({start} to {end})...")
        df = statcast(start_dt=start, end_dt=end)
        if len(df) > 0:
            print(f"  Got {len(df):,} pitches")
            load_to_duckdb(df, "statcast_pitches")
        else:
            print("  No new data (offseason?)")
    else:
        year = datetime.now().year
        df = pull_statcast_season(year)
        df.to_csv(f"data/raw/statcast_{year}.csv", index=False)
        load_to_duckdb(df, "statcast_pitches")


def refresh_fangraphs():
    """Pull FanGraphs batting and pitching stats."""
    from src.data_collection.fangraphs import pull_batting, pull_pitching, load_to_duckdb

    year = datetime.now().year
    print(f"Refreshing FanGraphs stats for {year}...")
    batting = pull_batting(year, year)
    pitching = pull_pitching(year, year)

    batting.to_csv(f"data/raw/fg_batting_{year}.csv", index=False)
    pitching.to_csv(f"data/raw/fg_pitching_{year}.csv", index=False)

    load_to_duckdb(batting, "fg_batting_current")
    load_to_duckdb(pitching, "fg_pitching_current")


def refresh_ottoneu():
    """Pull Ottoneu average values."""
    from src.data_collection.ottoneu import pull_ottoneu_values, load_to_duckdb

    for fmt in ["fgpts", "sabr"]:
        df = pull_ottoneu_values(fmt)
        load_to_duckdb(df, f"ottoneu_{fmt}_values")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh baseball data")
    parser.add_argument("--recent", action="store_true", help="Only pull last 7 days of Statcast")
    parser.add_argument("--skip-statcast", action="store_true", help="Skip Statcast (slow)")
    parser.add_argument("--skip-fangraphs", action="store_true", help="Skip FanGraphs")
    parser.add_argument("--skip-ottoneu", action="store_true", help="Skip Ottoneu")
    args = parser.parse_args()

    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    os.makedirs("data/database", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)

    if not args.skip_statcast:
        refresh_statcast(recent_only=args.recent)

    if not args.skip_fangraphs:
        refresh_fangraphs()

    if not args.skip_ottoneu:
        refresh_ottoneu()

    print("\nAll data refreshed!")

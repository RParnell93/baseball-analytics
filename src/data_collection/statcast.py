"""Pull Statcast pitch-level data from Baseball Savant via pybaseball."""

import duckdb
import pandas as pd
from pybaseball import statcast, cache

# Enable caching so re-runs don't re-download
cache.enable()

DB_PATH = "data/database/baseball.duckdb"


def pull_statcast_season(year: int) -> pd.DataFrame:
    """Pull a full season of Statcast data."""
    print(f"Pulling Statcast data for {year}...")
    start = f"{year}-03-20"
    end = f"{year}-11-05"
    df = statcast(start_dt=start, end_dt=end)
    print(f"  Got {len(df):,} pitches")
    return df


def load_to_duckdb(df: pd.DataFrame, table_name: str):
    """Load a DataFrame into DuckDB, replacing existing data for that table."""
    con = duckdb.connect(DB_PATH)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df WHERE 1=0")
    con.execute(f"INSERT INTO {table_name} SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  {table_name} now has {row_count:,} rows in DuckDB")
    con.close()


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Pull 2024 season
    df_2024 = pull_statcast_season(2024)

    # Save raw CSV as backup
    raw_path = f"data/raw/statcast_2024.csv"
    df_2024.to_csv(raw_path, index=False)
    print(f"  Saved raw CSV to {raw_path}")

    # Load to DuckDB
    load_to_duckdb(df_2024, "statcast_pitches")
    print("Done!")

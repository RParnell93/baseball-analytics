"""Pull batting and pitching leaderboards from FanGraphs via pybaseball."""

import time
import duckdb
import pandas as pd
from pybaseball import batting_stats, pitching_stats, cache

cache.enable()

DB_PATH = "data/database/baseball.duckdb"


def pull_batting(start_year: int, end_year: int) -> pd.DataFrame:
    """Pull FanGraphs batting leaderboard, one year at a time to avoid timeouts."""
    frames = []
    for year in range(start_year, end_year + 1):
        print(f"  Batting {year}...", end=" ")
        try:
            df = batting_stats(year, year, qual=0)
            df["Season"] = year
            frames.append(df)
            print(f"{len(df)} players")
        except Exception as e:
            print(f"FAILED: {e}")
        time.sleep(2)
    result = pd.concat(frames, ignore_index=True)
    print(f"  Total: {len(result):,} player-seasons")
    return result


def pull_pitching(start_year: int, end_year: int) -> pd.DataFrame:
    """Pull FanGraphs pitching leaderboard, one year at a time."""
    frames = []
    for year in range(start_year, end_year + 1):
        print(f"  Pitching {year}...", end=" ")
        try:
            df = pitching_stats(year, year, qual=0)
            df["Season"] = year
            frames.append(df)
            print(f"{len(df)} players")
        except Exception as e:
            print(f"FAILED: {e}")
        time.sleep(2)
    result = pd.concat(frames, ignore_index=True)
    print(f"  Total: {len(result):,} player-seasons")
    return result


def load_to_duckdb(df: pd.DataFrame, table_name: str):
    """Load a DataFrame into DuckDB."""
    con = duckdb.connect(DB_PATH)
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"  {table_name}: {row_count:,} rows in DuckDB")
    con.close()


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    print("Pulling FanGraphs batting stats 2015-2025...")
    batting_df = pull_batting(2015, 2025)

    print("Pulling FanGraphs pitching stats 2015-2025...")
    pitching_df = pull_pitching(2015, 2025)

    # Save raw CSVs
    batting_df.to_csv("data/raw/fg_batting_2015_2025.csv", index=False)
    pitching_df.to_csv("data/raw/fg_pitching_2015_2025.csv", index=False)
    print("Saved raw CSVs")

    # Load to DuckDB
    load_to_duckdb(batting_df, "fg_batting")
    load_to_duckdb(pitching_df, "fg_pitching")
    print("Done!")

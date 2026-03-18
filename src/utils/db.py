"""Database utilities for querying the baseball DuckDB."""

import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = str(Path(__file__).parent.parent.parent / "data" / "database" / "baseball.duckdb")


def query(sql: str) -> pd.DataFrame:
    """Run a SQL query against the baseball database and return a DataFrame."""
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute(sql).fetchdf()
    con.close()
    return result


def get_player_mlbam_id(name_first: str, name_last: str) -> int:
    """Look up a player's MLBAM ID from the player_ids table."""
    df = query(f"""
        SELECT key_mlbam FROM player_ids
        WHERE name_first = '{name_first}' AND name_last = '{name_last}'
        AND key_mlbam IS NOT NULL
        ORDER BY mlb_played_last DESC NULLS LAST
        LIMIT 1
    """)
    if len(df) == 0:
        raise ValueError(f"Player not found: {name_first} {name_last}")
    return int(df.iloc[0]["key_mlbam"])


def get_player_fg_id(name_first: str, name_last: str) -> int:
    """Look up a player's FanGraphs ID from the player_ids table."""
    df = query(f"""
        SELECT key_fangraphs FROM player_ids
        WHERE name_first = '{name_first}' AND name_last = '{name_last}'
        AND key_fangraphs IS NOT NULL
        ORDER BY mlb_played_last DESC NULLS LAST
        LIMIT 1
    """)
    if len(df) == 0:
        raise ValueError(f"Player not found: {name_first} {name_last}")
    return int(df.iloc[0]["key_fangraphs"])


def batter_statcast(name_first: str, name_last: str, year: int = 2024) -> pd.DataFrame:
    """Get all Statcast pitches faced by a batter in a season."""
    mlbam_id = get_player_mlbam_id(name_first, name_last)
    return query(f"""
        SELECT * FROM statcast_pitches
        WHERE batter = {mlbam_id}
        AND game_date >= '{year}-01-01'
        AND game_date <= '{year}-12-31'
        ORDER BY game_date, at_bat_number, pitch_number
    """)


def pitcher_statcast(name_first: str, name_last: str, year: int = 2024) -> pd.DataFrame:
    """Get all Statcast pitches thrown by a pitcher in a season."""
    mlbam_id = get_player_mlbam_id(name_first, name_last)
    return query(f"""
        SELECT * FROM statcast_pitches
        WHERE pitcher = {mlbam_id}
        AND game_date >= '{year}-01-01'
        AND game_date <= '{year}-12-31'
        ORDER BY game_date, at_bat_number, pitch_number
    """)


def fg_batting_season(name: str = None, season: int = None, min_pa: int = 0) -> pd.DataFrame:
    """Get FanGraphs batting stats, optionally filtered."""
    where = ["1=1"]
    if name:
        where.append(f"Name LIKE '%{name}%'")
    if season:
        where.append(f"Season = {season}")
    if min_pa > 0:
        where.append(f"PA >= {min_pa}")
    return query(f"SELECT * FROM fg_batting WHERE {' AND '.join(where)} ORDER BY PA DESC")


def fg_pitching_season(name: str = None, season: int = None, min_ip: float = 0) -> pd.DataFrame:
    """Get FanGraphs pitching stats, optionally filtered."""
    where = ["1=1"]
    if name:
        where.append(f"Name LIKE '%{name}%'")
    if season:
        where.append(f"Season = {season}")
    if min_ip > 0:
        where.append(f"IP >= {min_ip}")
    return query(f"SELECT * FROM fg_pitching WHERE {' AND '.join(where)} ORDER BY IP DESC")
